from typing import List

from datacollection.user_app.backend.models.mistake import Mistake
from datacollection.user_app.backend.models.mistake_tag import MistakeTag
from datacollection.user_app.backend.models.step import Step
from datacollection.user_app.backend.constants import Recording_Constants as const


class Activity:
	
	def __init__(
			self,
			id: int,
			name: str,
			category: str,
			activity_type: str,
			mistake_hints: List[Mistake],
			steps: List[Step],
			required_items: dict
	):
		self.id = id
		self.name = name
		self.category = category
		self.activity_type = activity_type
		self.required_items = required_items
		
		self.steps = steps
		self.mistake_hints = mistake_hints
	
	def to_dict(self) -> dict:
		activity_dict = {
			const.ID: self.id,
			const.NAME: self.name,
			const.CATEGORY: self.category,
			const.ACTIVITY_TYPE: self.activity_type,
			const.REQUIRED_ITEMS: self.required_items
		}
		
		step_dict_list = []
		for step in self.steps:
			step_dict_list.append(step.to_dict())
		activity_dict[const.STEPS] = step_dict_list
		
		mistake_dict_list = []
		for mistake in self.mistake_hints:
			mistake_dict_list.append(mistake.to_dict())
		activity_dict[const.MISTAKE_HINTS] = mistake_dict_list
		
		return activity_dict
	
	@classmethod
	def from_dict(cls, activity_dict: dict) -> "Activity":
		step_list = []
		for step_dict in activity_dict[const.STEPS]:
			step_list.append(Step.from_dict(step_dict))
		
		mistake_hint_list = []
		for mistake_dict in activity_dict[const.MISTAKE_HINTS]:
			mistake_hint_list.append(Mistake.from_dict(mistake_dict))
		
		return cls(
			id=activity_dict[const.ID],
			name=activity_dict[const.NAME],
			category=activity_dict[const.CATEGORY],
			activity_type=activity_dict[const.ACTIVITY_TYPE],
			mistake_hints=mistake_hint_list,
			steps=step_list,
			required_items=activity_dict[const.REQUIRED_ITEMS]
		)
	
	@classmethod
	def from_yaml_dict(cls, activity_yaml_dict) -> "Activity":
		step_list = []
		for step_dict in activity_yaml_dict[const.STEPS]:
			step_list.append(Step.from_dict(step_dict))
		
		# TODO: Update these for final ones
		mistake_hint_list = []
		for mistake_dict in activity_yaml_dict[const.MISTAKE_HINTS]:
			# mistake_dict[const.TAG] = MistakeTag.get_best_tag(mistake_dict[const.TAG])
			mistake_hint_list.append(Mistake.from_dict(mistake_dict))
		
		return cls(
			id=activity_yaml_dict[const.ID],
			name=activity_yaml_dict[const.NAME],
			category=activity_yaml_dict[const.CATEGORY],
			activity_type=activity_yaml_dict[const.ACTIVITY_TYPE],
			mistake_hints=mistake_hint_list,
			steps=step_list,
			required_items=activity_yaml_dict[const.REQUIRED_ITEMS]
		)
