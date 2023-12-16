import json
import os

from datacollection.user_app.backend.app.utils.constants import Recording_Constants as const


def fetch_hololens_box_recording_ids():
    with open(download_links_json_file_path, "r") as f:
        download_links = json.load(f)

    downloadable_recording_ids = []
    for recording_id, recording_download_link_dict in download_links.items():
        if const.HOLOLENS_SYNC_PV_VIDEO in recording_download_link_dict:
            if recording_download_link_dict[const.HOLOLENS_SYNC_PV_VIDEO] is not None:
                downloadable_recording_ids.append(recording_id)

    return downloadable_recording_ids


def fetch_hololens_recording_ids(hololens_data_path):
    current_hololens_recording_ids = []
    for recording_id_directory_name in os.listdir(hololens_data_path):
        if os.path.isdir(os.path.join(hololens_data_path, recording_id_directory_name)):
            current_hololens_recording_ids.append(recording_id_directory_name)

    return current_hololens_recording_ids


def fetch_hololens_nas_recording_ids(hololens_data_path):
    current_hololens_recording_ids = []
    for recording_id_directory_name in os.listdir(hololens_data_path):
        if os.path.isdir(os.path.join(hololens_data_path, recording_id_directory_name)):
            hololens_recording_data_path = os.path.join(hololens_data_path, recording_id_directory_name)
            sub_directories = os.listdir(hololens_recording_data_path)
            # print(f"Recording {recording_id_directory_name} has sub directories: {sub_directories}")
            if "sync" in sub_directories:
                if len(os.listdir(os.path.join(hololens_recording_data_path, "sync"))) > 0:
                    current_hololens_recording_ids.append(recording_id_directory_name)
                else:
                    # print(f"Recording {recording_id_directory_name} has empty sync folder. Skipping...")
                    pass
    return current_hololens_recording_ids


def check_recording_ids_difference_box_local():
    downloadable_recording_ids = fetch_hololens_box_recording_ids()
    current_hololens_recording_ids = fetch_hololens_recording_ids(local_hololens_data_path)

    missing_recording_ids = list(set(downloadable_recording_ids) ^ set(current_hololens_recording_ids))
    print(" ---------------- BOX - LOCAL ---------------- ")
    print(f"Number of box recording ids: {len(downloadable_recording_ids)}")
    print(f"Number of local recording ids: {len(current_hololens_recording_ids)}")
    print(f"Number of missing recording ids: {len(missing_recording_ids)}")
    print(f"Missing recording ids: {missing_recording_ids}")


def check_recording_ids_difference_nas_local():
    nas_recording_ids = fetch_hololens_nas_recording_ids(nas_hololens_data_path)
    current_hololens_recording_ids = fetch_hololens_recording_ids(local_hololens_data_path)

    missing_recording_ids = list(set(nas_recording_ids) ^ set(current_hololens_recording_ids))
    print(" ---------------- NAS - LOCAL ---------------- ")
    print(f"Number of NAS recording ids: {len(nas_recording_ids)}")
    print(f"Number of local recording ids: {len(current_hololens_recording_ids)}")
    print(f"Number of missing recording ids: {len(missing_recording_ids)}")
    print(f"Missing recording ids: {missing_recording_ids}")


def check_recording_ids_difference_box_nas():
    downloadable_recording_ids = fetch_hololens_box_recording_ids()
    nas_recording_ids = fetch_hololens_nas_recording_ids(nas_hololens_data_path)

    missing_recording_ids = list(set(nas_recording_ids) ^ set(downloadable_recording_ids))
    print(" ---------------- BOX - NAS ---------------- ")
    print(f"Number of box recording ids: {len(downloadable_recording_ids)}")
    print(f"Number of NAS recording ids: {len(nas_recording_ids)}")
    print(f"Number of missing recording ids: {len(missing_recording_ids)}")
    print(f"Missing recording ids: {missing_recording_ids}")


if __name__ == "__main__":
    download_links_version = 10
    download_links_json_file_path = f"../backend/download_links_jsons/v{download_links_version}/recording_download_links_{download_links_version}.json"
    local_hololens_data_path = "/data/rohith/captain_cook/data/hololens"
    nas_hololens_data_path = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG/"

    check_recording_ids_difference_box_local()
    check_recording_ids_difference_nas_local()
    check_recording_ids_difference_box_nas()
