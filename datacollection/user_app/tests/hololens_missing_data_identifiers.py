import json
import os

from datacollection.user_app.backend.app.utils.constants import Recording_Constants as const


def fetch_current_downloadable_recording_ids():
	with open(download_links_json_file_path, "r") as f:
		download_links = json.load(f)
	
	downloadable_recording_ids = []
	for recording_id, recording_download_link_dict in download_links.items():
		if const.HOLOLENS_SYNC_PV_VIDEO in recording_download_link_dict:
			if recording_download_link_dict[const.HOLOLENS_SYNC_PV_VIDEO] is not None:
				downloadable_recording_ids.append(recording_id)
	
	return downloadable_recording_ids


def fetch_current_hololens_recording_ids():
	current_hololens_recording_ids = []
	for recording_id_directory_name in os.listdir(current_hololens_data_path):
		if os.path.isdir(os.path.join(current_hololens_data_path, recording_id_directory_name)):
			current_hololens_recording_ids.append(recording_id_directory_name)
	
	return current_hololens_recording_ids


def main():
	downloadable_recording_ids = fetch_current_downloadable_recording_ids()
	current_hololens_recording_ids = fetch_current_hololens_recording_ids()
	
	missing_recording_ids = list(set(downloadable_recording_ids) - set(current_hololens_recording_ids))
	print(f"Number of missing recording ids: {len(missing_recording_ids)}")
	print(f"Missing recording ids: {missing_recording_ids}")


if __name__ == "__main__":
	download_links_json_file_path = "../backend/download_links_jsons/download_links.json"
	current_hololens_data_path = "../backend/download_links_jsons/current_hololens.json"
	main()
