import os.path

from boxsdk import Client, CCGAuth


def get_client_credentials(credentials_path):
    with open(credentials_path) as f:
        line = f.readline()
        client_id, client_secret = line.split()
    return client_id, client_secret


def get_client(credentials_path, user_id):
    client_id, client_secret = get_client_credentials(credentials_path)
    ccg_auth = CCGAuth(
        client_id=client_id,
        client_secret=client_secret,
        user=user_id
    )
    client = Client(ccg_auth)
    return client


def upload_data_to_box(local_path, folder_id, user_id, credentials_path):
    client = get_client(credentials_path, user_id=user_id)
    if os.path.isfile(local_path):
        new_file = client.folder(folder_id).upload(local_path)
        print(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')
    elif os.path.isdir(local_path):
        local_path = local_path.rstrip(os.path.sep)
        sub_folder_name = os.path.basename(local_path)
        sub_folder_box = client.folder(folder_id).create_subfolder(sub_folder_name)
        sub_folder_id = sub_folder_box.object_id
        print(f"Folder {sub_folder_name} Upload started")
        dir_files = sorted(os.listdir(local_path))
        for dir_file in dir_files:
            upload_data_to_box(os.path.join(local_path, dir_file), sub_folder_id, credentials_path)
        print(f"Folder {sub_folder_name} Upload completed")


def test_upload():
    local_path = "<Path to the local file or folder>"
    credentials_path = "<Path to the local Box_CCG_Credentials>"
    box_user_id = '<box_user_id>'
    box_folder_id = '<box_folder_id>'
    upload_data_to_box(local_path, folder_id=box_folder_id, user_id=box_user_id, credentials_path=credentials_path)


if __name__ == '__main__':
    test_upload()
