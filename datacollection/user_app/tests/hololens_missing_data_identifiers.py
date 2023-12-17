import json
import os

from datacollection.user_app.backend.app.utils.constants import Recording_Constants as const

download_links_version = 13
download_links_json_file_path = f"../backend/download_links_jsons/v{download_links_version}/recording_download_links_{download_links_version}.json"
local_hololens_data_path = "/data/rohith/captain_cook/data/hololens"
nas_hololens_data_path = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG/"


def fetch_hololens_box_recording_ids():
    with open(download_links_json_file_path, "r") as f:
        download_links = json.load(f)

    downloadable_recording_ids = []
    for recording_id, recording_download_link_dict in download_links.items():
        if const.HOLOLENS_SYNC_PV_VIDEO in recording_download_link_dict:
            if (recording_download_link_dict[const.HOLOLENS_SYNC_PV_VIDEO] is not None
                    and recording_download_link_dict[const.HOLOLENS_SYNC_PV_VIDEO] != "null"):
                downloadable_recording_ids.append(recording_id)
            else:
                print(f"{recording_id} - {recording_download_link_dict[const.HOLOLENS_SYNC_PV_VIDEO]}")

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
            sync_recording_data_path = os.path.join(hololens_recording_data_path, "sync")
            pv_sync_recording_data_path = os.path.join(sync_recording_data_path, "pv")

            if os.path.isdir(pv_sync_recording_data_path):
                if len(os.listdir(pv_sync_recording_data_path)) > 0:
                    current_hololens_recording_ids.append(recording_id_directory_name)
                else:
                    # print(f"Recording {recording_id_directory_name} has empty sync folder. Skipping...")
                    pass
    return current_hololens_recording_ids


def check_recording_ids_difference_box_local():
    downloadable_recording_ids = fetch_hololens_box_recording_ids()
    current_hololens_recording_ids = fetch_hololens_recording_ids(local_hololens_data_path)

    missing_recording_ids = list(set(downloadable_recording_ids) ^ set(current_hololens_recording_ids))
    missing_recording_ids = sorted(missing_recording_ids, key=lambda x: int(x.split("_")[0]))
    print(" ---------------- BOX - LOCAL ---------------- ")
    print(f"Number of box recording ids: {len(downloadable_recording_ids)}")
    print(f"Number of local recording ids: {len(current_hololens_recording_ids)}")
    print(f"Number of missing recording ids: {len(missing_recording_ids)}")
    print(f"Missing recording ids: {missing_recording_ids}")


def check_recording_ids_difference_nas_local():
    nas_recording_ids = fetch_hololens_nas_recording_ids(nas_hololens_data_path)
    current_hololens_recording_ids = fetch_hololens_recording_ids(local_hololens_data_path)

    missing_recording_ids = list(set(nas_recording_ids) ^ set(current_hololens_recording_ids))
    missing_recording_ids = sorted(missing_recording_ids, key=lambda x: int(x.split("_")[0]))
    print(" ---------------- NAS - LOCAL ---------------- ")
    print(f"Number of NAS recording ids: {len(nas_recording_ids)}")
    print(f"Number of local recording ids: {len(current_hololens_recording_ids)}")
    print(f"Number of missing recording ids: {len(missing_recording_ids)}")
    print(f"Missing recording ids: {missing_recording_ids}")


def check_recording_ids_difference_box_nas():
    downloadable_recording_ids = fetch_hololens_box_recording_ids()
    nas_recording_ids = fetch_hololens_nas_recording_ids(nas_hololens_data_path)

    missing_recording_ids = list(set(nas_recording_ids) ^ set(downloadable_recording_ids))
    missing_recording_ids = sorted(missing_recording_ids, key=lambda x: int(x.split("_")[0]))
    print(" ---------------- BOX - NAS ---------------- ")
    print(f"Number of box recording ids: {len(downloadable_recording_ids)}")
    print(f"Number of NAS recording ids: {len(nas_recording_ids)}")
    print(f"Number of missing recording ids: {len(missing_recording_ids)}")
    print(f"Missing recording ids: {missing_recording_ids}")
    print("---------------------------------------------------------------------------")

    for recording_id in missing_recording_ids:
        is_in_box = recording_id in downloadable_recording_ids
        is_in_nas = recording_id in nas_recording_ids
        print(f"{recording_id}: BOX - {is_in_box}, NAS - {is_in_nas}")

    return missing_recording_ids


if __name__ == "__main__":
    # check_recording_ids_difference_box_local()
    # check_recording_ids_difference_nas_local()
    check_recording_ids_difference_box_nas()
