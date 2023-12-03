import yaml

from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def fetch_user_environment_recordings(user_id, environment):
    user_recordings = db_service.fetch_user_recordings(user_id)
    environment_recordings_dict = []

    for recording_id, recording_dict in user_recordings.items():
        if recording_dict['environment'] == environment:
            environment_recordings_dict.append(recording_dict)

    with open(f"../backend/info_files/user_environment_recordings/user_{user_id}_env_{environment}.yaml",
              'w') as yaml_file:
        yaml.dump(environment_recordings_dict, yaml_file)


def fetch_user_environment_selections(user_id, environment):
    user_recordings = db_service.fetch_user_selections(user_id)
    environment_recordings_dict = []

    for recording_id, recording_dict in user_recordings.items():
        if recording_dict['environment'] == environment:
            environment_recordings_dict.append(recording_dict)

    with open(f"../backend/info_files/user_environment_selections/user_selections_{user_id}_env_{environment}.yaml",
              'w') as yaml_file:
        yaml.dump(environment_recordings_dict, yaml_file)


if __name__ == '__main__':
    db_service = FirebaseService()
    # fetch_user_environment_recordings(3, 6)
    fetch_user_environment_selections(1, 6)
