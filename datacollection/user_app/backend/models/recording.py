from typing import List, Optional

from datacollection.user_app.backend.models.mistake import Mistake
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
		self.recorded_by = None
		
		self.recording_info = None
	
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
		
		if self.environment is not None:
			recording_dict[const.ENVIRONMENT] = self.environment
		
		if self.recorded_by is not None:
			recording_dict[const.RECORDED_BY] = self.recorded_by
		
		if self.recording_info is not None:
			recording_dict[const.RECORDING_INFO] = self.recording_info.to_dict()
		
		return recording_dict
	
	@classmethod
	def from_dict(cls, recording_dict) -> "Recording":
		
		step_list = []
		for step_dict in recording_dict[const.STEPS]:
			step = Step.from_dict(step_dict)
			step_list.append(step)
		
		recording = cls(recording_dict[const.ID], recording_dict[const.ACTIVITY_ID], recording_dict[const.IS_MISTAKE], step_list)
		
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
		
		return recording
