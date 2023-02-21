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

import multiprocessing as mp
import open3d as o3d

from fractions import Fraction
from datacollection.backend import hl2ss
from datacollection.backend import hl2ss_mp
from datacollection.backend import hl2ss_3dcv
from datacollection.backend.Recording import Recording
from datacollection.backend.constants import *

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('Started Depth Verification')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class VerifyDepth:

	def __init__(self, data_directory, recording_instance):
		self.recording_instance = recording_instance

		self.recording_id = f'{recording_instance.activity}_{recording_instance.place_id}_{recording_instance.person_id}_{recording_instance.rec_number}'
		self.data_directory = os.path.join(data_directory, self.recording_id)

		self.calibration_directory = os.path.join(self.data_directory, "calibration")
		self.pv_directory = os.path.join(self.data_directory, "pv")
		self.ahat_directory = os.path.join(self.data_directory, "dep_ahat_depth")

		calibration_ahat = hl2ss_3dcv.get_calibration_rm(recording_instance.device_ip, hl2ss.StreamPort.RM_DEPTH_AHAT,
														 self.calibration_directory)
		calibration_pv = hl2ss_3dcv.get_calibration_pv(recording_instance.device_ip,
													   hl2ss.StreamPort.PHOTO_VIDEO,
													   self.calibration_directory, PV_FOCUS,
													   PV_WIDTH, PV_HEIGHT, PV_FRAMERATE, True)


if __name__ == '__main__':
	recording_instance = Recording("MugPizza", "PL2", "P2", "R1", False)
	data_parent_directory = "/mnt/d/DATA/COLLECTED/KITCHENS-101/"
	recording_instance.set_device_ip('192.168.0.117')

	verify_depth = VerifyDepth(data_parent_directory, recording_instance)
