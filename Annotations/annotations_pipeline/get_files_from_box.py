import concurrent
import os

import boxsdk
from boxsdk import Client, OAuth2, CCGAuth


class BoxService:

    def __init__(self, save_path):
        self.user_id = '23441227496'
        self.root_folder_id = '202193575471'
        self.client_id = 'krr2b0dmxvnqn83ikpe6ufs58jg9t82b'
        self.client_secret = 'TTsVwLrnv9EzmKJv67yrCyUM09wJSriK'
        self.ccg_credentials = 'krr2b0dmxvnqn83ikpe6ufs58jg9t82b TTsVwLrnv9EzmKJv67yrCyUM09wJSriK'
        ccg_auth = CCGAuth(client_id=self.client_id, client_secret=self.client_secret, user=self.user_id)
        self.client = Client(ccg_auth)
        self.save_path = save_path
        self.downloaded_files = os.listdir(save_path)

    def download_file(self, file, ):
        file_path = os.path.join(self.save_path, f"{file.name}")
        if file.name not in self.downloaded_files:
            self.downloaded_files.append(file.name)
            with open(file_path, 'wb') as f:
                # print(file_path)
                self.client.file(file.id).download_to(f)

    def get_folders(self, id, max_workers=5):
        # There is a rate limit on box of 6 per second, so we need to use max 5 thread pools to download the files
        folders = self.client.folder(id).get()
        items = self.client.folder(id).get_items()
        # Print the folder name and the names of the items in the folder
        print(f"Folder name: {folders.name}")
        # Download the contents of each file in the folder parallelly
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for item in items:
                if isinstance(item, boxsdk.object.file.File):
                    futures.append(executor.submit(self.download_file, item))
                elif isinstance(item, boxsdk.object.folder.Folder):
                    # Recursively call this function with the subfolder as the new folder to iterate through
                    futures.append(executor.submit(self.get_folders, item.id))
            for future in concurrent.futures.as_completed(futures):
                # Raise any exceptions that occurred during the download
                future.result()


if __name__ == '__main__':
    save_path = '/data/error_dataset/recordings'
    box_service = BoxService(save_path)
    box_service.get_folders(box_service.root_folder_id)
