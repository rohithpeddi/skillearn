from datacollection.user_app.backend.app.services.firebase_service import FirebaseService

# first goto env_setup folder and run ./create_venv.sh
# run command:    python3 get_annotations.py

if __name__ == "__main__":
    db_service = FirebaseService()
    fetched_recording_details = db_service.fetch_recording('6_46')
    step_array = [{'step_number': i, 'modified_description': s['modified_description']}
                  for i, s in enumerate(fetched_recording_details['steps'])]
    print(step_array)
