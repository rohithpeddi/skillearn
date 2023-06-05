# import decord
# import matplotlib.pyplot as plt
# import numpy as np
# from collections import OrderedDict
#
# import torch
# import torchvision.transforms as transforms
# import torchvision.transforms._transforms_video as transforms_video
#
# import sys
#
# sys.path.insert(0, './')
# from lavila.data.video_transforms import Permute
# from lavila.data.datasets import get_frame_ids, video_loader_by_frames
# from lavila.models.models import VCLM_OPENAI_TIMESFORMER_BASE_GPT2
# from lavila.models.tokenizer import MyGPT2Tokenizer
#
# import json
# import os
# import os.path as osp
# import yaml
#
# from datacollection.user_app.backend.app.services.box_service import BoxService
#
#
# def add_path(path):
# 	if path not in sys.path:
# 		sys.path.insert(0, path)
#
#
# def initialize_paths():
# 	this_dir = osp.dirname(__file__)
#
# 	lib_path = osp.join(this_dir, "../../datacollection")
# 	add_path(lib_path)
#
#
# def load_yaml_file(file_path):
# 	with open(file_path, 'r') as file:
# 		try:
# 			data = yaml.safe_load(file)
# 			return data
# 		except yaml.YAMLError as e:
# 			print(f"Error while parsing YAML file: {e}")
#
#
# initialize_paths()
#
# from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
# from datacollection.user_app.backend.app.models.recording import Recording
# from datacollection.user_app.backend.app.models.activity import Activity
# from moviepy.editor import VideoFileClip
#
#
# def create_directory(output_directory):
# 	if not osp.exists(output_directory):
# 		os.makedirs(output_directory)
#
#
# class LavilaVideoTranscript:
#
# 	def __init__(self, recording: Recording, video_directory):
# 		self.video_directory = video_directory
#
# 		self.num_segments = 4
# 		self.video_path = os.path.join(self.video_directory, f'{recording.id}_360p.mp4')
#
# 		self._prepare_video()
#
# 	def _prepare_video(self):
# 		vr = decord.VideoReader(self.video_path)
# 		num_seg = 4
# 		frame_ids = get_frame_ids(0, len(vr), num_segments=num_seg, jitter=False)
# 		frames = video_loader_by_frames('./', self.video_path, frame_ids)
