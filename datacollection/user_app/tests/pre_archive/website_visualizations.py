import os

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def clip_video(video_path, start_time, end_time, output_directory, vid_name):
	"""
	Clip the video based on start and end times.

	:param video_path: Path to the input video file.
	:param start_time: Start time in seconds.
	:param end_time: End time in seconds.
	:param output_directory: Directory where the clipped video will be saved.
	"""
	# Extract the video name and its extension
	video_name = video_path.split("/")[-1].split(".")[0]
	video_extension = video_path.split(".")[-1]
	
	# Create the output video path
	output_video_path = f"{output_directory}/{vid_name}_clipped.{video_extension}"
	
	# Clip the video
	ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=output_video_path)
	
	print(f"Clipped video saved to: {output_video_path}")


if __name__ == "__main__":
	video_directory = "D:\\UTD\\PUBLICATIONS\\ICLR2024\\WEBSITE"
	hand_visualization_video_name = "vis_points_in_depth_frame.mp4"
	depth_visualization_video_name = "vis_rgbd_head_pose.mp4"
	
	hand_visualization_video_path = os.path.join(video_directory, hand_visualization_video_name)
	# 1. Hand visualization video
	clip_video(hand_visualization_video_path, 0, 15, video_directory, "hand_visualization")
	
	# depth_visualization_video_path = os.path.join(video_directory, depth_visualization_video_name)
	# # 2. Depth and camera visualization video
	# clip_video(depth_visualization_video_path, 0, 10, video_directory, "depth_visualization")

