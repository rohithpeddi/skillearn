import os
import sys


def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


this_dir = os.path.dirname(__file__)

# Add lib to PYTHONPATH
lib_path = os.path.join(this_dir, "../../backend")
add_path(lib_path)

import threading
import time
import logging

import pickle
import av
import cv2
import queue

from fractions import Fraction
from datacollection.backend import hl2ss
from datacollection.backend.Recording import Recording
from datacollection.backend.constants import *

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('Started Audio Video Muxing Service')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class VideoJoiner:

	def __init__(self, data_directory, recording_instance):
		self.recording_instance = recording_instance
		self.tsfirst = None
		self.time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)

		self.recording_id = f'{recording_instance.activity}_{recording_instance.place_id}_{recording_instance.person_id}_{recording_instance.rec_number}'
		self.data_directory = os.path.join(data_directory, self.recording_id)

		self.video_directory = os.path.join(self.data_directory, "pv")

		self.codec_video = av.CodecContext.create(hl2ss.get_video_codec_name(VIDEO_PROFILE), 'r')

		self.video_name = f'{self.recording_id}_video.mp4'
		self.container = av.open(self.video_name, 'w')
		self.stream_video = self.container.add_stream(hl2ss.get_video_codec_name(VIDEO_PROFILE), rate=FRAMERATE)

	def join_video(self):
		for frame_ix, pv_frame_name in enumerate(os.listdir(self.video_directory)):
			pv_frame_path = os.path.join(self.video_directory, pv_frame_name)

			pv_frame_array = cv2.imread(pv_frame_path)
			pv_timestamp = int(((pv_frame_name[:-4]).split("_"))[-1])

			if self.tsfirst is None:
				self.tsfirst = pv_timestamp

			pv_frame_decoded = av.VideoFrame.from_ndarray(pv_frame_array, format=VIDEO_DECODE)

			for packet in self.stream_video.encode(pv_frame_decoded):
				packet.stream = self.stream_video
				packet.pts = pv_timestamp - self.tsfirst
				packet.dts = packet.pts
				packet.time_base = self.time_base

				self.container.mux(packet)

			if frame_ix % 500 == 0:
				print(f'Processed {frame_ix}')

		self.container.close()


if __name__ == '__main__':
	recording_instance = Recording("MugPizza", "PL2", "P2", "R1", False)
	data_parent_directory = "/mnt/d/DATA/COLLECTED/KITCHENS-101/"
	recording_instance.set_device_ip('192.168.0.117')

	video_joiner = VideoJoiner(data_parent_directory, recording_instance)
	video_joiner.join_video()