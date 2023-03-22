from typing import List, Optional

from datacollection.user_app.backend.models.mistake import Mistake
from datacollection.user_app.backend.models.step import Step
from datacollection.user_app.backend.constants import DatabaseIngestion_Constants as const


class RecordingIngestionHelper:
	
	def __init__(
			self,
			recording_id: int,
			steps: List[Step],
			mistakes: Optional[List[Mistake]] = None
	):
		self.recording_id = recording_id
		
		self.steps = steps
		self.mistakes = mistakes
	
	def to_dict(self) -> dict:
		return {const.RECORDING_ID: self.recording_id,
		        const.STEPS: [step.to_dict() for step in self.steps],
		        const.MISTAKES: [mistake.to_dict() for mistake in self.mistakes]}
	
	@classmethod
	def from_dict(cls, recording_helper_dict) -> "RecordingIngestionHelper":
		recording_id = recording_helper_dict[const.RECORDING_ID]
		steps = [Step.from_dict(step_dict) for step_dict in recording_helper_dict[const.STEPS]]
		
		mistakes = None
		if const.MISTAKES in recording_helper_dict:
			mistakes = [Mistake.from_dict(mistake_dict) for mistake_dict in recording_helper_dict[const.MISTAKES]]
		
		recording_helper = cls(recording_id, steps, mistakes)
		return recording_helper
