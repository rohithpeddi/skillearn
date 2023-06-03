import os
import shutil


def split_filename(file):
	"""Split the file name by '_' and extract the second number."""
	filename = os.path.splitext(file)[0]  # Remove file extension
	parts = filename.split('_')
	try:
		second_number = int(parts[1])
		return second_number
	except (IndexError, ValueError):
		return None


def create_subfolders(folder_path):
	"""Create 'correct' and 'error' subfolders in the given path if they don't exist."""
	subfolders = ['correct', 'error']
	for subfolder in subfolders:
		subfolder_path = os.path.join(folder_path, subfolder)
		if not os.path.exists(subfolder_path):
			os.mkdir(subfolder_path)


def move_file(file_path, destination_folder):
	"""Move the file to the destination folder."""
	shutil.move(file_path, destination_folder)


def process_files(folder_path):
	"""Process files and move them to the correct subfolder or the error subfolder."""
	files = os.listdir(folder_path)
	for file in files:
		file_path = os.path.join(folder_path, file)
		if os.path.isfile(file_path):
			second_number = split_filename(file)
			if second_number is not None:
				if second_number < 26 or (second_number >= 100 and second_number <= 125):
					correct_folder = os.path.join(folder_path, 'correct')
					move_file(file_path, correct_folder)
				elif (second_number >= 26 and second_number < 99) or second_number >= 126:
					error_folder = os.path.join(folder_path, 'error')
					move_file(file_path, error_folder)


def process_directories(parent_directory_path):
	"""Process directories and move the files to the correct subfolder or the error subfolder."""
	directories = os.listdir(parent_directory_path)
	for directory in directories:
		directory_path = os.path.join(parent_directory_path, directory)
		process_files(directory_path)


# Example usage
folder_path = '/home/rohith/data/ptg'  # Replace with the desired folder path
create_subfolders(folder_path)
process_directories(folder_path)
