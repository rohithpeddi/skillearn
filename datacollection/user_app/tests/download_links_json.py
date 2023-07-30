import json
import os

from datacollection.user_app.backend.app.models.recording_summary import RecordingSummary
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def prepare_download_links_json(version):
	recording_download_links_dict = {}
	recording_summary_dict_list = dict(db_service.fetch_recording_summaries())
	for index, (recording_id, recording_summary_dict) in enumerate(recording_summary_dict_list.items()):
		recording_summary = RecordingSummary.from_dict(recording_summary_dict)
		recording_download_links_dict[recording_summary.recording_id] = recording_summary.download_links.to_dict()
	
	current_directory = os.getcwd()
	website_directory = os.path.join(current_directory, "../backend/website_files")
	if not os.path.exists(website_directory):
		os.makedirs(website_directory)
	
	with open(os.path.join(website_directory, f"recording_download_links_{version}.json"), "w") as recording_download_links_file:
		recording_download_links_file.write(json.dumps(recording_download_links_dict))


if __name__ == "__main__":
	db_service = FirebaseService()
	prepare_download_links_json(version=4)
