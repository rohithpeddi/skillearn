import os
import shutil
from concurrent.futures import ThreadPoolExecutor


def copy_files_if_different(source_folder, destination_parent_folder):
    for file_name in os.listdir(source_folder):
        source_gopro_file = os.path.join(source_folder, file_name)

        # Destination recording folder
        destination_recording_folder = os.path.join(destination_parent_folder, file_name[:-4])
        destination_recording_gopro_folder = os.path.join(destination_recording_folder, 'gopro')
        destination_gopro_file = os.path.join(destination_recording_gopro_folder, file_name)

        if os.path.isfile(source_gopro_file):
            if os.path.isfile(destination_gopro_file):
                # If the file exists in the destination folder and has the same size, continue
                if os.path.getsize(source_gopro_file) == os.path.getsize(destination_gopro_file):
                    print("Skipping file: " + source_gopro_file + " because it already exists in the destination "
                                                                  " folder and has the same size")
                    continue
            # Copy the file from the source to the destination folder
            print("-----------------------------------")
            print("Copying file: " + source_gopro_file + " to " + destination_gopro_file)
            shutil.copy2(source_gopro_file, destination_gopro_file)


def multithreaded_copy_file_if_different(file_name, source_folder, destination_parent_folder):
    source_gopro_file = os.path.join(source_folder, file_name)

    # Destination recording folder
    destination_recording_folder = os.path.join(destination_parent_folder, file_name[:-4])
    destination_recording_gopro_folder = os.path.join(destination_recording_folder, 'gopro')
    destination_gopro_file = os.path.join(destination_recording_gopro_folder, file_name)

    if os.path.isfile(source_gopro_file):
        if os.path.isfile(destination_gopro_file):
            # If the file exists in the destination folder and has the same size, continue
            if os.path.getsize(source_gopro_file) == os.path.getsize(destination_gopro_file):
                print("Skipping file: " + source_gopro_file + " because it already exists in the destination "
                                                              " folder and has the same size")
                return
        # Copy the file from the source to the destination folder
        print("-----------------------------------")
        print("Copying file: " + source_gopro_file + " to " + destination_gopro_file)
        shutil.copy2(source_gopro_file, destination_gopro_file)


def multithreaded_copy(source_folder, destination_parent_folder):
    with ThreadPoolExecutor(max_workers=1) as executor:
        for file_name in os.listdir(source_folder):
            executor.submit(multithreaded_copy_file_if_different, file_name, source_folder, destination_parent_folder)


# Test
source_folder = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/MISSING_GOPRO/GOPRO"
destination_folder = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG"
# copy_files_if_different(source_folder, destination_folder)
multithreaded_copy(source_folder, destination_folder)
