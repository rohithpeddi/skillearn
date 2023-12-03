# 1. For each activity build level order traversal of the graph with List[List[Int]] where each list is a level
# 2. For each recording, traverse through steps of the recording and recursively delete the step_id in the order traversal list
# 3. For each level, identify if the step occurs before or after the correct order in the recipe
# 4. Correspondingly assign order error to that step in the recording and update the recording_annotation object
# 5. Persist recording_annotation object to firebase
import json
import re
from typing import List

from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.annotation import Annotation
from datacollection.user_app.backend.app.models.error import Error
from datacollection.user_app.backend.app.models.error_tag import ErrorTag
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.models.recording_annotation import RecordingAnnotation
from datacollection.user_app.backend.app.models.step import Step
from datacollection.user_app.backend.app.models.step_annotation import StepAnnotation
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def build_level_order_traversal(activity: Activity) -> (List[List[int]], dict):
	activity_name = (activity.name.replace(" ", "")).lower()
	activity_json_path = f"../backend/info_files/recordings/v{version}/{activity_name}.json"
	activity_json = json.load(open(activity_json_path))
	
	activity_steps = activity_json["steps"]
	activity_edges = activity_json["edges"]
	
	class StepNode:
		def __init__(self, step_id):
			self.step_id = step_id
			self.step_description = activity_steps[str(step_id)]
			self.children = []
			self.parents = []
	
	step_id_step_node_map = {}
	
	for edge in activity_edges:
		parent_id = edge[0]
		child_id = edge[1]
		if parent_id not in step_id_step_node_map:
			step_id_step_node_map[parent_id] = StepNode(parent_id)
		parent_node = step_id_step_node_map[parent_id]
		
		if child_id not in step_id_step_node_map:
			step_id_step_node_map[child_id] = StepNode(child_id)
		child_node = step_id_step_node_map[child_id]
		
		parent_node.children.append(child_node)
		child_node.parents.append(parent_node)
	
	current_level_nodes = [0]
	level_order_traversal = []
	
	while len(current_level_nodes) > 0:
		level_order_traversal.append(current_level_nodes)
		next_level_nodes = []
		for node_id in current_level_nodes:
			node = step_id_step_node_map[node_id]
			next_level_nodes.extend([child_node.step_id for child_node in node.children])
		current_level_nodes = next_level_nodes
	
	universal_step_counter = len(activity_step_universal_map)
	activity_step_inverse_map = {}
	for idx, step_description in activity_steps.items():
		if step_description not in activity_step_universal_map:
			activity_step_universal_map[step_description] = universal_step_counter
			universal_step_counter += 1
		activity_step_inverse_map[step_description] = idx
	return level_order_traversal, activity_step_inverse_map


def strip_text(text: str):
	text = text.replace(" ", "")
	text = text.lower()
	text = text.replace(".", "")
	text = text.replace(":", "")
	text = text.replace("(", "")
	text = text.replace(")", "")
	return text


def fetch_step_label(step: Step):
	step_alias = ''
	if step.errors is not None and len(step.errors) > 0:
		for error in step.errors:
			step_alias += f' (ErrorTag:{error.tag}, ErrorDescription:{error.description}),'
		step_alias += f' (StepDescription: {step.description})'
	
	if step.modified_description is None or step.modified_description == '':
		step_alias += f' (StepDescription: {step.description})'
	else:
		# step_alias += f', (StepModifiedDescription: {step.modified_description})'
		step_alias += f'(StepDescription: {step.description}), (StepModifiedDescription: {step.modified_description})'
	
	step_descriptions = re.findall(r'\(StepDescription: (.*?)\)', step_alias)
	step_alias = step_descriptions[0]
	step_alias = strip_text(step_alias)
	# if step.errors is not None and len(step.errors) > 0:
	# 	step_alias += f"_{len(step.errors)}_errors)"
	
	return step_alias


def fetch_step_annotation(step_description: str):
	if step_description.endswith(".") or step_description.endswith(","):
		# Remove the last character
		step_description = step_description[:-1]
	
	if step_description == "Weigh-Weigh the coffee beans (8oz-12 oz)":
		step_description = "Weigh-Weigh the coffee beans (0.8oz-0.12 oz)"
	
	if step_description in "Boil-Boil the water. (While the water is boiling, assemble the filter cone)":
		step_description = "Boil-Boil the water. (While the water is boiling, assemble the filter cone)"
	
	if step_description in "Boil-Boil the water (While the water is boiling, assemble the filter cone)":
		step_description = "Boil-Boil the water. (While the water is boiling, assemble the filter cone)"
	
	if step_description == "Roll-Roll the butter around in the cup to coat it":
		step_description = "Roll-Roll the butter around in the mug to coat it"
	
	if step_description == "Put-Put the cup's contents on a plate":
		step_description = "Put-Put the mug's contents on a plate"
	
	if step_description == "add-add  1 tbsp milk to the bowl":
		step_description = "add-add 1 tbsp milk to the bowl"
		
	if step_description == 'pat-immediately pat rinsed mushrooms dry with a paper towel':
		step_description = 'pat-pat rinsed mushrooms dry with a paper towel'
		
	if step_description == 'Melt-Melt the cheese by microwaving cup for 30 sec. (Check after 30 seconds and microwave for 10 seconds more if needed).':
		step_description = 'Melt-Melt the cheese by microwaving cup for 30 sec. (Check after 30 seconds and microwave for 10 seconds more if needed)'
		
	if step_description == "top-top lettuce leaves with the mixture":
		step_description = "top-top lettuce leaves with the tuna mixture"
		
	if step_description == 'Add-Add 1 can tuna in a bowl':
		step_description = 'Add-Add 1 can drained tuna to the bowl'
		
	if step_description == "Toast-Toast both sides of the slices on the pan for 2 to 3 minutes until lightly charred and crispy":
		step_description = "Toast-Toast both sides of the slices on the pan for 2 to 3 minutes until lightly charred and crispy and transfer the slices to a plate"
	
	universal_step_id = activity_step_universal_map[step_description]
	step_annotation = StepAnnotation(universal_step_id, step_description)
	return step_annotation


def fetch_recording_step_description(step_description: str):
	if step_description.endswith(".") or step_description.endswith(","):
		step_description = step_description[:-1]
	
	if step_description == "Roll-Roll the butter around in the cup to coat it":
		step_description = "Roll-Roll the butter around in the mug to coat it"
	
	if step_description == "Put-Put the cup's contents on a plate":
		step_description = "Put-Put the mug's contents on a plate"
	
	return step_description


def fetch_transformed_label(labels: List[str]):
	transformed_labels = re.findall(r'\(StepDescription: (.*?)\)', labels[0])
	# if len(transformed_labels) == 0:
	# 	transformed_labels = re.findall(r'\(StepModifiedDescription: (.*?)\)', labels[0])
	
	if len(transformed_labels) == 0:
		pattern = r'^S\d+'
		match = re.match(pattern, labels[0])
		if match is not None:
			transformed_labels = [re.sub(pattern, '', labels[0])]
	
	transformed_label = strip_text(transformed_labels[0])
	
	if transformed_label == "cook-cookgarlicuntilfragrantabout1minutes":
		transformed_label = "cook-cookgarlicuntilfragrantabout1minutesbecarefulnottoburngarlic"
	
	if transformed_label == "add-addchoppedbasiltothebowl":
		transformed_label = "add-addbasiltothebowl"
	
	return transformed_label


def update_recording_annotation(
		level_order_traversal: List[List[int]],
		activity_step_inverse_map: dict,
		recording: Recording
):
	# 1. Create Step Annotations for recording
	annotation_json = recording_id_to_annotation_map[recording.id].annotation_json
	annotated_steps = annotation_json[0]["annotations"][0]["result"]
	
	step_annotation_list = []
	step_label_to_step_annotation_map = {}
	step_description_to_step_annotation_map = {}
	for step in recording.steps:
		step_annotation = fetch_step_annotation(step.description)
		if step.modified_description is not None and step.modified_description != '':
			step_annotation.modified_description = step.modified_description
		step_annotation.update_errors(step.errors)
		step_label = fetch_step_label(step)
		step_label_to_step_annotation_map[step_label] = step_annotation
		step_description_to_step_annotation_map[step.description] = step_annotation
		step_annotation_list.append(step_annotation)
	
	has_order_errors = False
	if recording.errors is not None and len(recording.errors) > 0:
		for recording_error in recording.errors:
			if recording_error.tag == ErrorTag.MISSING_STEP:
				missing_step_description = recording_error.description
				step_annotation = fetch_step_annotation(missing_step_description)
				step_description_to_step_annotation_map[missing_step_description] = step_annotation
				missing_step_label = strip_text(missing_step_description)
				step_label_to_step_annotation_map[missing_step_label] = step_annotation
				step_annotation_list.append(step_annotation)
			if recording_error.tag == ErrorTag.ORDER_ERROR:
				has_order_errors = True
	
	for annotated_step in annotated_steps:
		start_time = annotated_step["value"]["start"]
		end_time = annotated_step["value"]["end"]
		labels = annotated_step["value"]["labels"]
		
		transformed_label = fetch_transformed_label(labels)
		
		if transformed_label == "cook-cookgarlicuntilfragrantabout1minutes":
			if transformed_label not in step_label_to_step_annotation_map:
				transformed_label = "cook-cookgarlicuntilfragrantabout1minutesbecarefulnottoburngarlic"
		if transformed_label == "cook-cookgarlicuntilfragrantabout1minutesbecarefulnottoburngarlic":
			if transformed_label not in step_label_to_step_annotation_map:
				transformed_label = "cook-cookgarlicuntilfragrantabout1minutes"
				
		step_annotation = step_label_to_step_annotation_map[transformed_label]
		step_annotation.start_time = start_time
		step_annotation.end_time = end_time
	
	# 3. Update Order Error Descriptions in Step Annotations
	if has_order_errors:
		current_recording_order = []
		for step in recording.steps:
			step_description = fetch_recording_step_description(step.description)
			if step_description == "add-add  1 tbsp milk to the bowl":
				step_description = "add-add 1 tbsp milk to the bowl"
			
			if step_description == "top-top lettuce leaves with the mixture":
				step_description = "top-top lettuce leaves with the tuna mixture"
			
			if step_description == 'Add-Add 1 can tuna in a bowl':
				step_description = 'Add-Add 1 can drained tuna to the bowl'
			
			if step_description == "Toast-Toast both sides of the slices on the pan for 2 to 3 minutes until lightly charred and crispy":
				step_description = "Toast-Toast both sides of the slices on the pan for 2 to 3 minutes until lightly charred and crispy and transfer the slices to a plate"
			
			current_recording_order.append(activity_step_inverse_map[step_description])
		
		step_id_to_level_idx_map = {}
		for level_idx in range(len(level_order_traversal)):
			level = level_order_traversal[level_idx]
			for step_id in level:
				step_id_to_level_idx_map[step_id] = level_idx
		
		num_levels = len(level_order_traversal)
		step_idx = 0
		total_num_steps = len(recording.steps)
		for level_idx in range(1, num_levels - 1):
			level = level_order_traversal[level_idx]
			prev_step_count = step_idx
			while step_idx < total_num_steps and step_idx - prev_step_count < len(level):
				current_recording_step_id = current_recording_order[step_idx]
				current_recording_step_id_level_idx = step_id_to_level_idx_map[int(current_recording_step_id)]
				if current_recording_step_id_level_idx < level_idx:
					step_description = recording.steps[step_idx].description
					step_annotation = step_description_to_step_annotation_map[step_description]
					step_annotation.update_errors([Error(ErrorTag.ORDER_ERROR, "Step performed after correct order")])
				elif current_recording_step_id_level_idx > level_idx:
					step_description = recording.steps[step_idx].description
					step_annotation = step_description_to_step_annotation_map[step_description]
					step_annotation.update_errors([Error(ErrorTag.ORDER_ERROR, "Step performed before correct order")])
				step_idx += 1
	
	# 2. Create Recording Annotation
	recording_annotation = RecordingAnnotation(
		recording.id,
		recording.activity_id,
		recording.is_error,
		step_annotation_list
	)
	
	db_service.update_recording_annotation(recording_annotation)


def fetch_recording_id_annotation_map():
	annotations = dict(db_service.fetch_annotations())
	annotation_list = []
	for annotation_id, annotation_dict in annotations.items():
		annotation = Annotation.from_dict(annotation_dict)
		annotation_list.append(annotation)
	id_to_annotation_map = {annotation.recording_id: annotation for annotation in annotation_list}
	return id_to_annotation_map


def process_activities():
	for activity in activities:
		logger.info(f"=========================================================================")
		logger.info(f"Processing activity {activity.name}, id: {activity.id}")
		level_order_traversal, activity_step_inverse_map = build_level_order_traversal(activity)
		activity_recordings_dict = dict(db_service.fetch_all_activity_recordings(activity.id))
		activity_recordings = [
			Recording.from_dict(recording_dict) for recording_dict in activity_recordings_dict.values()
		]
		recorded_activity_recordings = [recording for recording in activity_recordings if recording.recorded_by != -1]
		for activity_recording in recorded_activity_recordings:
			# Continue for un annotated recordings
			if activity_recording.id in ["17_2", "26_37"]:
				continue
			logger.info(f"-------------------------------------------------------------------------")
			logger.info(f"Processing recording {activity_recording.id}")
			level_order_traversal_copy = level_order_traversal.copy()
			update_recording_annotation(level_order_traversal_copy, activity_step_inverse_map, activity_recording)


if __name__ == "__main__":
	version = 2
	db_service = FirebaseService()
	db_service.remove_all_recording_annotations()
	activities_dict = db_service.fetch_activities()
	activity_step_universal_map = {}
	activities = [Activity.from_dict(activity) for activity in activities_dict if activity is not None]
	activity_id_to_activity_name_map = {activity.id: activity.name for activity in activities}
	activity_name_to_activity_id_map = {activity.name: activity.id for activity in activities}
	activity_id_to_activity_map = {activity.id: activity for activity in activities}
	recording_id_to_annotation_map = fetch_recording_id_annotation_map()
	process_activities()
