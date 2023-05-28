import os
from moviepy.editor import VideoFileClip
from pathlib import Path

# video file extensions
video_exts = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]


def fetch_directories(path):
	"""Fetches all the directories in the given path"""
	directories = []
	for entry in os.scandir(path):
		if entry.is_dir():
			directories.append(entry.path)
	return directories


def create_dictionary():
	"""Creates a dictionary of sub folders and their video files"""
	folder_dict = {}
	for folder in fetch_directories(folder_path):
		video_list = []
		for folder_name, sub_folders, file_names in os.walk(folder):
			for file_name in file_names:
				# check if the file is a video file
				if Path(file_name).suffix in video_exts:
					# add the file path to the list of video files
					file_path = os.path.join(folder_name, file_name)
					video_list.append(file_path)
		if video_list:  # check if the list is not empty
			# add the sub folder name and its video files to the dictionary
			folder_dict[Path(folder).name] = video_list
	return folder_dict


def get_video_duration(video_path):
	"""Returns the duration of the video in minutes"""
	clip = VideoFileClip(video_path)
	return round(clip.duration / 60, 2)  # convert to minutes


def write_video_information_to_file(folder_dict):
	"""Writes the duration of each video to a text file"""
	with open('video_duration.txt', 'w') as f:
		total_duration = 0
		total_videos = 0
		for folder, videos in folder_dict.items():
			f.write('-----------------------------------------\n')
			f.write(f'{folder}\n')
			subfolder_duration = 0
			for video in videos:
				video_duration = get_video_duration(video)
				subfolder_duration += video_duration
				f.write(f'{Path(video).name}: {video_duration} minutes\n')
			total_duration += subfolder_duration
			total_videos += len(videos)
			f.write('\n')
			f.write('-----------------------------------------\n')
			f.write('-----------------------------------------\n')
			f.write(f'Total {folder} duration: {subfolder_duration} minutes\n\n')
			f.write(f'Avg {folder} duration: {subfolder_duration / len(videos)} minutes\n\n')
			f.write('-----------------------------------------\n')
			f.write('-----------------------------------------\n')
		f.write(f'Total {folder} duration: {total_duration} minutes\n\n')
		f.write(f'Avg {folder} duration: {total_duration / total_videos} minutes\n\n')
		f.write('-----------------------------------------\n')


if __name__ == '__main__':
	folder_path = 'D:\DATA\COLLECTED\PTG\ERROR-DATASET\ERROR-DATASET'
	folder_dict = create_dictionary()
	write_video_information_to_file(folder_dict)
