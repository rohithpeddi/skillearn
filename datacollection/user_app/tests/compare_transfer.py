import os


def compare_files_in_folder(source_root, destination_root):
	# 1. Get all the files in the source folder and destination folder and compare them
	source_files = [f for f in os.listdir(source_root) if os.path.isfile(os.path.join(source_root, f))]
	
	for file in source_files:
		source_file = os.path.join(source_root, file)
		destination_file = os.path.join(destination_root, file)
		
		if not os.path.isfile(destination_file):
			print(f"File {destination_file} is missing.")
			return False
		
		if os.path.getsize(source_file) != os.path.getsize(destination_file):
			print(f"File {destination_file} has a different size.")
			return False
	
	return True


def compare_folders(source_root, destination_root):
	# 1. Check if all files in the source folder are present in the destination folder
	are_files_matching = compare_files_in_folder(source_root, destination_root)
	
	if not are_files_matching:
		print("-----------------------------------")
		print("Files are missing.")
		print("Source folder: ", source_root)
		print("Destination folder: ", destination_root)
		print("-----------------------------------")
		return False
	
	# 2. Get all the sub folders in the source folder and destination folder and compare them recursively
	source_directories = [d for d in os.listdir(source_root) if os.path.isdir(os.path.join(source_root, d))]
	destination_directories = [d for d in os.listdir(destination_root) if
	                           os.path.isdir(os.path.join(destination_root, d))]
	
	for directory in source_directories:
		source_directory = os.path.join(source_root, directory)
		destination_directory = os.path.join(destination_root, directory)
		
		if not os.path.isdir(destination_directory):
			print(f"Directory {destination_directory} is missing.")
			return False
		
		are_folders_matching = compare_folders(source_directory, destination_directory)
		
		if not are_folders_matching:
			print("-----------------------------------")
			print("Folder files are missing.")
			print("Source folder: ", source_directory)
			print("Destination folder: ", destination_directory)
			print("-----------------------------------")
			return False

if __name__ == '__main__':
	pass
