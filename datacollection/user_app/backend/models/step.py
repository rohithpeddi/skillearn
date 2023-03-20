from typing import Optional
from datacollection.user_app.backend.constants import *
from datacollection.user_app.backend.models.mistake import Mistake


class Step:
	
	def __init__(
			self,
			description: str,
			modified_description: Optional[str] = None
	):
		self.description = description
		self.modified_description = modified_description
		
		self.mistakes = []
	
	def update_mistakes(self, step_mistakes):
		self.mistakes.extend(step_mistakes)
	
	def to_dict(self) -> dict:
		step_dict = {DESCRIPTION: self.description}
		
		if self.modified_description is not None:
			step_dict[MODIFIED_DESCRIPTION] = self.modified_description
		
		if len(self.mistakes) > 0:
			step_mistake_dict_list = []
			for step_mistake in self.mistakes:
				step_mistake_dict_list.append(step_mistake.to_dict())
				
			step_dict[MISTAKES] = step_mistake_dict_list
		
		return step_dict
	
	@classmethod
	def from_dict(cls, step_dict) -> "Step":
		step = cls(step_dict[DESCRIPTION])
		
		if MODIFIED_DESCRIPTION in step_dict:
			step.modified_description = step_dict[MODIFIED_DESCRIPTION]
		
		if MISTAKES in step_dict:
			step_mistakes_list = []
			for step_mistake_dict in step_dict[MISTAKES]:
				step_mistake = Mistake.from_dict(step_mistake_dict)
				step_mistakes_list.append(step_mistake)
			step.mistakes = step_mistakes_list
			
		return step
		
		
		
