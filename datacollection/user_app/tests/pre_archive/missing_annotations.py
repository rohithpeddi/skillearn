from datacollection.user_app.backend.app.models.annotation import Annotation
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def fetch_missing_annotations():
	# Fetch all ids for recorded videos
	recordings_dict = dict(db_service.fetch_all_recordings())
	recording_list = []
	for recording_id, recording_dict in recordings_dict.items():
		recording_list.append(Recording.from_dict(recording_dict))
	
	all_recordings = set()
	for recording in recording_list:
		if recording.recorded_by is not None and recording.recorded_by != -1:
			all_recordings.add(recording.id)
	
	# Fetch all ids for annotated videos
	annotation_dict_list = dict(db_service.fetch_annotations())
	annotation_list = []
	for annotation_id, annotation_dict in annotation_dict_list.items():
		annotation_list.append(Annotation.from_dict(annotation_dict))
	
	annotated_recordings = set()
	for annotation in annotation_list:
		annotated_recordings.add(annotation.annotation_id[:-2])
	
	# Find missing annotations
	missing_annotations = all_recordings - annotated_recordings
	print(f"Missing annotations: {missing_annotations}")


if __name__ == "__main__":
	db_service = FirebaseService()
	fetch_missing_annotations()
