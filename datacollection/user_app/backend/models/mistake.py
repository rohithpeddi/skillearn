from typing import Optional

from datacollection.user_app.backend.constants import Recording_Constants as const


class Mistake:
	
	def __init__(
			self,
			tag: str,
			description: Optional[str] = None
	):
		self.tag = tag
		self.description = description
	
	def to_dict(self) -> dict:
		mistake_dict = {const.TAG: self.tag}
		
		if self.description:
			mistake_dict[const.DESCRIPTION] = self.description
		
		return mistake_dict
	
	@classmethod
	def from_dict(cls, mistake_dict) -> "Mistake":
		mistake = cls(mistake_dict[const.TAG])
		
		if const.DESCRIPTION in mistake_dict:
			mistake.description = mistake_dict[const.DESCRIPTION]
		
		return mistake
