import os
import shutil
import shutil
import time

from concurrent.futures import ThreadPoolExecutor
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


#
# def compare_files_in_folder(source_root, destination_root):
# 	# 1. Get all the files in the source folder and destination folder and compare them
# 	source_files = [f for f in os.listdir(source_root) if os.path.isfile(os.path.join(source_root, f))]
#
# 	for file in source_files:
# 		source_file = os.path.join(source_root, file)
# 		destination_file = os.path.join(destination_root, file)
#
# 		if not os.path.isfile(destination_file):
# 			logger.info(f"File {destination_file} is missing.")
# 			return False
#
# 		if os.path.getsize(source_file) != os.path.getsize(destination_file):
# 			logger.info(f"File {destination_file} has a different size.")
# 			return False
#
# 	return True
#
#
# def compare_folders(source_root, destination_root):
# 	# 1. Check if all files in the source folder are present in the destination folder
# 	are_files_matching = compare_files_in_folder(source_root, destination_root)
#
# 	if not are_files_matching:
# 		logger.info("-----------------------------------")
# 		logger.info("Files are missing.")
# 		logger.info("Source folder: ", source_root)
# 		logger.info("Destination folder: ", destination_root)
# 		logger.info("-----------------------------------")
# 		return False
#
# 	# 2. Get all the sub folders in the source folder and destination folder and compare them recursively
# 	source_directories = [d for d in os.listdir(source_root) if os.path.isdir(os.path.join(source_root, d))]
# 	destination_directories = [d for d in os.listdir(destination_root) if
# 	                           os.path.isdir(os.path.join(destination_root, d))]
#
# 	for directory in source_directories:
# 		source_directory = os.path.join(source_root, directory)
# 		destination_directory = os.path.join(destination_root, directory)
#
# 		if not os.path.isdir(destination_directory):
# 			logger.info(f"Directory {destination_directory} is missing.")
# 			return False
#
# 		are_folders_matching = compare_folders(source_directory, destination_directory)
#
# 		if not are_folders_matching:
# 			logger.info("-----------------------------------")
# 			logger.info("Folder files are missing.")
# 			logger.info("Source folder: ", source_directory)
# 			logger.info("Destination folder: ", destination_directory)
# 			logger.info("-----------------------------------")
# 			return False


def compare_and_transfer_info_files(source_parent_directory, destination_parent_directory):
    for recording_id in os.listdir(source_parent_directory):
        logger.info("----------------------------------------------------------")
        logger.info(f"Processing recording {recording_id}")
        source_recording_directory = os.path.join(source_parent_directory, recording_id)
        if os.listdir(source_recording_directory):
            source_recording_info_file_path = os.path.join(source_recording_directory, "Hololens2Info.dat")
            destination_recording_folder = os.path.join(destination_parent_directory, recording_id, "raw")
            destination_recording_info_file_path = os.path.join(destination_recording_folder, "Hololens2Info.dat")
            
            if not os.path.isdir(destination_recording_folder):
                logger.info("Recording folder does not exist. Skipping this recording.")
                continue
            
            if os.path.isfile(source_recording_info_file_path):
                if not os.path.isfile(destination_recording_info_file_path):
                    logger.info(f"Copying file {destination_recording_info_file_path}")
                    shutil.copyfile(source_recording_info_file_path, destination_recording_info_file_path)
                else:
                    if os.path.getsize(source_recording_info_file_path) != os.path.getsize(
                            destination_recording_info_file_path):
                        logger.info(f"File {destination_recording_info_file_path} has a different size.")
                        logger.info("Deleting the file and copying again.")
                        shutil.rmtree(destination_recording_info_file_path)
                        shutil.copyfile(source_recording_info_file_path, destination_recording_info_file_path)
                    logger.info(f"File {destination_recording_info_file_path} already exists.")


def check_file_size_and_transfer(source_file_path, destination_file_path):
    if os.path.isfile(source_file_path):
        if not os.path.isfile(destination_file_path):
            logger.info(f"Copying file {destination_file_path}")
            shutil.copyfile(source_file_path, destination_file_path)
        else:
            if os.path.getsize(source_file_path) != os.path.getsize(destination_file_path):
                logger.info(f"File {destination_file_path} has a different size.")
                logger.info("Deleting the file and copying again.")
                shutil.rmtree(destination_file_path)
                shutil.copyfile(source_file_path, destination_file_path)
            logger.info(f"File {destination_file_path} already exists.")


def compare_and_transfer(source_parent_directory, destination_parent_directory, recording_id):
    logger.info("----------------------------------------------------------")
    logger.info(f"[{recording_id}] BEGIN TRANSFER ZIPPED FILES FROM LOCAL TO NAS")
    source_sync_directory = os.path.join(source_parent_directory, recording_id, "sync")
    destination_sync_directory = os.path.join(destination_parent_directory, recording_id, "sync")
    
    source_depth_ahat_directory = os.path.join(source_sync_directory, "depth_ahat")
    source_ab_zip_file = os.path.join(source_depth_ahat_directory, "ab.zip")
    source_depth_zip_file = os.path.join(source_depth_ahat_directory, "depth.zip")
    
    destination_depth_ahat_directory = os.path.join(destination_sync_directory, "depth_ahat")
    destination_ab_zip_file = os.path.join(destination_depth_ahat_directory, "ab.zip")
    destination_depth_zip_file = os.path.join(destination_depth_ahat_directory, "depth.zip")
    
    logger.info(f"[{recording_id}  Checking file size and transferring [AB]")
    check_file_size_and_transfer(source_ab_zip_file, destination_ab_zip_file)
    
    logger.info(f"[{recording_id}  Checking file size and transferring [Depth]")
    check_file_size_and_transfer(source_depth_zip_file, destination_depth_zip_file)
    
    source_pv_directory = os.path.join(source_sync_directory, "pv")
    source_pv_zip_file = os.path.join(source_pv_directory, "frames.zip")
    
    destination_pv_directory = os.path.join(destination_sync_directory, "pv")
    destination_pv_zip_file = os.path.join(destination_pv_directory, "frames.zip")
    
    logger.info(f"[{recording_id}  Checking file size and transferring [PV]")
    check_file_size_and_transfer(source_pv_zip_file, destination_pv_zip_file)
    
    logger.info(f"[{recording_id}] END TRANSFER ZIPPED FILES FROM LOCAL TO NAS")
    
    
def multithreading_video_conversion(source_parent_directory, destination_parent_directory):
    max_workers = 10
    recording_ids = os.listdir(source_parent_directory)
    logger.info("Preparing to synchronize using ThreadPoolExecutor with max_workers = 1")
    # Create a ThreadPoolExecutor with a suitable number of threads (e.g., 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for index, recording_id in recording_ids:
            executor.submit(
                compare_and_transfer,
                source_parent_directory,
                destination_parent_directory,
                recording_id
            )


if __name__ == '__main__':
    # source_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/BACKUP_STUFF/PTG_HOLOLENS_BACKUP/hololens_bak_bharath"
    # destination_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG"
    #
    # compare_and_transfer_info_files(source_directory, destination_directory)
    
    source_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/BACKUP_STUFF/PTG_HOLOLENS_BACKUP/hololens_bak_bharath"
    destination_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG"
