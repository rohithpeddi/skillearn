import json
import os

from datacollection.user_app.backend.app.models.recording_annotation import RecordingAnnotation
from datacollection.user_app.backend.app.models.recording_summary import RecordingSummary
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def prepare_download_links_json(version):
	recording_annotation_list_dict = dict(db_service.fetch_recording_annotations())
	recording_annotations = [
		RecordingAnnotation.from_dict(recording_annotation_dict) for recording_id, recording_annotation_dict in
		recording_annotation_list_dict.items() if recording_annotation_dict is not None
	]
	recording_annotations = sorted(
		recording_annotations,
		key=lambda x: (int(x.activity_id), int(x.recording_id.split("_")[1]))
	)
	
	valid_recording_ids = []
	for recording_annotation in recording_annotations:
		valid_recording_ids.append(recording_annotation.recording_id)
	
	recording_download_links_dict = {}
	recording_summary_dict_list = dict(db_service.fetch_recording_summaries())
	for index, (recording_id, recording_summary_dict) in enumerate(recording_summary_dict_list.items()):
		if recording_id not in valid_recording_ids:
			print(f"Recording {recording_id} is not valid. Skipping...")
			continue
		else:
			print(f"Recording {recording_id} is valid. Adding to list...")
		recording_summary = RecordingSummary.from_dict(recording_summary_dict)
		recording_download_links_dict[recording_summary.recording_id] = recording_summary_dict["download_links"]
	
	current_directory = os.getcwd()
	website_directory = os.path.join(current_directory, "../backend/website_files")
	if not os.path.exists(website_directory):
		os.makedirs(website_directory)
	
	with open(os.path.join(website_directory, f"recording_download_links_{version}.json"), "w") as recording_download_links_file:
		recording_download_links_file.write(json.dumps(recording_download_links_dict))


if __name__ == "__main__":
	db_service = FirebaseService()
	prepare_download_links_json(version=15)
