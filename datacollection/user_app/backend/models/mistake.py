from typing import Optional

from datacollection.user_app.backend.constants import *


class Mistake:
	
	def __init__(
			self,
			tag: str,
			description: Optional[str] = None
	):
		self.tag = tag
		self.description = description
		
	def to_dict(self) -> dict:
		mistake_dict = {TAG: self.tag}
		
		if self.description:
			mistake_dict[DESCRIPTION] = self.description
			
		return mistake_dict
	
	@classmethod
	def from_dict(cls, mistake_dict) -> "Mistake":
		mistake = cls(mistake_dict[TAG])
		
		if DESCRIPTION in mistake_dict:
			mistake.description = mistake_dict[DESCRIPTION]
			
		return mistake
