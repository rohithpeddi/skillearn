import os
import paramiko
import stat


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
                size = item.st_size
                file.write(f'{indent}- {item.filename} ({size} bytes)\n')

    def close(self):
        self.sftp_client.close()
        self.transport.close()


if __name__ == '__main__':
    folder_path = r'\NetBackup\PTG'
    output_file_path = r'C:\Users\rohit\PycharmProjects\skillearn\Annotations\data_cleaning\folder_structure.txt'
    folder_info_utils = FolderInfoUtils(folder_path, output_file_path)
    folder_info_utils.write_folder_structure()
    folder_info_utils.close()
