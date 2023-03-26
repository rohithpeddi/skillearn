from ..models.recording import Recording
from ..services.hololens_service import HololensService
from ..services.open_gopro_service import OpenGoProService
from ..logger_config import logger


class RecordingService:
	
	def __init__(self, recording: Recording):
		self.recording = recording
		self.hololens_service = HololensService()
		self.go_pro_service = OpenGoProService()
	
	def start_recording(self):
		self.hololens_service.start_recording(self.recording)
		self.go_pro_service.start_recording()
	
	def stop_recording(self):
		self.hololens_service.stop_recording()
		self.go_pro_service.stop_recording()
