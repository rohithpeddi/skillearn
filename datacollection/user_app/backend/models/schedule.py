from typing import List, Optional
from datacollection.user_app.backend.constants import User_Constants as const


class Schedule:
	
	def __init__(
			self,
			environment: int,
			normal_recordings: List[int],
			mistake_recordings: List[int]
	):
		self.normal = normal_recordings
		self.mistakes = mistake_recordings
		self.environment = environment
		
		self.recorded_list = []
		self.is_done_recording = False
	
	def update_recorded(self, recording_id):
		self.recorded_list.append(recording_id)
		
		if len(self.recorded_list) >= 8:
			self.is_done_recording = True
	
	def to_dict(self) -> dict:
		schedule_dict = {const.ENVIRONMENT: self.environment, const.NORMAL_RECORDINGS: self.normal,
		                 const.MISTAKE_RECORDINGS: self.mistakes}
		
		if len(self.recorded_list) > 0:
			schedule_dict[const.RECORDED_LIST] = self.recorded_list
			schedule_dict[const.IS_DONE_RECORDING] = self.is_done_recording
		
		return schedule_dict
	
	@classmethod
	def from_dict(cls, schedule_dict) -> "Schedule":
		schedule = Schedule(schedule_dict[const.ENVIRONMENT], schedule_dict[const.NORMAL_RECORDINGS],
		                    schedule_dict[const.MISTAKE_RECORDINGS])
		
		if const.RECORDED_LIST in schedule_dict:
			schedule.recorded_list = schedule_dict[const.RECORDED_LIST]
			schedule.is_done_recording = schedule_dict[const.IS_DONE_RECORDING]
		
		return schedule
