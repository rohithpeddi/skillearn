import sys
import os.path as osp

from datacollection.user_app.backend.app.models.recording_annotation import RecordingAnnotation
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


def initialize_paths():
	this_dir = osp.dirname(__file__)
	
	lib_path = osp.join(this_dir, "../../datacollection")
	add_path(lib_path)


initialize_paths()


def main():
	for recording_annotation in recording_annotations:
		print(f"Recording {recording_annotation.recording_id}")
		step_annotations = recording_annotation.step_annotations
		for step_annotation in step_annotations:
			if step_annotation.start_time == -1.0 or step_annotation.end_time == -1.0:
				step_errors = step_annotation.errors
				if len(step_errors) == 0:
					print(
						f"Recording {recording_annotation.recording_id} has no errors, but step annotation has no start or end time")
				else:
					for error in step_errors:
						if error.tag == "Missing Step":
							continue
						else:
							print(
								f"Recording {recording_annotation.recording_id} has error {error.tag}, but step annotation has no start or end time")
							print(f"-----------------------------------------------------")


if __name__ == '__main__':
	db_service = FirebaseService()
	recording_annotation_list_dict = dict(db_service.fetch_recording_annotations())
	recording_annotations = [
		RecordingAnnotation.from_dict(recording_annotation_dict) for recording_id, recording_annotation_dict in
		recording_annotation_list_dict.items() if recording_annotation_dict is not None
	]
	recording_annotations = sorted(
		recording_annotations,
		key=lambda x: (int(x.activity_id), int(x.recording_id.split("_")[1]))
	)
	
	main()
