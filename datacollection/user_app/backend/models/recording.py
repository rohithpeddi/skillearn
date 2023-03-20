from typing import List, Optional

from datacollection.user_app.backend.constants import *
from datacollection.user_app.backend.models.mistake import Mistake
from datacollection.user_app.backend.models.step import Step


class Recording:
	
	def __init__(
			self,
			id: int,
			activity_id: int,
			is_mistake: bool,
			steps: List[Step],
			mistakes: Optional[List[Mistake]]
	):
		self.id = id
		self.activity_id = activity_id
		self.is_mistake = is_mistake
		self.steps = steps
		self.mistakes = mistakes
		
		self.environment = None
		self.recorded_by = None
	
	def to_dict(self) -> dict:
		recording_dict = {ID: self.id, ACTIVITY_ID: self.activity_id, IS_MISTAKE: self.is_mistake}
		
		step_dict_list = []
		for step in self.steps:
			step_dict_list.append(step.to_dict())
		recording_dict[STEPS] = step_dict_list
		
		if len(self.mistakes) > 0:
			mistake_dict_list = []
			for mistake in self.mistakes:
				mistake_dict_list.append(mistake.to_dict())
			recording_dict[MISTAKES] = mistake_dict_list
		
		if self.environment is not None:
			recording_dict[ENVIRONMENT] = self.environment
		
		if self.recorded_by is not None:
			recording_dict[RECORDED_BY] = self.recorded_by
		
		return recording_dict
	
	@classmethod
	def from_dict(cls, recording_dict) -> "Recording":
		
		step_list = []
		for step_dict in recording_dict[STEPS]:
			step = Step.from_dict(step_dict)
			step_list.append(step)
		
		recording = cls(recording_dict[ID], recording_dict[ACTIVITY_ID], recording_dict[IS_MISTAKE], step_list)
		
		if MISTAKES in recording_dict:
			mistake_list = []
			for mistake_dict in recording_dict[MISTAKES]:
				mistake = Mistake.from_dict(mistake_dict)
				mistake_list.append(mistake)
			recording.mistakes = mistake_list
			
		if ENVIRONMENT in recording_dict:
			recording.environment = recording_dict[ENVIRONMENT]
			
		if RECORDED_BY in recording_dict:
			recording.recorded_by = recording_dict[RECORDED_BY]
		
		return recording
