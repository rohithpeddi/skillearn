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
