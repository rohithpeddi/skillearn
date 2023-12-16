import json
from typing import List
from ..models.step_annotation import StepAnnotation

from ..utils.constants import Recording_Constants as const


class RecordingAnnotation:
	
	def __init__(
			self,
			recording_id: str,
			activity_id: int,
			is_error: bool,
			step_annotations: List[StepAnnotation],
	):
		self.recording_id = recording_id
		self.activity_id = activity_id
		self.is_error = is_error
		self.step_annotations = step_annotations
		
	def __str__(self):
		return json.dumps(self.to_dict())
	
	def to_dict(self):
		recording_annotation_dict = {const.RECORDING_ID: self.recording_id, const.ACTIVITY_ID: self.activity_id, const.IS_ERROR: self.is_error}
		
		step_annotations_dict_list = []
		for step_annotation in self.step_annotations:
			step_annotations_dict_list.append(step_annotation.to_dict())
		
		recording_annotation_dict[const.STEP_ANNOTATIONS] = step_annotations_dict_list
		return recording_annotation_dict
	
	@classmethod
	def from_dict(cls, recording_dict) -> "RecordingAnnotation":
		step_annotations_list = []
		for step_annotation_dict in recording_dict[const.STEP_ANNOTATIONS]:
			step_annotation = StepAnnotation.from_dict(step_annotation_dict)
			step_annotations_list.append(step_annotation)
			
		recording_annotation = cls(recording_dict[const.RECORDING_ID], recording_dict[const.ACTIVITY_ID], recording_dict[const.IS_ERROR], step_annotations_list)
		return recording_annotation
	
		
