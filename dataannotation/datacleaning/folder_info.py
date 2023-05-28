import os
import paramiko
import stat
import json


class FolderInfoUtils:

    def __init__(self, folder_path, output_file_path):
        self.folder_path = folder_path
        self.output_file_path = output_file_path

        # Establish SFTP connection
        self.transport = paramiko.Transport(('10.176.140.2', 22))
        self.transport.connect(username='ptg',
                               password='darpa@NAS#DS1522')
        self.sftp_client = self.transport.open_sftp_client()

    def write_folder_structure(self):
        with open(self.output_file_path, 'w') as file:
            self.write_folder(self.folder_path, file, '')

    def write_folder(self, folder_path, file, indent):
        file.write(f'{indent}+ {os.path.basename(folder_path)}\n')
        indent += '|  '

        for item in self.sftp_client.listdir_attr(folder_path):
            item_path = os.path.join(folder_path, item.filename)

            if stat.S_ISDIR(item.st_mode):
                self.write_folder(item_path, file, indent)
            else:
                size = self.human_readable_size(item.st_size)
                file.write(f'{indent}- {item.filename} ({size})\n')

    def create_dict(self, path):
        dir_dict = {'name': os.path.basename(path)}

        if os.path.isdir(path):
            dir_dict['type'] = "directory"
            dir_dict['children'] = [self.create_dict(os.path.join(path, name)) for name in os.listdir(path)]
        else:
            dir_dict['type'] = "file"

        return dir_dict

    def create_json(self, directory_path, output_path):
        directory_dict = self.create_dict(directory_path)

        with open(output_path, 'w') as file:
            json.dump(directory_dict, file, indent=4)

        self.find_missing_gopro(directory_dict)

    def human_readable_size(self, size):
        # the powers for the different units, bytes, kb, mb, gb, tb
        powers = ['B', 'KB', 'MB', 'GB', 'TB']
        index = 0

        while size > 1024 and index < 4:
            size /= 1024
            index += 1

        return f'{size:.2f} {powers[index]}'

    def find_missing_gopro(self, directory_dict):
        missing_gopro = []
        recordings = directory_dict['children']
        for recording in recordings:
            if 'children' not in recording or len(recording['children']) == 0:
                continue
            recording_children = recording['children']
            for recording_child in recording_children:
                if recording_child['name'] == 'gopro':
                    if 'children' not in recording_child or len(recording_child['children']) == 0:
                        missing_gopro.append(recording['name'])
                    break
        missing_gopro = sorted(missing_gopro, key=lambda x: (int(x.split('_')[0]), int(x.split('_')[1])))
        with open('missing_gopro.txt', 'w') as f:
            for id in missing_gopro:
                f.write(id + '\n')

    def close(self):
        self.sftp_client.close()
        self.transport.close()


if __name__ == '__main__':
    folder_path = r'/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG'
    output_file_path = r'/home/rxp190007/CODE/skillearn/dataannotation/datacleaning/folder_structure.txt'
    output_json_path = r'/home/rxp190007/CODE/skillearn/dataannotation/datacleaning/folder_structure.json'
    folder_info_utils = FolderInfoUtils(folder_path, output_file_path)
    # folder_info_utils.write_folder_structure()
    # folder_info_utils.close()

    folder_info_utils.create_json(folder_path, output_json_path)
