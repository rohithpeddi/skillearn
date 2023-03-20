from typing import List

from datacollection.user_app.backend.constants import *
from datacollection.user_app.backend.models.mistake import Mistake
from datacollection.user_app.backend.models.mistake_tag import MistakeTag
from datacollection.user_app.backend.models.step import Step


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
			ID: self.id,
			NAME: self.name,
			CATEGORY: self.category,
			ACTIVITY_TYPE: self.activity_type,
			REQUIRED_ITEMS: self.required_items
		}
		
		step_dict_list = []
		for step in self.steps:
			step_dict_list.append(step.to_dict())
		activity_dict[STEPS] = step_dict_list
		
		mistake_dict_list = []
		for mistake in self.mistake_hints:
			mistake_dict_list.append(mistake.to_dict())
		activity_dict[MISTAKE_HINTS] = mistake_dict_list
		
		return activity_dict
	
	@classmethod
	def from_dict(cls, activity_dict: dict) -> "Activity":
		step_list = []
		for step_dict in activity_dict[STEPS]:
			step_list.append(Step.from_dict(step_dict))
		
		mistake_hint_list = []
		for mistake_dict in activity_dict[MISTAKE_HINTS]:
			mistake_hint_list.append(Mistake.from_dict(mistake_dict))
		
		return cls(
			id=activity_dict[ID],
			name=activity_dict[NAME],
			category=activity_dict[CATEGORY],
			activity_type=activity_dict[ACTIVITY_TYPE],
			mistake_hints=mistake_hint_list,
			steps=step_list,
			required_items=activity_dict[REQUIRED_ITEMS]
		)
	
	@classmethod
	def from_yaml_dict(cls, activity_yaml_dict) -> "Activity":
		step_list = []
		for step_dict in activity_yaml_dict[STEPS]:
			step_list.append(Step.from_dict(step_dict))
		
		mistake_hint_list = []
		for mistake_dict in activity_yaml_dict[MISTAKE_HINTS]:
			mistake_dict[TAG] = MistakeTag.get_best_tag(mistake_dict[TAG])
			mistake_hint_list.append(Mistake.from_dict(mistake_dict))
		
		return cls(
			id=activity_yaml_dict[ID],
			name=activity_yaml_dict[NAME],
			category=activity_yaml_dict[CATEGORY],
			activity_type=activity_yaml_dict[ACTIVITY_TYPE],
			mistake_hints=mistake_hint_list,
			steps=step_list,
			required_items=activity_yaml_dict[REQUIRED_ITEMS]
		)
