import json

from ..models.error import Error
from ..utils.constants import Recording_Constants as const


class StepAnnotation:
	
	def __init__(
			self,
			step_id: int,
			description: str,
	):
		self.step_id = step_id
		self.description = description
		self.errors = []
		self.start_time = -1.0
		self.end_time = -1.0
		self.modified_description = None
	
	def update_errors(self, step_errors):
		self.errors.extend(step_errors)
	
	def to_dict(self) -> dict:
		step_annotation_dict = {const.DESCRIPTION: self.description, const.STEP_ID: self.step_id}
		
		if len(self.errors) > 0:
			step_error_dict_list = []
			for step_error in self.errors:
				step_error_dict_list.append(step_error.to_dict())
			step_annotation_dict[const.ERRORS] = step_error_dict_list
		
		if self.start_time is not None:
			step_annotation_dict[const.START_TIME] = self.start_time
		
		if self.end_time is not None:
			step_annotation_dict[const.END_TIME] = self.end_time
		
		if self.modified_description is not None:
			step_annotation_dict[const.MODIFIED_DESCRIPTION] = self.modified_description
		
		return step_annotation_dict
	
	@classmethod
	def from_dict(cls, step_dict) -> "StepAnnotation":
		step_annotation = cls(step_dict[const.STEP_ID], step_dict[const.DESCRIPTION])
		
		if const.ERRORS in step_dict:
			step_errors_list = []
			for step_error_dict in step_dict[const.ERRORS]:
				step_error = Error.from_dict(step_error_dict)
				step_errors_list.append(step_error)
			step_annotation.errors = step_errors_list
		
		if const.START_TIME in step_dict:
			step_annotation.start_time = step_dict[const.START_TIME]
		
		if const.END_TIME in step_dict:
			step_annotation.end_time = step_dict[const.END_TIME]
		
		if const.MODIFIED_DESCRIPTION in step_dict:
			step_annotation.modified_description = step_dict[const.MODIFIED_DESCRIPTION]
		
		return step_annotation
	
	def __str__(self):
		return json.dumps(self.to_dict())
