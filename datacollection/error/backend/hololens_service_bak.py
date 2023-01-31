import os
import queue
import threading
from fractions import Fraction

import av
import cv2
import numpy as np

from datacollection.error.backend.constants import *


class HololensService:

	def __init__(self, hololens_ip):
		self.hololens_ip = hololens_ip
		self.tsfirst = None
		self.enable = True
		self.lock = threading.Lock()
		self.packet_queue = queue.PriorityQueue()
		self.time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)

		self.depth_frames_dir_path = "../frames/depth/"
		self.ab_dir_path = "../frames/ab/"

	def _init_params_(self, recipe, kitchen_id, person_id, recording_number):
		self.video_file_name = "{}_{}_{}_{}.mp4".format(recipe, kitchen_id, person_id, recording_number)
		self.container = av.open(self.video_file_name, 'w')
		self.stream_video = self.container.add_stream(hl2ss.get_video_codec_name(VIDEO_PROFILE), rate=FRAMERATE)
		self.stream_audio = self.container.add_stream(hl2ss.get_audio_codec_name(AUDIO_PROFILE),
													  rate=hl2ss.Parameters_MICROPHONE.SAMPLE_RATE)

	def _receive_pv_(self):
		codec_video = av.CodecContext.create(hl2ss.get_video_codec_name(VIDEO_PROFILE), 'r')
		pv_client = hl2ss.rx_pv(HOLOLENS_IP, hl2ss.StreamPort.PERSONAL_VIDEO, hl2ss.ChunkSize.PERSONAL_VIDEO,
								hl2ss.StreamMode.MODE_0, FRAME_WIDTH, FRAME_HEIGHT, FRAMERATE, VIDEO_PROFILE,
								VIDEO_BITRATE)
		pv_client.open()
		while self.enable:
			data = pv_client.get_next_packet()
			self.lock.acquire()
			if not self.tsfirst:
				self.tsfirst = data.timestamp
			self.lock.release()
			for packet in codec_video.parse(data.payload):
				packet.stream = self.stream_video
				packet.pts = data.timestamp - self.tsfirst
				packet.dts = packet.pts
				packet.time_base = self.time_base
				self.packet_queue.put((packet.pts, packet))
		pv_client.close()

	def _receive_mc_(self):
		codec_audio = av.CodecContext.create(hl2ss.get_audio_codec_name(AUDIO_PROFILE), 'r')
		mc_client = hl2ss.rx_microphone(HOLOLENS_IP, hl2ss.StreamPort.MICROPHONE, hl2ss.ChunkSize.MICROPHONE,
										AUDIO_PROFILE)
		mc_client.open()
		while self.enable:
			data = mc_client.get_next_packet()
			self.lock.acquire()
			leave = self.tsfirst is None
			self.lock.release()

			if leave:
				continue
			for packet in codec_audio.parse(data.payload):
				packet.stream = self.stream_audio
				packet.pts = data.timestamp - self.tsfirst
				packet.dts = packet.pts
				packet.time_base = self.time_base
				self.packet_queue.put((packet.pts, packet))
		mc_client.close()

	def _receive_depth_(self):
		depth_client = hl2ss.rx_decoded_rm_depth_ahat(HOLOLENS_IP, DEPTH_PORT, hl2ss.ChunkSize.RM_DEPTH_AHAT,
													  DEPTH_MODE, VIDEO_PROFILE, DEPTH_BITRATE)
		depth_client.open()

		while self.enable:
			data = depth_client.get_next_packet()

			self.lock.acquire()
			leave = self.tsfirst is None
			self.lock.release()

			if leave:
				continue

			print('Pose at time {ts}'.format(ts=data.timestamp))
			print(data.pose)

			cv2.imshow('Depth', data.payload.depth / np.max(data.payload.depth))  # Normalized for visibility
			cv2.imshow('AB', data.payload.ab / np.max(data.payload.ab))  # Normalized for visibility

			def save_file(directory, filename, payload):
				file_path = os.path.join(directory, filename)
				directories = os.path.dirname(file_path)

				if not os.path.exists(directories):
					os.makedirs(directories)

				cv2.imwrite(file_path, payload)

			save_file(self.depth_frames_dir_path, "Depth_{}.png".format(data.timestamp), data.payload.depth)
			save_file(self.ab_dir_path, "AB_{}.png".format(data.timestamp), data.payload.ab)
			cv2.waitKey(1)


