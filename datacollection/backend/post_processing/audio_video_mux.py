import os
import queue
import threading
import time
import logging

import av
import cv2

from fractions import Fraction
from datacollection.backend import hl2ss
from datacollection.backend.Recording import Recording
from datacollection.backend.constants import VIDEO_PROFILE, AUDIO_PROFILE, FRAMERATE

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('Started Audio Video Muxing Service')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MuxAudioVideo:

	def __init__(self, data_directory, recording_instance):
		self.tsfirst = None
		self.time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)
		self.lock = threading.Lock()
		self.rm_pv_enable = True
		self.packet_queue = queue.PriorityQueue()

		self.data_directory = data_directory
		self.recording_instance = recording_instance

		self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPG # case-sensitive Codecs
		self.vlc_fourcc = cv2.VideoWriter_fourcc(*'H264')  # mp4v, H264, DIVX # case-sensitive Codecs

		self.stream_video = self.container.add_stream(hl2ss.get_video_codec_name(VIDEO_PROFILE), rate=FRAMERATE)
		self.stream_audio = self.container.add_stream(hl2ss.get_audio_codec_name(AUDIO_PROFILE),
													  rate=hl2ss.Parameters_MICROPHONE.SAMPLE_RATE)

	def _process_pv(self):
		codec_video = av.CodecContext.create(hl2ss.get_video_codec_name(VIDEO_PROFILE), 'r')
		# 1. Fetch list of images in a directory
		pv_directory_path = os.path.join(self.data_directory, "pv")

		# 2. Loop through all images and store corresponding timestamps and encoded payload
		for pv_frame_name in os.listdir(pv_directory_path):
			pv_frame_path = os.path.join(pv_directory_path, pv_frame_name)

			# Reading in unchanged format
			pv_frame_data = cv2.imread(pv_frame_path, -1)
			pv_timestamp = int(((pv_frame_name[:-4]).split("_"))[-1])

			self.lock.acquire()
			if not self.tsfirst:
				self.tsfirst = pv_timestamp
			self.lock.release()
			for packet in codec_video.parse(data.payload):
				packet.stream = self.stream_video
				packet.pts = pv_timestamp - self.tsfirst
				packet.dts = packet.pts
				packet.time_base = self.time_base
				self.packet_queue.put((packet.pts, packet))

	def _process_audio(self):
		codec_audio = av.CodecContext.create(hl2ss.get_audio_codec_name(AUDIO_PROFILE), 'r')
		while self.rm_pv_enable:
			data = pv_client.get_next_packet()
			self.lock.acquire()
			if not self.tsfirst:
				self.tsfirst = data.timestamp
			self.lock.release()

			for packet in codec_audio.parse(data.payload):
				packet.stream = self.stream_audio
				packet.pts = data.timestamp - self.tsfirst
				packet.dts = packet.pts
				packet.time_base = self.time_base
				self.packet_queue.put((packet.pts, packet))

	def mux_pv_audio(self):
		logger.log(logging.INFO, "Configuring muxing")
		while self.rm_pv_enable:
			tuple = self.packet_queue.get()
			ts = tuple[0]
			self.container.mux(tuple[1])


if __name__ == '__main__':
	rec = Recording("Coffee", "PL1", "P1", "R1", False)
	data_directory = ""
	rec.set_device_ip('192.168.0.117')

	mav = MuxAudioVideo()

	rec_thread = threading.Thread(target=mav.mux_pv_audio(), args=(rec,))
	rec_thread.start()
	print("Recording Started")
	sleep_min = 1
	for min_done in range(sleep_min):
		print("Minutes done {}".format(min_done))
		time.sleep(60)

	mav.stop_recording()
	print("Recording Stopped")
	rec_thread.join()
