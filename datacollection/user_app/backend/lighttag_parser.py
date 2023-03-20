import itertools
import os
import json
import random

import networkx as nx
import matplotlib.pyplot as plt
import yaml

from datacollection.user_app.backend.models.mistake import Mistake
from datacollection.user_app.backend.models.mistake_tag import MistakeTag
from datacollection.user_app.backend.models.step import Step
from logger_config import logger
from datacollection.user_app.backend.constants import LightTag_Constants as const


def create_directories(dir_path):
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)


def create_tag_mappings(activity_json):
	tag_to_tag_id = {}
	tag_id_to_tag = {}
	for tag_node in activity_json[const.SCHEMA][const.TAGS]:
		tag_to_tag_id[tag_node[const.NAME]] = tag_node[const.ID]
		tag_id_to_tag[tag_node[const.ID]] = tag_node[const.NAME]
	return tag_to_tag_id, tag_id_to_tag


def create_annotation_mappings(activity_json):
	tagged_token_id_to_tag_id = {}
	tag_id_to_tagged_token_id = {}
	tagged_token_id_to_value = {}
	for annotation_node in activity_json[const.EXAMPLES][0][const.ANNOTATIONS]:
		tagged_token_id_to_tag_id[annotation_node[const.TAGGED_TOKEN_ID]] = annotation_node[const.TAG_ID]
		tag_id_to_tagged_token_id[annotation_node[const.TAG_ID]] = annotation_node[const.TAGGED_TOKEN_ID]
		tagged_token_id_to_value[annotation_node[const.TAGGED_TOKEN_ID]] = annotation_node[const.VALUE]
	return tagged_token_id_to_tag_id, tag_id_to_tagged_token_id, tagged_token_id_to_value


def create_relation_mappings(activity_json, tag_id_to_tag, tagged_token_id_to_tag_id, tagged_token_id_to_value):
	relation_id_to_tagged_token = {}
	relation_id_to_tag = {}
	relation_id_to_children = {}
	relation_id_to_tagged_token_id = {}
	for relation_node in activity_json[const.RELATIONS]:
		relation_id_to_tagged_token[relation_node[const.ID]] = tagged_token_id_to_value[
			relation_node[const.TAGGED_TOKEN_ID]]
		relation_id_to_tag[relation_node[const.ID]] = tag_id_to_tag[
			tagged_token_id_to_tag_id[relation_node[const.TAGGED_TOKEN_ID]]]
		relation_id_to_children[relation_node[const.ID]] = relation_node[const.CHILDREN]
		relation_id_to_tagged_token_id[relation_node[const.ID]] = relation_node[const.TAGGED_TOKEN_ID]
	return relation_id_to_tagged_token, relation_id_to_tag, relation_id_to_children, relation_id_to_tagged_token_id


def find_topological_orderings(dependency_graph):
	orderings = []
	
	def topological_sort(graph, visited, stack):
		if not graph:
			orderings.append(stack)
			return
		
		# Only include a sample of 3 from terminal nodes
		terminal_nodes = [node for node in graph if graph.in_degree()[node] == 0]
		random.shuffle(terminal_nodes)
		sampled_nodes = random.sample(terminal_nodes, min(3, len(terminal_nodes)))
		for node in sampled_nodes:
			if node not in visited:
				new_visited = visited | {node}
				new_graph = graph.subgraph([n for n in graph if n not in new_visited])
				topological_sort(new_graph, new_visited, stack + [node])
	
	topological_sort(dependency_graph, set(), [])
	return orderings


def interleave_sequences(sequences):
	interleaved = []
	for seq in itertools.zip_longest(*sequences, fillvalue=None):
		for item in seq:
			if item is not None:
				interleaved.append(item)
	return interleaved


def fetch_activity_programs(topological_orderings, num_programs):
	num_topological_orders = len(topological_orderings)
	if num_topological_orders > num_programs:
		activity_programs = random.sample(topological_orderings, num_programs)
	else:
		activity_programs = topological_orderings.copy()
		for idx in range(num_programs - num_topological_orders):
			activity_programs.append(random.choice(topological_orderings))
	return activity_programs


class LightTagParser:
	
	def __init__(self, data_directory):
		self.data_directory = data_directory
		self.activity_data_directory = os.path.join(self.data_directory, "lighttag")
		self.recording_data_directory = os.path.join(self.data_directory, "recordings")
		self.dependency_graph_data_directory = os.path.join(self.data_directory, "graphs")
		
		create_directories(self.activity_data_directory)
		create_directories(self.recording_data_directory)
		create_directories(self.dependency_graph_data_directory)
	
	def generate_dependency_graph(self, activity_file_name):
		logger.info("--------------------------------------------------------------------------- \n")
		activity_path = os.path.join(self.activity_data_directory, activity_file_name)
		with open(activity_path) as activity_file:
			activity_json = json.load(activity_file)
		
		# 1. Generate Map and Inverse Map of Tags and Tag ID from schema
		tag_to_tag_id, tag_id_to_tag = create_tag_mappings(activity_json)
		
		# 2. Generate Map and Inverse Map of Tagged Token ID and Tag ID
		tagged_token_id_to_tag_id, tag_id_to_tagged_token_id, tagged_token_id_to_value = create_annotation_mappings(
			activity_json)
		
		# 3. Generate a Map of Relation ID and value
		relation_id_to_tagged_token, relation_id_to_tag, relation_id_to_children, relation_id_to_tagged_token_id = create_relation_mappings(
			activity_json, tag_id_to_tag, tagged_token_id_to_tag_id, tagged_token_id_to_value)
		
		# 4. Start generating a graph based on Nodes
		# Node ID - [Tag: Step Value] - Network X
		# Children - [List Nodes]
		# Have a map of {Node ID: Node}
		graph = nx.DiGraph()
		
		relation_id_to_node_id = {}
		node_id_to_node_attributes = {}
		node_id_to_tagged_token_id = {}
		# 5. Add all nodes to the graph with Node ID as attribute
		for relation_node in activity_json[const.RELATIONS]:
			
			# Terminal Node in LightTag graph, no need to create a node for it - [Step Node] in LightTag
			if len(relation_node[const.CHILDREN]) < 1:
				continue
			
			step_info = None
			node_attributes = {}
			tagged_token = relation_id_to_tagged_token[relation_node[const.ID]]
			for child_id in relation_node[const.CHILDREN]:
				child_tag = relation_id_to_tag[child_id]
				if child_tag == const.STEP:
					# Assigns node-id as : node_id-put-"put onion into box"
					step_info = relation_id_to_tagged_token[child_id]
					break
			
			node_attributes[const.ACTION] = tagged_token
			node_attributes[const.STEP] = step_info
			node_label = f'{tagged_token}-{step_info}'
			
			node_id = f'{relation_node[const.TAGGED_TOKEN_ID]}:{tagged_token}:{step_info}'
			
			relation_id_to_node_id[relation_node[const.ID]] = node_id
			node_id_to_node_attributes[node_id] = node_attributes
			node_id_to_tagged_token_id[node_id] = relation_node[const.TAGGED_TOKEN_ID]
			
			graph.add_node(node_id, label=node_label, **node_attributes)
		
		for relation_node in activity_json[const.RELATIONS]:
			
			if len(relation_node[const.CHILDREN]) < 1:
				continue
			
			parent_node_id = relation_id_to_node_id[relation_node[const.ID]]
			for child_id in relation_node[const.CHILDREN]:
				
				if relation_id_to_tag[child_id] == const.STEP:
					continue
				
				try:
					child_node_id = relation_id_to_node_id[child_id]
				except KeyError:
					# tagged_token = relation_id_to_tagged_token[child_id]
					# child_node_id = f'{child_id}-{tagged_token}'
					# child_node_label = tagged_token
					# relation_id_to_node_id[child_id] = child_node_id
					#
					# graph.add_node(child_node_id, label=child_node_label)
					logger.error(f"Exception occurred in adding the edge from {child_id} to {parent_node_id}")
					# continue
					child_tagged_token_id = relation_id_to_tagged_token_id[child_id]
					child_node_id = [node_id for node_id, tagged_token_id in node_id_to_tagged_token_id.items() if
					                 tagged_token_id == child_tagged_token_id][0]
					
					logger.info(f"Adding the edge from {child_node_id} to {parent_node_id}")
				
				graph.add_edge(child_node_id, parent_node_id)
		
		plt.figure(figsize=(50, 50), dpi=150)
		
		labels = nx.get_node_attributes(graph, const.LABEL)
		nx.draw_planar(
			graph,
			arrowsize=12,
			with_labels=True,
			node_size=8000,
			node_color="#ffff8f",
			linewidths=2.0,
			width=1.5,
			font_size=14,
			labels=labels
		)
		
		dependency_graph_path = os.path.join(self.dependency_graph_data_directory, f'{activity_file_name[:-5]}.png')
		plt.savefig(dependency_graph_path)
		plt.clf()
		
		# print(graph.nodes)
		logger.info(f"Finished processing {activity_file_name}")
		# print(graph.edges)
		logger.info("--------------------------------------------------------------------------- \n")
		
		# 6. Return graph
		return graph
	
	# def generate_activity_recording_data(self, activity_file_name):
	# 	# 1. Build dependency graph for the activity
	# 	dependency_graph = self.generate_dependency_graph(activity_file_name)
	# 	# 2. Use the graph for generating topological orderings
	# 	topological_orderings = find_topological_orderings(dependency_graph)
	#
	# 	valid_programs = fetch_activity_programs(topological_orderings, const.NUM_VALID_PROGRAMS)
	#
	# 	# 3. Use the graph for generating invalid programs
	# 	invalid_programs = fetch_activity_programs(topological_orderings, const.NUM_INVALID_PROGRAMS)
	#
	# 	# 4. Write to a file in with the name of an activity
	# 	program_dict_list = []
	#
	# 	valid_program_counter = 1
	# 	for valid_program in valid_programs:
	# 		valid_program_dict = {const.RECORDING_ID: valid_program_counter}
	# 		step_dict_list = []
	# 		for valid_program_step in valid_program:
	# 			step_description = valid_program_step.split(":")[-1]
	# 			step_dict = Step(step_description).to_dict()
	# 			step_dict_list.append(step_dict)
	# 		valid_program_dict[const.STEPS] = step_dict_list
	# 		program_dict_list.append(valid_program_dict)
	# 		valid_program_counter += 1
	#
	# 	# In invalid programs 10 will have missing steps
	# 	# The rest will have invalid orders
	# 	invalid_program_counter = 1
	# 	for invalid_program in invalid_programs:
	# 		invalid_program_dict = {const.RECORDING_ID: invalid_program_counter}
	# 		step_dict_list = []
	# 		missed_steps = []
	#
	# 		# Randomly shuffle 20% of the steps in the recipe
	# 		if invalid_program_counter > 10:
	# 			num_to_shuffle = int(len(invalid_program) * 2 // 10)
	# 			indices_to_shuffle = random.sample(range(len(invalid_program)), num_to_shuffle)
	#
	# 			for index_to_shuffle in indices_to_shuffle:
	# 				random_index = random.randint(0, len(invalid_program) - 1)
	# 				invalid_program[index_to_shuffle], invalid_program[random_index] = invalid_program[random_index], \
	# 				                                                                   invalid_program[index_to_shuffle]
	#
	# 		for invalid_program_step in invalid_program:
	# 			# Skips 10% of the steps in the program
	# 			step_description = invalid_program_step.split(":")[-1]
	# 			if invalid_program_counter < 10 and random.random() < 0.1:
	# 				missed_steps.append(step_description)
	# 				continue
	# 			step_dict = Step(step_description).to_dict()
	# 			step_dict_list.append(step_dict)
	# 		invalid_program_dict[const.STEPS] = step_dict_list
	#
	# 		if len(missed_steps) > 0:
	# 			mistake_dict_list = []
	# 			for missed_step_description in missed_steps:
	# 				mistake_dict = Mistake(MistakeTag.MISSING_STEP, missed_step_description).to_dict()
	# 				mistake_dict_list.append(mistake_dict)
	# 			invalid_program_dict[const.MISTAKES] = mistake_dict_list
	#
	# 		program_dict_list.append(invalid_program_dict)
	# 		invalid_program_counter += 1
	#
	# 	activity_recording_file_path = os.path.join(self.recording_data_directory, activity_file_name[:-5])
	# 	with open(activity_recording_file_path, 'w') as activity_recording_file:
	# 		yaml.dump(program_dict_list, activity_recording_file)
	#
	def generate_activity_recording_data(self, activity_file_name):
		dependency_graph = self.generate_dependency_graph(activity_file_name)
		topological_orderings = find_topological_orderings(dependency_graph)
		
		valid_programs = fetch_activity_programs(topological_orderings, const.NUM_VALID_PROGRAMS)
		invalid_programs = fetch_activity_programs(topological_orderings, const.NUM_INVALID_PROGRAMS)
		
		program_dict_list = self._generate_program_dicts(valid_programs, invalid_programs)
		
		activity_recording_file_path = os.path.join(self.recording_data_directory, activity_file_name[:-5])
		with open(activity_recording_file_path, 'w') as activity_recording_file:
			yaml.dump(program_dict_list, activity_recording_file)
	
	def _generate_program_dicts(self, valid_programs, invalid_programs):
		program_dicts = []
		
		for i, program in enumerate(valid_programs):
			program_dict = self._generate_program_dict(program, i + 1, is_valid=True)
			program_dicts.append(program_dict)
		
		for i, program in enumerate(invalid_programs):
			program_dict = self._generate_program_dict(program, i + 1 + const.NUM_VALID_PROGRAMS, is_valid=False)
			program_dicts.append(program_dict)
		
		return program_dicts
	
	def _generate_program_dict(self, program, program_counter, is_valid):
		program_dict = {const.RECORDING_ID: program_counter}
		step_dicts = [self._step_dict_from_program_step(step) for step in program]
		
		if not is_valid:
			step_dicts, mistake_dicts = self._add_mistakes(step_dicts, program_counter, const.NUM_VALID_PROGRAMS)
		
		program_dict[const.STEPS] = step_dicts
		
		if not is_valid and len(mistake_dicts) > 0:
			program_dict[const.MISTAKES] = mistake_dicts
		
		return program_dict
	
	def _step_dict_from_program_step(self, program_step):
		step_description = program_step.split(":")[-1]
		return Step(step_description).to_dict()
	
	def _add_mistakes(self, step_dicts, program_counter, base_counter):
		# Order mistakes for all the invalid programs > 10
		# Missing step for all the invalid programs < 30
		if program_counter > const.THRESHOLD_NUM_MISSING_STEPS + base_counter:
			step_dicts = self._shuffle_steps(step_dicts)
		
		mistake_dicts = []
		filtered_step_dicts = []
		
		for step_dict in step_dicts:
			if program_counter < const.THRESHOLD_NUM_MISSING_STEPS_ORDER_MISTAKES + base_counter and random.random() < 0.1:
				mistake_dicts.append(Mistake(MistakeTag.MISSING_STEP, step_dict[const.DESCRIPTION]).to_dict())
			else:
				filtered_step_dicts.append(step_dict)
		
		if program_counter > const.THRESHOLD_NUM_MISSING_STEPS + base_counter:
			mistake_dicts.append(Mistake(MistakeTag.ORDER_MISTAKE).to_dict())
		
		return filtered_step_dicts, mistake_dicts
	
	def _shuffle_steps(self, step_dicts):
		num_to_shuffle = len(step_dicts) // 5
		indices_to_shuffle = random.sample(range(len(step_dicts)), num_to_shuffle)
		
		for i in indices_to_shuffle:
			random_index = random.randint(0, len(step_dicts) - 1)
			step_dicts[i], step_dicts[random_index] = step_dicts[random_index], step_dicts[i]
		
		return step_dicts
	
	def generate_recording_data(self):
		for activity_file_name in os.listdir(self.activity_data_directory):
			self.generate_activity_recording_data(activity_file_name)


if __name__ == "__main__":
	current_directory = os.getcwd()
	info_directory = os.path.join(current_directory, "info_files")
	parser = LightTagParser(info_directory)
	parser.generate_recording_data()
