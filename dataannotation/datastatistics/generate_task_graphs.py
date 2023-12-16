import json
import os


def generate_task_graphs_with_global_step_ids(step_description_to_step_idx_map):
	local_task_graph_directory = "task_graphs/local_step_ids"
	global_task_graph_directory = f"task_graphs/global_step_ids/v{version}"
	os.makedirs(global_task_graph_directory, exist_ok=True)
	
	step_description_to_step_idx_map["START"] = 0
	step_description_to_step_idx_map["END"] = 1000
	for task_graph_file_name in os.listdir(local_task_graph_directory):
		local_task_graph = json.load(open(f"{local_task_graph_directory}/{task_graph_file_name}", 'r'))
		global_task_graph = {}
		local_step_global_step_map = {}
		global_step_map = {}
		for local_step_idx, step_description in local_task_graph["steps"].items():
			try:
				global_step_idx = step_description_to_step_idx_map[step_description]
			except KeyError:
				print(f"Step description {step_description} not found in step_description_to_step_idx_map")
				raise
			local_step_global_step_map[int(local_step_idx)] = int(global_step_idx)
			global_step_map[global_step_idx] = step_description
		
		edges_local_step_ids = local_task_graph["edges"]
		edges_global_step_ids = []
		for edge in edges_local_step_ids:
			edges_global_step_ids.append([
				local_step_global_step_map[edge[0]],
				local_step_global_step_map[edge[1]]
			])
			
		global_task_graph["steps"] = global_step_map
		global_task_graph["edges"] = edges_global_step_ids
		
		with open(f"{global_task_graph_directory}/{task_graph_file_name}", 'w') as f:
			json.dump(global_task_graph, f)


def main():
	step_idx_description = json.load(open(f"annotation_jsons/v{version}/step_idx_description.json", 'r'))
	
	step_description_to_step_idx_map = {}
	for step_idx, step_description in step_idx_description.items():
		step_description_to_step_idx_map[step_description] = step_idx
		
	generate_task_graphs_with_global_step_ids(step_description_to_step_idx_map)


if __name__ == '__main__':
	version = 5
	main()
