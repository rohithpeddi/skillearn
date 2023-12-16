import os

from datacollection.user_app.backend.app.models.recording_summary import RecordingSummary
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService

import csv


def generate_csv_from_list_of_dicts(data, filename):
    # Extract the keys from the first dictionary to use as CSV header
    header = data[0].keys()

    # Open a CSV file in write mode
    with open(filename, 'w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.DictWriter(csvfile, fieldnames=header)

        # Write the header row to the CSV file
        writer.writeheader()

        # Write each dictionary as a row in the CSV file
        for row in data:
            writer.writerow(row)


def generate_video_info_csv():
    video_info_dict_list = []
    recording_summary_dict_list = dict(db_service.fetch_recording_summaries())
    for index, (recording_id, recording_summary_dict) in enumerate(recording_summary_dict_list.items()):
        recording_summary = RecordingSummary.from_dict(recording_summary_dict)

        video_info_dict = {
            "recording_id": recording_id,
            "environment_id": recording_summary.recording.environment,
            "person_id": recording_summary.recording.selected_by,
            "duration(min)": round(recording_summary.duration, 2),
        }

        video_info_dict_list.append(video_info_dict)

    current_directory = os.getcwd()
    website_directory = os.path.join(current_directory, "../backend/website_files")
    if not os.path.exists(website_directory):
        os.makedirs(website_directory)

    output_file_path = os.path.join(website_directory, "video_info.csv")
    generate_csv_from_list_of_dicts(video_info_dict_list, output_file_path)


if __name__ == "__main__":
    db_service = FirebaseService()
    box_service = BoxService()
    generate_video_info_csv()
