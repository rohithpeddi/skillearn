import os
import threading
from ..models.recording import Recording
from ..services.hololens_service import HololensService
from ..services.open_gopro_service import OpenGoProService
from ..logger_config import logger


class RecordingService:
	
	def __init__(self, recording: Recording):
		self.recording = recording
		self.hololens_service = HololensService()
		self.go_pro_service = OpenGoProService()
		
		self.file_dir = os.path.dirname(os.path.realpath(__file__))
		self.data_dir = os.path.join(self.file_dir, "../../../../data")
		self.go_pro_dir = os.path.join(self.data_dir, "gopro")
		self.hololens_dir = os.path.join(self.data_dir, "hololens")
	
	def start_recording(self):
		logger.info("Starting hololens recording")
		hololens_thread = threading.Thread(target=self.hololens_service.start_recording, args=(self.recording, self.hololens_dir,))
		logger.info("Starting gopro recording")
		go_pro_thread = threading.Thread(target=self.go_pro_service.start_recording)
		
		hololens_thread.start()
		go_pro_thread.start()
		
		hololens_thread.join()
		go_pro_thread.join()
	
	def stop_recording(self):
		logger.info("Stopping hololens recording")
		hololens_thread = threading.Thread(target=self.hololens_service.stop_recording)
		logger.info("Stopping gopro recording")
		go_pro_thread = threading.Thread(target=self.go_pro_service.stop_recording, args=(self.go_pro_dir, self.recording.id,))
		
		hololens_thread.start()
		go_pro_thread.start()
		
		hololens_thread.join()
		go_pro_thread.join()
