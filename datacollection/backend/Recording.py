class Recording:

	def __init__(self, activity, place_id, person_id, rec_number, is_error=False):
		self.activity = activity
		self.place_id = place_id
		self.person_id = person_id
		self.rec_number = rec_number
		self.is_error = is_error

	def set_current_step_id(self, step_id):
		self.current_step_id = step_id

	def set_device_ip(self, device_ip):
		self.device_ip = device_ip
		
	def get_recording_id(self):
		return f'{self.activity}_{self.place_id}_{self.person_id}_{self.rec_number}_{self.is_error}'
		
	def __str__(self):
		return f'Activity: {self.activity}, Place: {self.place_id}, Person: {self.person_id}, Recording Number: {self.rec_number}'
