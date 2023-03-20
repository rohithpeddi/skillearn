from typing import List, Optional
from datacollection.user_app.backend.constants import *


class Schedule:
	
	def __init__(
			self,
			environment: Optional[int] = None,
			normal_recordings: Optional[List[int]] = None,
			mistake_recordings: Optional[List[int]] = None
	):
		self.normal = normal_recordings
		self.mistakes = mistake_recordings
		self.environment = environment
		
		self.recorded_list = []
		self.recording_status = False
	
	def update_recorded(self, recording_id):
		self.recorded_list.append(recording_id)
		
		if len(self.recorded_list) >= 8:
			self.recording_status = True
	
	def to_dict(self) -> dict:
		schedule_dict = {ENVIRONMENT: self.environment, NORMAL_RECORDINGS: self.normal,
		                 MISTAKE_RECORDINGS: self.mistakes}
		
		if len(self.recorded_list) > 0:
			schedule_dict[RECORDED_LIST] = self.recorded_list
			schedule_dict[RECORDING_STATUS] = self.recording_status
		
		return schedule_dict
	
	@classmethod
	def from_dict(cls, schedule_dict) -> "Schedule":
		schedule = Schedule(schedule_dict[ENVIRONMENT], schedule_dict[NORMAL_RECORDINGS],
		                    schedule_dict[MISTAKE_RECORDINGS])
		
		if RECORDED_LIST in schedule_dict:
			schedule.recorded_list = schedule_dict[RECORDED_LIST]
			schedule.recorded_status = schedule_dict[RECORDING_STATUS]
		
		return schedule
