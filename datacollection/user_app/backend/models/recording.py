from typing import List, Optional

from datacollection.user_app.backend.models.mistake import Mistake
from datacollection.user_app.backend.models.recording_info import RecordingInfo
from datacollection.user_app.backend.models.step import Step

from datacollection.user_app.backend.constants import Recording_Constants as const


class Recording:
	
	def __init__(
			self,
			id: str,
			activity_id: int,
			is_mistake: bool,
			steps: List[Step],
			mistakes: Optional[List[Mistake]] = None
	):
		self.id = id
		self.activity_id = activity_id
		self.is_mistake = is_mistake
		self.steps = steps
		self.mistakes = mistakes
		
		self.environment = None
		self.recorded_by = const.DUMMY_USER_ID
		
		self.is_prepared = False
		self.selected_by = const.DUMMY_USER_ID
		
		self.recording_info = RecordingInfo()

	def get_recording_id(self):
		return self.id
	
	def __str__(self):
		return f"Recording: {self.id} - {self.activity_id} - {self.is_mistake} - {self.environment}"
	
	def update_mistakes(self, recording_mistakes):
		if self.mistakes is None:
			self.mistakes = []
		self.mistakes.extend(recording_mistakes)
		if len(self.mistakes) > 10:
			self.is_prepared = True
	
	def to_dict(self) -> dict:
		recording_dict = {const.ID: self.id, const.ACTIVITY_ID: self.activity_id, const.IS_MISTAKE: self.is_mistake}
		
		step_dict_list = []
		for step in self.steps:
			step_dict_list.append(step.to_dict())
		recording_dict[const.STEPS] = step_dict_list
		
		if self.mistakes is not None and len(self.mistakes) > 0:
			mistake_dict_list = []
			for mistake in self.mistakes:
				mistake_dict_list.append(mistake.to_dict())
			recording_dict[const.MISTAKES] = mistake_dict_list
		
		recording_dict[const.ENVIRONMENT] = self.environment
		recording_dict[const.RECORDED_BY] = self.recorded_by
		recording_dict[const.SELECTED_BY] = self.selected_by
		
		recording_dict[const.RECORDING_INFO] = self.recording_info.to_dict()
		
		if self.is_prepared:
			recording_dict[const.IS_PREPARED] = self.is_prepared
		
		return recording_dict
	
	@classmethod
	def from_dict(cls, recording_dict) -> "Recording":
		
		step_list = []
		for step_dict in recording_dict[const.STEPS]:
			step = Step.from_dict(step_dict)
			step_list.append(step)
		
		recording = cls(recording_dict[const.ID], recording_dict[const.ACTIVITY_ID], recording_dict[const.IS_MISTAKE],
		                step_list)
		
		if const.MISTAKES in recording_dict:
			mistake_list = []
			for mistake_dict in recording_dict[const.MISTAKES]:
				mistake = Mistake.from_dict(mistake_dict)
				mistake_list.append(mistake)
			recording.mistakes = mistake_list
		
		if const.ENVIRONMENT in recording_dict:
			recording.environment = recording_dict[const.ENVIRONMENT]
		
		if const.RECORDED_BY in recording_dict:
			recording.recorded_by = recording_dict[const.RECORDED_BY]
		
		if const.SELECTED_BY in recording_dict:
			recording.selected_by = recording_dict[const.SELECTED_BY]
		
		if const.IS_PREPARED in recording_dict:
			recording.is_prepared = recording_dict[const.IS_PREPARED]
			
		recording.recording_info = RecordingInfo.from_dict(recording_dict[const.RECORDING_INFO])
		return recording
