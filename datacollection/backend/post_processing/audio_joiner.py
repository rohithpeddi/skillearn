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


class AudioJoiner:

	def __init__(self, data_directory, recording_instance):
		self.recording_instance = recording_instance
		self.tsfirst = None
		self.time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)

		self.recording_id = f'{recording_instance.activity}_{recording_instance.place_id}_{recording_instance.person_id}_{recording_instance.rec_number}'
		self.data_directory = os.path.join(data_directory, self.recording_id)

		self.audio_directory = os.path.join(self.data_directory, "mc")
		self.audio_file_name = "audio_data.pkl"
		self.audio_file_path = os.path.join(self.audio_directory, self.audio_file_name)

		self.codec_audio = av.CodecContext.create(hl2ss.get_audio_codec_name(AUDIO_PROFILE), 'r')

		self.audio_name = f'{self.recording_id}_audio.mp4'
		self.container = av.open(self.audio_name, 'w')
		self.stream_audio = self.container.add_stream(hl2ss.get_audio_codec_name(AUDIO_PROFILE),
													  rate=hl2ss.Parameters_MICROPHONE.SAMPLE_RATE)

	def join_audio(self):
		with open(self.audio_file_path, 'rb') as mc_file:
			mc_frame_list = pickle.load(mc_file)
			for frame in mc_frame_list:
				timestamp = int(frame[0])
				if self.tsfirst is None:
					self.tsfirst = timestamp
				for packet in self.codec_audio.parse(frame[1]):
					packet.stream = self.stream_audio
					packet.pts = timestamp - self.tsfirst
					packet.dts = packet.pts
					packet.time_base = self.time_base
					self.container.mux(packet)
		self.container.close()


if __name__ == '__main__':
	recording_instance = Recording("MugPizza", "PL2", "P2", "R1", False)
	data_parent_directory = "/mnt/d/DATA/COLLECTED/KITCHENS-101/"
	recording_instance.set_device_ip('192.168.0.117')

	audio_joiner = AudioJoiner(data_parent_directory, recording_instance)
	audio_joiner.join_audio()

