from typing import Optional

from datacollection.user_app.backend.constants import Recording_Constants as const


class Error:
	
	def __init__(
			self,
			tag: str,
			description: Optional[str] = None
	):
		self.tag = tag
		self.description = description
	
	def to_dict(self) -> dict:
		error_dict = {const.TAG: self.tag}
		
		if self.description:
			error_dict[const.DESCRIPTION] = self.description
		
		return error_dict
	
	@classmethod
	def from_dict(cls, error_dict) -> "Error":
		error = cls(error_dict[const.TAG])
		
		if const.DESCRIPTION in error_dict:
			error.description = error_dict[const.DESCRIPTION]
		
		return error