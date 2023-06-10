import os
import shutil
import json


def process_files_in_folder(source_folder):
	with open('recipe.json') as recipe_json_file:
		recipe_id_to_name_map = json.load(recipe_json_file)
	
	videos_directory = os.path.join(source_folder, 'videos')
	
	# Get the list of all files in directory tree at given path
	all_files = []
	for dirpath, _, filenames in os.walk(source_folder):
		for f in filenames:
			all_files.append(os.path.join(dirpath, f))
	
	# Loop through all files and process them
	for file_path in all_files:
		if not os.path.isfile(file_path):
			continue
		
		print("Processing", file_path)
		# Split the filename on "_"
		filename = os.path.basename(file_path)
		filename_parts = filename.split("_")
		
		if len(filename_parts) > 1:
			# Create new folder name based on the first element of the split
			if filename_parts[0] not in recipe_id_to_name_map:
				print("Recipe id {} not found in recipe.json".format(filename_parts[0]))
				continue
			
			recipe_name = recipe_id_to_name_map[filename_parts[0]]
			new_folder = os.path.join(videos_directory, recipe_name)
			
			print("Moving {} to {}".format(file_path, new_folder))
			# Create new folder if it doesn't exist
			os.makedirs(new_folder, exist_ok=True)
			
			# Move the file to the new folder
			new_file_path = os.path.join(new_folder, filename)
			shutil.move(file_path, new_file_path)
			print("Moved {} to {}".format(file_path, new_file_path))
	print("Finished processing all files")


def transfer_files_to_normal_error_folders(source_path):
	# Get list of directories
	directories = [dirpath for dirpath, dirnames, filenames in os.walk(source_path) if dirpath != source_path]
	
	for directory in directories:
		print("------------------------------------------------------------------")
		print("Directory is ", directory)
		# Get list of files in each directory
		files = os.listdir(directory)
		
		for file in files:
			
			print("Processing", file)
			# Check if filename can be split on "_"
			if "_" in file:
				parts = file.split("_")
				
				# Check if split resulted in at least 2 parts
				if len(parts) >= 2:
					try:
						# Attempt to convert second part to integer
						num = int(parts[1])
						
						print("Num is", num)
						
						# Define folder name based on conditions
						if 0 <= num <= 25 or 100 <= num <= 125:
							folder_name = 'normal'
						elif 26 <= num <= 99 or num > 125:
							folder_name = 'error'
						else:
							continue
						
						print("Moving {} to {}".format(file, folder_name))
						
						# Create new directory if it does not exist
						new_dir = os.path.join(directory, folder_name)
						if not os.path.exists(new_dir):
							os.makedirs(new_dir)
						
						# Move file to new directory
						shutil.move(os.path.join(directory, file), os.path.join(new_dir, file))
						
						print("Moved {} to {}".format(file, new_dir))
					
					except ValueError:
						# Skip if second part can't be converted to an integer
						continue


def rename_directories(source_path):
	if not os.path.exists(source_path):
		print(f"The path {source_path} does not exist.")
		return
	
	# Iterate through the directory names
	for dirname in os.listdir(source_path):
		full_dirname = os.path.join(source_path, dirname)
		# Skip if not a directory
		if not os.path.isdir(full_dirname):
			continue
		
		print("Processing", dirname)
		# Replace spaces and "'" characters
		new_dirname = dirname.replace(' ', '').replace("'", "")
		print("Processed, new dirname is", new_dirname)
		
		# If the name has changed, rename the directory
		if new_dirname != dirname:
			full_new_dirname = os.path.join(source_path, new_dirname)
			shutil.move(full_dirname, full_new_dirname)


def create_directories(source_path):
	if not os.path.exists(source_path):
		print(f"The path {source_path} does not exist.")
		return
	
	# Iterate through the directory names
	for dirname in os.listdir(source_path):
		directory_path = os.path.join(source_path, dirname)
		# Skip if not a directory
		if not os.path.isdir(directory_path):
			continue
		
		print("Processing", dirname)
		frames_directory_path = os.path.join(directory_path, 'frames')
		os.makedirs(frames_directory_path, exist_ok=True)
		print("Processed, new dirname is", frames_directory_path)
		
		annotations_directory_path = os.path.join(directory_path, 'annotations')
		print("Processing", annotations_directory_path)
		os.makedirs(annotations_directory_path, exist_ok=True)
		print("Processed, new dirname is", annotations_directory_path)
		
		annotations_normal_directory_path = os.path.join(annotations_directory_path, 'normal')
		annotations_error_directory_path = os.path.join(annotations_directory_path, 'error')
		os.makedirs(annotations_normal_directory_path, exist_ok=True)
		print("Processed, new dirname is", annotations_normal_directory_path)
		os.makedirs(annotations_error_directory_path, exist_ok=True)
		print("Processed, new dirname is", annotations_error_directory_path)


def create_execution_scripts(path):
	with open("execution_scripts.txt", "w") as execution_file:
		for file in os.listdir(path):
			script = ""
			if os.path.isfile(os.path.join(path, file)):
				script += f"python -m RepLearn.TCC.main --cfg configs/{file}"
				execution_file.write(script + "\n")


def prepare_egoprocel_data(source_folder):
	with open('../processed_files/activity_id_to_activity_name_map.json') as activity_id_to_activity_name_map_json_file:
		activity_id_to_activity_name_map = json.load(activity_id_to_activity_name_map_json_file)
	
	# Get the list of all files in directory tree at given path
	all_files = []
	for dirpath, _, filenames in os.walk(source_folder):
		for f in filenames:
			all_files.append(os.path.join(dirpath, f))
	
	# Loop through all files and process them
	for file_path in all_files:
		if not os.path.isfile(file_path):
			continue
		
		print("Processing", file_path)
		# Split the filename on "_"
		filename = os.path.basename(file_path)
		filename_parts = filename.split("_")
		
		if len(filename_parts) > 1:
			# Create new folder name based on the first element of the split
			if filename_parts[0] not in activity_id_to_activity_name_map:
				print("Recipe id {} not found in recipe.json".format(filename_parts[0]))
				continue
			
			recipe_name = activity_id_to_activity_name_map[filename_parts[0]]
			recipe_folder = os.path.join(source_folder, recipe_name)
			
			# Create new folder if it doesn't exist
			os.makedirs(recipe_folder, exist_ok=True)
			
			# ----------------- Create Frames Folder -----------------
			recipe_frames_folder = os.path.join(recipe_folder, 'frames')
			os.makedirs(recipe_frames_folder, exist_ok=True)
			
			# ----------------- Create Annotations Folder -----------------
			recipe_annotations_folder = os.path.join(recipe_folder, 'annotations')
			os.makedirs(recipe_annotations_folder, exist_ok=True)
			
			# ----------------- Create Normal and Error Folders -----------------
			recipe_annotations_normal_folder = os.path.join(recipe_annotations_folder, 'normal')
			os.makedirs(recipe_annotations_normal_folder, exist_ok=True)
			
			recipe_annotations_error_folder = os.path.join(recipe_annotations_folder, 'error')
			os.makedirs(recipe_annotations_error_folder, exist_ok=True)
			
			# ----------------- Create Videos Folder -----------------
			
			recipe_videos_folder = os.path.join(recipe_folder, 'videos')
			os.makedirs(recipe_videos_folder, exist_ok=True)
			
			recording_number = filename_parts[1]
			if 0 <= recording_number <= 25 or 100 <= recording_number <= 125:
				recording_type = 'normal'
			elif 26 <= recording_number <= 99 or recording_number > 125:
				recording_type = 'error'
			else:
				continue
			
			recipe_videos_recording_type_folder = os.path.join(recipe_videos_folder, recording_type)
			os.makedirs(recipe_videos_recording_type_folder, exist_ok=True)
			
			# Move the file to the new folder
			new_file_path = os.path.join(recipe_videos_recording_type_folder, filename)
			shutil.move(file_path, new_file_path)
			print("Moved {} to {}".format(file_path, new_file_path))
	print("Finished processing all files")


if __name__ == '__main__':
	# process_files_in_folder('/home/rohith/data/ptg')
	# transfer_files_to_normal_error_folders('/home/rohith/data/ptg')
	# rename_directories('/home/rohith/data/ptg')
	prepare_egoprocel_data('/home/rohith/data/ptg')
