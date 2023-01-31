import os.path

from boxsdk import Client, CCGAuth


# TODO: Upload should respect nested folder structure in the box

class BoxService:

	def __init__(self):
		self.user_id = '23441227496'
		self.root_folder_id = '192253529318'
		self.client_id = 'krr2b0dmxvnqn83ikpe6ufs58jg9t82b'
		self.client_secret = 'TTsVwLrnv9EzmKJv67yrCyUM09wJSriK'
		self.ccg_credentials = 'krr2b0dmxvnqn83ikpe6ufs58jg9t82b TTsVwLrnv9EzmKJv67yrCyUM09wJSriK'

		self.client = Client(CCGAuth(client_id=self.client_id,
									 client_secret=self.client_secret,
									 user=self.user_id))

	def uploadData(self, local_path, folder_id='192253529318'):
		if os.path.isfile(local_path):
			new_file = self.client.folder(self.root_folder_id).upload(local_path)
			print(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')
		elif os.path.isdir(local_path):
			local_path = local_path.rstrip(os.path.sep)
			sub_folder_name = os.path.basename(local_path)
			sub_folder_box = self.client.folder(folder_id).create_subfolder(sub_folder_name)
			sub_folder_id = sub_folder_box.object_id
			print(f"Folder {sub_folder_name} Upload started")
			dir_files = sorted(os.listdir(local_path))
			for dir_file in dir_files:
				self.uploadData(os.path.join(local_path, dir_file), sub_folder_id)
			print(f"Folder {sub_folder_name} Upload completed")


def test_upload():
	local_path = "<Path to the local file or folder>"
	credentials_path = "<Path to the local Box_CCG_Credentials>"
	box_user_id = '<box_user_id>'
	box_folder_id = '<box_folder_id>'


# upload_data_to_box(local_path, folder_id=box_folder_id, user_id=box_user_id, credentials_path=credentials_path)


if __name__ == '__main__':
	test_upload()
