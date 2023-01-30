class Recording:

	def __init__(self, recipe, kitchen_id, person_id, rec_number):
		self.recipe = recipe
		self.kitchen_id = kitchen_id
		self.person_id = person_id
		self.rec_number = rec_number

	def setCurrentStepId(self, step_id):
		self.current_step_id = step_id

