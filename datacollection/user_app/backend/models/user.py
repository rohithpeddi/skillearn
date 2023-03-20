import random
from typing import List
from datacollection.user_app.backend.constants import *
from datacollection.user_app.backend.logger_config import logger
from datacollection.user_app.backend.models.schedule import Schedule


class User:
	
	def __init__(self, id, username):
		self.id = id
		self.username = username
		
		self.activity_preferences = []
		self.recording_schedules = []
	
	def update_preferences(self, activity_list: List[int]):
		self.activity_preferences.extend(activity_list)
	
	def update_recording(self, environment: int, recording_id):
		try:
			environment_schedule = self.recording_schedules[environment]
			environment_schedule.update_recorded(recording_id)
		except IndexError:
			logger.error("Current environment schedule is not created")
			raise Exception("Current environment schedule is not created")
	
	def update_environment_schedule(self, environment: int):
		# Create/Update a schedule for this environment
		if len(self.activity_preferences) == 0:
			logger.error("Preferences are not set - set preferences first")
			raise Exception("Preferences are not set - set preferences first")
		
		# Create a list of all activities based on preferences in round robin fashion
		def duplicate_list(original_list, length):
			duplicated_list = original_list.copy()
			while len(duplicated_list) < length:
				duplicated_list.extend(original_list)
			return duplicated_list
		
		all_environment_activities = duplicate_list(self.activity_preferences,
		                                            TOTAL_ENVIRONMENTS * ACTIVITIES_PER_PERSON_PER_ENV)
		current_environment_activities = all_environment_activities[
		                                 ACTIVITIES_PER_PERSON_PER_ENV * environment: ACTIVITIES_PER_PERSON_PER_ENV * (
				                                 environment + 1)]
		
		# Create a schedule and update in the requested environment position
		environment_normal_recordings = []
		environment_mistake_recordings = []
		for idx, activity_id in enumerate(current_environment_activities):
			# For normal recordings
			if idx < 5:
				random_int = random.randint(1, 25)
				environment_normal_recordings.append(int(f'{activity_id}_{random_int}'))
			else:
				random_int = random.randint(25, 50)
				environment_mistake_recordings.append(int(f'{activity_id}_{random_int}'))
		
		schedule = Schedule(environment, environment_normal_recordings, environment_mistake_recordings)
		
		if environment < len(self.recording_schedules):
			self.recording_schedules[environment] = schedule
		else:
			for missing_environment in range(len(self.recording_schedules), environment + 1):
				self.update_environment_schedule(missing_environment)
	
	def build_all_environment_schedules(self):
		for missing_environment in range(1, TOTAL_ENVIRONMENTS + 1):
			self.update_environment_schedule(missing_environment)
	
	def to_dict(self) -> dict:
		user_dict = {ID: self.id, USERNAME: self.username}
		
		if len(self.activity_preferences) > 0:
			user_dict[ACTIVITY_PREFERENCES] = self.activity_preferences
		
		if len(self.recording_schedules) > 0:
			user_dict[RECORDING_SCHEDULES] = [recording_schedule.to_dict() for recording_schedule in
			                                  self.recording_schedules]
		
		return user_dict
	
	@classmethod
	def from_dict(cls, user_dict) -> "User":
		user = User(user_dict[ID], user_dict[USERNAME])
		
		if ACTIVITY_PREFERENCES in user_dict:
			user.activity_preferences = user_dict[ACTIVITY_PREFERENCES]
		
		if RECORDING_SCHEDULES in user_dict:
			recording_schedules_dict_list = user_dict[RECORDING_SCHEDULES]
			for schedule_dict in recording_schedules_dict_list:
				schedule = Schedule()
				schedule.from_dict(schedule_dict)
				user.recording_schedules.append(schedule)
		
		return user
