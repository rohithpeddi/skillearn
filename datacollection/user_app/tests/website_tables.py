import os

from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.recording_summary import RecordingSummary
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def fetch_activity_name(activity_id):
	return activity_id_name_map[activity_id]


def get_symbol_for_status(status):
	if status is not None and status:
		return f"<td><i class=\"fas fa-check\" style=\"color: #2eaf2c;\"></i></td>\n"
	else:
		return f"<td><i class=\"fas fa-times\" style=\"color: #d30d0d;\"></i></td>\n"


def make_overview_table():
	overview_table = ""
	overview_table += "<div class=\"columns is-centered\">\n"
	overview_table += "<div class=\"column is-fullwidth\">\n"
	overview_table += "<h3 class=\"title is-4\">Overview</h3>\n"
	overview_table += "<div class=\"table-container is-centered\">\n"
	overview_table += "<table class=\"table is-striped is-fullwidth is-hoverable\">\n"
	overview_table += "<thead>\n"
	overview_table += "<tr>\n"
	overview_table += "<th>S.No</th>\n"
	overview_table += "<th>Recipe Name</th>\n"
	overview_table += "<th>Recording Id</th>\n"
	overview_table += "<th>Person Id</th>\n"
	overview_table += "<th>Environment Id</th>\n"
	overview_table += "<th>Video GoPro</th>\n"
	overview_table += "<th>Video Hololens</th>\n"
	overview_table += "<th>Depth</th>\n"
	overview_table += "<th>Spatial</th>\n"
	overview_table += "<th>Audio</th>\n"
	overview_table += "</tr>\n"
	overview_table += "</thead>\n"
	overview_table += "<tbody>\n"
	
	recording_summary_dict_list = dict(db_service.fetch_recording_summaries())
	for index, (recording_id, recording_summary_dict) in enumerate(recording_summary_dict_list.items()):
		recording_summary = RecordingSummary.from_dict(recording_summary_dict)
		overview_table += "<tr>\n"
		overview_table += f"<th>{index + 1}</th>\n"
		overview_table += f"<td>{fetch_activity_name(recording_summary.recording.activity_id)}</td>\n"
		overview_table += f"<td>{recording_summary.recording_id}</td>\n"
		overview_table += f"<td>{recording_summary.recording.selected_by}</td>\n"
		overview_table += f"<td>{recording_summary.recording.environment}</td>\n"
		
		overview_table += get_symbol_for_status(recording_summary.download_links.GOPRO_RESOLUTION_360p)
		overview_table += get_symbol_for_status(recording_summary.is_hololens_enabled)
		overview_table += get_symbol_for_status(recording_summary.is_hololens_enabled)
		overview_table += get_symbol_for_status(recording_summary.is_spatial_enabled)
		overview_table += get_symbol_for_status(True)
	
	overview_table += "</tbody>\n"
	overview_table += "</table>\n"
	overview_table += "</div>\n"
	overview_table += "</div>\n"
	overview_table += "</div>\n"
	
	current_directory = os.getcwd()
	website_directory = os.path.join(current_directory, "../backend/website_files")
	if not os.path.exists(website_directory):
		os.makedirs(website_directory)
	
	with open(os.path.join(website_directory, "overview_table.html"), "w") as f:
		f.write(overview_table)
	
	return overview_table


def make_recipe_table():
	recipe_table = ""
	recipe_table += "<div class=\"columns is-centered\">\n"
	recipe_table += "<div class=\"column is-fullwidth\">\n"
	recipe_table += "<h3 class=\"title is-4\">Recipe Information</h3>\n"
	recipe_table += "<div class=\"table-container is-centered\">\n"
	recipe_table += "<table class=\"table is-striped is-fullwidth is-hoverable\">\n"
	recipe_table += "<thead>\n"
	recipe_table += "<tr>\n"
	recipe_table += "<th>S.No</th>\n"
	recipe_table += "<th>Recipe Name</th>\n"
	recipe_table += "<th>Heating Type</th>\n"
	recipe_table += "<th>Recipe Text</th>\n"
	recipe_table += "</tr>\n"
	recipe_table += "</thead>\n"
	recipe_table += "<tbody>\n"
	
	for index, activity in enumerate(activities):
		recipe_table += "<tr>\n"
		recipe_table += f"<th>{index + 1}</th>\n"
		recipe_table += f"<td>{activity.name}</td>\n"
		recipe_table += f"<td>{activity.activity_type}</td>\n"
		
		recipe_text = ""
		for step in activity.steps:
			recipe_text += f"{step.description} "
		
		recipe_table += f"<td>{recipe_text}</td>\n"
		recipe_table += "</tr>\n"
	
	recipe_table += "</tbody>\n"
	recipe_table += "</table>\n"
	recipe_table += "</div>\n"
	recipe_table += "</div>\n"
	recipe_table += "</div>\n"
	
	current_directory = os.getcwd()
	website_directory = os.path.join(current_directory, "../backend/website_files")
	if not os.path.exists(website_directory):
		os.makedirs(website_directory)
	
	with open(os.path.join(website_directory, "recipe_table.html"), "w") as f:
		f.write(recipe_table)
	
	return recipe_table


def make_data_2d_table():
	data2d_table = ""
	data2d_table += "<div class=\"columns is-centered\">\n"
	data2d_table += "<div class=\"column is-fullwidth\">\n"
	data2d_table += "<h3 class=\"title is-4\">2D Data</h3>\n"
	data2d_table += "<div class=\"table-container is-centered\">\n"
	data2d_table += "<table class=\"table is-striped is-fullwidth is-hoverable\">\n"
	data2d_table += "<thead>\n"
	data2d_table += "<tr>\n"
	data2d_table += "<th>S.No</th>\n"
	data2d_table += "<th>Recipe Name</th>\n"
	data2d_table += "<th>Recording Id</th>\n"
	data2d_table += "<th>Person Id</th>\n"
	data2d_table += "<th>Environment Id</th>\n"
	data2d_table += "<th>GoPro</th>\n"
	data2d_table += "<th>Hololens</th>\n"
	data2d_table += "<th>Annotation</th>\n"
	data2d_table += "</tr>\n"
	data2d_table += "</thead>\n"
	data2d_table += "<tbody>\n"
	
	recording_summary_dict_list = dict(db_service.fetch_recording_summaries())
	for index, (recording_id, recording_summary_dict) in enumerate(recording_summary_dict_list.items()):
		recording_summary = RecordingSummary.from_dict(recording_summary_dict)
		data2d_table += "<tr>\n"
		data2d_table += f"<th>{index + 1}</th>\n"
		data2d_table += f"<td>{fetch_activity_name(recording_summary.recording.activity_id)}</td>\n"
		data2d_table += f"<td>{recording_summary.recording_id}</td>\n"
		data2d_table += f"<td>{recording_summary.recording.selected_by}</td>\n"
		data2d_table += f"<td>{recording_summary.recording.environment}</td>\n"
		
		if recording_summary.download_links.GOPRO_RESOLUTION_360p is None:
			data2d_table += "<td><i class=\"fas fa-times\"></i></td>\n"
		else:
			data2d_table += f"<td><button class=\"hoverable-button\"><a href=\"{recording_summary.download_links.GOPRO_RESOLUTION_360p}\">360p</a></button> <button class=\"hoverable-button\"> <a href=\"{recording_summary.download_links.GOPRO_RESOLUTION_4k}\">4K</a></button></td>\n"
		
		if not recording_summary.is_hololens_enabled:
			data2d_table += "<td><i class=\"fas fa-times\"></i></td>\n"
		else:
			if recording_summary.download_links.HOLOLENS_SYNC_PV_VIDEO is None:
				data2d_table += "<td><i class=\"fas fa-spinner fa-spin\" style=\"color: #10ad13;\"></i></td>\n"
			else:
				data2d_table += f"<td><button class=\"hoverable-button\"><a href=\"{recording_summary.download_links.HOLOLENS_SYNC_PV_VIDEO}\">360p</a></button></td>\n"
		
		data2d_table += get_symbol_for_status(True)
	
	data2d_table += "</tbody>\n"
	data2d_table += "</table>\n"
	data2d_table += "</div>\n"
	data2d_table += "</div>\n"
	data2d_table += "</div>\n"
	
	current_directory = os.getcwd()
	website_directory = os.path.join(current_directory, "../backend/website_files")
	if not os.path.exists(website_directory):
		os.makedirs(website_directory)
	
	with open(os.path.join(website_directory, "data2d_table.html"), "w") as f:
		f.write(data2d_table)
	
	return data2d_table


def make_data3d_table():
	data3d_table = ""
	data3d_table += "<div class=\"columns is-centered\">\n"
	data3d_table += "<div class=\"column is-fullwidth\">\n"
	data3d_table += "<h3 class=\"title is-4\">3D Data</h3>\n"
	data3d_table += "<div class=\"table-container is-centered\">\n"
	data3d_table += "<table class=\"table is-striped is-fullwidth is-hoverable\">\n"
	data3d_table += "<thead>\n"
	data3d_table += "<tr>\n"
	data3d_table += "<th>S.No</th>\n"
	data3d_table += "<th>Recipe Name</th>\n"
	data3d_table += "<th>Recording Id</th>\n"
	data3d_table += "<th>Person Id</th>\n"
	data3d_table += "<th>Environment Id</th>\n"
	data3d_table += "<th>Depth</th>\n"
	data3d_table += "<th>Spatial</th>\n"
	data3d_table += "<th>IMU</th>\n"
	data3d_table += "</tr>\n"
	data3d_table += "</thead>\n"
	data3d_table += "<tbody>\n"
	
	recording_summary_dict_list = dict(db_service.fetch_recording_summaries())
	for index, (recording_id, recording_summary_dict) in enumerate(recording_summary_dict_list.items()):
		recording_summary = RecordingSummary.from_dict(recording_summary_dict)
		data3d_table += "<tr>\n"
		data3d_table += f"<th>{index + 1}</th>\n"
		data3d_table += f"<td>{fetch_activity_name(recording_summary.recording.activity_id)}</td>\n"
		data3d_table += f"<td>{recording_summary.recording_id}</td>\n"
		data3d_table += f"<td>{recording_summary.recording.selected_by}</td>\n"
		data3d_table += f"<td>{recording_summary.recording.environment}</td>\n"
		
		if not recording_summary.is_hololens_enabled:
			data3d_table += "<td><i class=\"fas fa-times\"></i></td>\n"
		else:
			if recording_summary.download_links.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP is None:
				data3d_table += "<td><i class=\"fas fa-spinner fa-spin\" style=\"color: #10ad13;\"></i></td>\n"
			else:
				data3d_table += f"<td><button class=\"hoverable-button\"><a href=\"{recording_summary.download_links.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP}\">Depth</a></button> <button class=\"hoverable-button\"> <a href=\"{recording_summary.download_links.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP}\">AB</a></button></td>\n"
		
		if not (recording_summary.is_hololens_enabled and recording_summary.is_spatial_enabled):
			data3d_table += "<td><i class=\"fas fa-times\"></i></td>\n"
		else:
			if recording_summary.download_links.HOLOLENS_SYNC_SPATIAL_PKL is None:
				data3d_table += "<td><i class=\"fas fa-spinner fa-spin\" style=\"color: #10ad13;\"></i></td>\n"
			else:
				data3d_table += f"<td><button class=\"hoverable-button\"><a href=\"{recording_summary.download_links.HOLOLENS_SYNC_SPATIAL_PKL}\">Spatial</a></button></td>\n"
		
		if not (recording_summary.is_hololens_enabled and recording_summary.is_spatial_enabled):
			data3d_table += "<td><i class=\"fas fa-times\"></i></td>\n"
		else:
			if recording_summary.download_links.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL is None:
				data3d_table += "<td><i class=\"fas fa-spinner fa-spin\" style=\"color: #10ad13;\"></i></td>\n"
			else:
				data3d_table += f"<td><button class=\"hoverable-button\"><a href=\"{recording_summary.download_links.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL}\">Mag</a></button> " \
				                f"<button class=\"hoverable-button\"> <a href=\"{recording_summary.download_links.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL}\">Gyr</a></button> " \
				                f"<button class=\"hoverable-button\"> <a href=\"{recording_summary.download_links.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL}\">Acc</a></button></td>\n"
	
	data3d_table += "</tbody>\n"
	data3d_table += "</table>\n"
	data3d_table += "</div>\n"
	data3d_table += "</div>\n"
	data3d_table += "</div>\n"
	
	current_directory = os.getcwd()
	website_directory = os.path.join(current_directory, "../backend/website_files")
	if not os.path.exists(website_directory):
		os.makedirs(website_directory)
	
	with open(os.path.join(website_directory, "data3d_table.html"), "w") as f:
		f.write(data3d_table)
	
	return data3d_table


if __name__ == '__main__':
	db_service = FirebaseService()
	
	activity_id_name_map = {}
	activities = [
		Activity.from_dict(activity_dict)
		for activity_dict in db_service.fetch_activities()
		if activity_dict is not None
	]
	for activity in activities:
		activity_id_name_map[activity.id] = activity.name
	
	# make_overview_table()
	# make_recipe_table()
	make_data_2d_table()
	make_data3d_table()
