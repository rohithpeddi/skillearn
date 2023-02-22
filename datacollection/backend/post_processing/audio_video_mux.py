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


class MuxAudioVideo:

	def __init__(self, data_directory, recording_instance):
		self.muxing_thread_list = []
		self.tsfirst = None
		self.time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)
		self.lock = threading.Lock()
		self.rm_pv_enable = True
		self.packet_queue = queue.PriorityQueue()

		self.recording_instance = recording_instance
		self.recording_id = f'{self.recording_instance.activity}_{self.recording_instance.place_id}_{self.recording_instance.person_id}_{self.recording_instance.rec_number}'
		self.data_directory = os.path.join(data_directory, self.recording_id)

		self.video_directory = os.path.join(self.data_directory, "pv")
		self.audio_directory = os.path.join(self.data_directory, "mc")

		# self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPG # case-sensitive Codecs
		# self.vlc_fourcc = cv2.VideoWriter_fourcc(*'H264')  # mp4v, H264, DIVX # case-sensitive Codecs

		self.container = av.open(f'{self.recording_id}.mp4', 'w')

		self.stream_video = self.container.add_stream(hl2ss.get_video_codec_name(VIDEO_PROFILE_DECODED), rate=FRAMERATE)
		self.stream_audio = self.container.add_stream(hl2ss.get_audio_codec_name(AUDIO_PROFILE),
													  rate=hl2ss.Parameters_MICROPHONE.SAMPLE_RATE)

		self.codec_audio = av.CodecContext.create(hl2ss.get_audio_codec_name(AUDIO_PROFILE), 'r')
		self.codec_video = av.CodecContext.create(hl2ss.get_video_codec_name(VIDEO_PROFILE_DECODED), 'r')

	def process_pv(self):
		# 1. Fetch list of images in a directory
		# 2. Loop through all images and store corresponding timestamps and encoded payload

		frame_list = os.listdir(self.video_directory)
		frame_list.sort(key=lambda x: int(((x[:-4]).split("_"))[-1]))

		logger.log(logging.INFO, "Started Video Processing")
		for frame_idx, pv_frame_name in enumerate(frame_list):
			pv_frame_path = os.path.join(self.video_directory, pv_frame_name)

			pv_frame_array = cv2.imread(pv_frame_path)
			pv_timestamp = int(((pv_frame_name[:-4]).split("_"))[-1])

			self.lock.acquire()
			if self.tsfirst is None:
				self.tsfirst = pv_timestamp
			self.lock.release()

			pv_frame_decoded = av.VideoFrame.from_ndarray(pv_frame_array, format=VIDEO_DECODE)

			for packet in self.stream_video.encode(pv_frame_decoded):
				packet.stream = self.stream_video
				packet.pts = pv_timestamp - self.tsfirst
				packet.dts = packet.pts
				packet.time_base = self.time_base

				self.packet_queue.put((packet.pts, packet))

			if frame_idx % 1000 == 0:
				logger.log(logging.INFO, f"Processed '{frame_idx}' video frames")

	def process_audio(self):
		mc_data_file_name = "audio_data.pkl"
		mc_data_file_path = os.path.join(self.audio_directory, mc_data_file_name)

		logger.log(logging.INFO, "Began Audio Processing")
		while self.tsfirst is None:
			time.sleep(0.3)

		logger.log(logging.INFO, "Started Audio Processing")
		# Load the pickle file
		with open(mc_data_file_path, 'rb') as mc_data_file:
			mc_frame_list = pickle.load(mc_data_file)

			for mc_frame_idx, mc_frame in enumerate(mc_frame_list):
				mc_frame_timestamp = int(mc_frame[0])
				mc_frame_payload = mc_frame[1]

				if self.tsfirst - mc_frame_timestamp > 1e4:
					continue

				for packet in self.codec_audio.parse(mc_frame_payload):
					packet.stream = self.stream_audio
					packet.pts = mc_frame_timestamp - self.tsfirst
					packet.dts = packet.pts
					packet.time_base = self.time_base

					self.packet_queue.put((packet.pts, packet))

				if mc_frame_idx % 1000 == 0:
					logger.log(logging.INFO, f"Processed '{mc_frame_idx}' audio frames")

	def mux_pv_audio(self):
		logger.log(logging.INFO, "Configuring muxing")
		while self.rm_pv_enable:
			q_size = self.packet_queue.qsize()

			if q_size == 0:
				self.rm_pv_enable = False
				break

			if q_size % 500 == 0:
				logger.log(logging.INFO, f"Queue has '{q_size}' frames in it")

			tuple = self.packet_queue.get()
			timestamp = tuple[0]
			self.container.mux(tuple[1])

		logger.log(logging.INFO, "Stopped muxing")
		self.container.close()

	def start_muxing_sync(self):
		logger.log(logging.INFO, "Started synchronized audio-video muxing")
		self.process_pv()
		logger.log(logging.INFO, "Added video frames to the Priority Queue")
		self.process_audio()
		logger.log(logging.INFO, "Added audio frames to the Priority Queue")
		self.mux_pv_audio()

	def start_muxing_async(self):
		pv_thread = threading.Thread(target=self.process_pv)
		mc_thread = threading.Thread(target=self.process_audio)
		mux_thread = threading.Thread(target=self.mux_pv_audio)

		muxing_threads = [pv_thread, mc_thread, mux_thread]

		for thread in muxing_threads:
			thread.start()

	def stop_muxing(self):
		pass


def mux_directory(data_directory):

	recipe_list = os.listdir(data_directory)
	recipe_list.sort(key=lambda x: ((x.split("_"))[0]))

	for recipe_name in recipe_list:
		recording_arguments = recipe_name.split("_")
		recording_instance = Recording(recording_arguments[0], recording_arguments[1], recording_arguments[2], recording_arguments[3], False)

		logger.log(logging.INFO, f"Started synchronized audio-video muxing for recording {recording_arguments[0]}")

		mav = MuxAudioVideo(data_directory, recording_instance)
		mav.start_muxing_sync()


if __name__ == '__main__':
	# recording_instance = Recording("EggSandwich", "PL2", "P5", "R1", False)
	# data_parent_directory = "/home/ptg/CODE/DATA/data_2022_02_11"
	# recording_instance.set_device_ip('192.168.0.117')
	#
	# mav = MuxAudioVideo(data_parent_directory, recording_instance)
	# mav.start_muxing_sync()

	data_parent_directory = "/home/ptg/CODE/DATA/data_2022_02_11"
	mux_directory(data_parent_directory)

# print("Started Muxing")
# sleep_min = 100
# for min_done in range(sleep_min):
# 	print("Minutes done {}".format(min_done))
# 	time.sleep(60)
# 	if not mav.rm_pv_enable:
# 		break

# mav.stop_recording()
# print("Recording Stopped")
# rec_thread.join()
