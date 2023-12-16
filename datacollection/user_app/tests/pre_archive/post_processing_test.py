import os
import shutil
import time

from concurrent.futures import ThreadPoolExecutor

import pysftp

from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.post_processing.compress_data_service import CompressDataService
from datacollection.user_app.backend.app.post_processing.nas_unzipping_service import multithreading_unzip
from datacollection.user_app.backend.app.post_processing.video_conversion_service import VideoConversionService
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.services.synchronization_service import SynchronizationServiceV2
from datacollection.user_app.backend.app.utils.constants import Synchronization_Constants as const
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


# def process_directory(
#         data_parent_directory,
#         data_recording_directory_name,
#         db_service,
#         box_service,
#         temp_local_data_directory
# ):
#     data_recording_directory_path = os.path.join(data_parent_directory, data_recording_directory_name)
#     if os.path.isdir(data_recording_directory_path):
#         recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
#         logger.info(f"[{recording.id}] BEGIN SYNCHRONIZATION")
#         synchronization_service = SynchronizationServiceV2(
#             data_parent_directory,
#             recording,
#             const.BASE_STREAM,
#             const.SYNCHRONIZATION_STREAMS
#         )
#         synchronization_service.sync_streams()
#         recording_id = recording.id
#
#         local_raw_data_directory = os.path.join(temp_local_data_directory, recording_id, const.RAW)
#         local_sync_data_directory = os.path.join(temp_local_data_directory, recording.id, const.SYNC)
#         if not os.path.exists(local_sync_data_directory):
#             os.makedirs(local_sync_data_directory)
#
#         # start_nas_to_local_time = time.time()
#         # logger.info(f"[{recording.id}] BEGIN NAS TO LOCAL")
#         #
#         # for item in os.listdir(remote_sync_data_directory):
#         # 	source_item_path = os.path.join(remote_sync_data_directory, item)
#         # 	destination_item_path = os.path.join(local_sync_data_directory, item)
#         # 	try:
#         # 		if os.path.isdir(source_item_path):
#         # 			shutil.copytree(source_item_path, destination_item_path, symlinks=False, ignore=None)
#         # 		else:
#         # 			shutil.copy2(source_item_path, destination_item_path)
#         # 	except Exception as e:
#         # 		logger.error(f"[{recording.id}] Error copying files from NAS to local : {e}")
#         #
#         # total_nas_to_local_time = time.strftime(
#         # 	"%H:%M:%S",
#         # 	time.gmtime(time.time() - start_nas_to_local_time)
#         # )
#         # logger.info(f"[{recording.id}] END NAS TO LOCAL : {total_nas_to_local_time}")
#
#         # ------------------ ZIPPING RAW FILES ------------------
#         logger.info(f"[{recording_id}] Zipping RAW frames data")
#         # ------------------ ZIPPING DEPTH FRAMES ------------------
#
#         local_raw_depth_parent_directory = os.path.join(local_raw_data_directory, const.DEPTH_AHAT)
#
#         local_raw_depth_frames_zip_file_path = os.path.join(local_raw_depth_parent_directory, const.DEPTH_ZIP)
#         if not os.path.exists(local_raw_depth_frames_zip_file_path):
#             logger.info(f"[{recording_id}] Compressing Depth data")
#             start_compress_depth_time = time.time()
#             CompressDataService.compress_dir(local_raw_depth_parent_directory, const.DEPTH)
#             total_compress_depth_time = time.strftime(
#                 "%H:%M:%S",
#                 time.gmtime(time.time() - start_compress_depth_time)
#             )
#             logger.info(f"[{recording_id}] Done compressing Depth data : {total_compress_depth_time}")
#         else:
#             logger.info(f"[{recording_id}] Skipping compressing Depth data")
#
#         local_raw_depth_ab_frames_zip_file_path = os.path.join(local_raw_depth_parent_directory, const.AB_ZIP)
#         if not os.path.exists(local_raw_depth_ab_frames_zip_file_path):
#             logger.info(f"[{recording_id}] Compressing Active Brightness data")
#             start_compress_ab_time = time.time()
#             CompressDataService.compress_dir(local_raw_depth_parent_directory, const.AB)
#             total_compress_ab_time = time.strftime(
#                 "%H:%M:%S",
#                 time.gmtime(time.time() - start_compress_ab_time)
#             )
#             logger.info(f"[{recording_id}] Done compressing Active Brightness data : {total_compress_ab_time}")
#         else:
#             logger.info(f"[{recording_id}] Skipping compressing Active Brightness data")
#
#         # ------------------ ZIPPING PV FRAMES ------------------
#
#         local_raw_base_stream_directory = os.path.join(local_raw_data_directory, const.BASE_STREAM)
#         sync_pv_frames_zip_file_path = os.path.join(local_raw_base_stream_directory, const.FRAMES_ZIP)
#         if not os.path.exists(sync_pv_frames_zip_file_path):
#             logger.info(f"[{recording_id}] Compressing pv frames directory")
#             start_compress_pv_time = time.time()
#             CompressDataService.compress_dir(local_raw_base_stream_directory, const.FRAMES)
#             total_compress_pv_time = time.strftime(
#                 "%H:%M:%S",
#                 time.gmtime(time.time() - start_compress_pv_time)
#             )
#             logger.info(f"[{recording_id}] Done compressing pv frames directory : {total_compress_pv_time}")
#         else:
#             logger.info(f"[{recording_id}] Skipping compressing pv frames directory")
#
#         # ------------------ ZIPPING SYNC FILES ------------------
#         logger.info(f"[{recording_id}] Zipping SYNC frames data")
#
#         # ------------------ ZIPPING DEPTH FRAMES ------------------
#
#         local_sync_depth_parent_directory = os.path.join(local_sync_data_directory, const.DEPTH_AHAT)
#
#         local_sync_depth_frames_zip_file_path = os.path.join(local_sync_depth_parent_directory, const.DEPTH_ZIP)
#         if not os.path.exists(local_sync_depth_frames_zip_file_path):
#             logger.info(f"[{recording_id}] Compressing Depth data")
#             start_compress_depth_time = time.time()
#             CompressDataService.compress_dir(local_sync_depth_parent_directory, const.DEPTH)
#             total_compress_depth_time = time.strftime(
#                 "%H:%M:%S",
#                 time.gmtime(time.time() - start_compress_depth_time)
#             )
#             logger.info(f"[{recording_id}] Done compressing Depth data : {total_compress_depth_time}")
#         else:
#             logger.info(f"[{recording_id}] Skipping compressing Depth data")
#
#         local_sync_depth_ab_frames_zip_file_path = os.path.join(local_sync_depth_parent_directory, const.AB_ZIP)
#         if not os.path.exists(local_sync_depth_ab_frames_zip_file_path):
#             logger.info(f"[{recording_id}] Compressing Active Brightness data")
#             start_compress_ab_time = time.time()
#             CompressDataService.compress_dir(local_sync_depth_parent_directory, const.AB)
#             total_compress_ab_time = time.strftime(
#                 "%H:%M:%S",
#                 time.gmtime(time.time() - start_compress_ab_time)
#             )
#             logger.info(f"[{recording_id}] Done compressing Active Brightness data : {total_compress_ab_time}")
#         else:
#             logger.info(f"[{recording_id}] Skipping compressing Active Brightness data")
#
#         # ------------------ ZIPPING PV FRAMES ------------------
#
#         local_sync_base_stream_directory = os.path.join(local_sync_data_directory, const.BASE_STREAM)
#         sync_pv_frames_zip_file_path = os.path.join(local_sync_base_stream_directory, const.FRAMES_ZIP)
#         if not os.path.exists(sync_pv_frames_zip_file_path):
#             logger.info(f"[{recording_id}] Compressing pv frames directory")
#             start_compress_pv_time = time.time()
#             CompressDataService.compress_dir(local_sync_base_stream_directory, const.FRAMES)
#             total_compress_pv_time = time.strftime(
#                 "%H:%M:%S",
#                 time.gmtime(time.time() - start_compress_pv_time)
#             )
#             logger.info(f"[{recording_id}] Done compressing pv frames directory : {total_compress_pv_time}")
#         else:
#             logger.info(f"[{recording_id}] Skipping compressing pv frames directory")
#
#         logger.info(f"[{recording.id}] BEGIN UPLOADING TO BOX")
#         box_service.upload_from_nas(recording, temp_local_data_directory)
#         logger.info(f"[{recording.id}] END UPLOADING TO BOX")
#         logger.info(f"[{recording.id}] END SYNCHRONIZATION")


def process_directory(
        data_parent_directory,
        data_recording_directory_name,
        db_service,
        box_service,
        temp_local_data_directory
):
    data_recording_directory_path = os.path.join(data_parent_directory, data_recording_directory_name)
    if os.path.isdir(data_recording_directory_path):
        recording = fetch_recording(db_service, data_recording_directory_name)
        # logger.info(f"[{recording.id}] BEGIN SYNCHRONIZATION")
        # try:
        #     sync_streams(data_parent_directory, recording)
        #     temp_directories = create_temp_directories(recording, temp_local_data_directory)
        #     zip_raw_files(temp_directories, recording.id)
        #     zip_sync_files(temp_directories, recording.id)
        # except Exception as e:
        #     logger.error(f"[{recording.id}] Error while synchronizing streams {e}")

        try:
            upload_to_box(box_service, recording, temp_local_data_directory)
            # logger.info(f"[{recording.id}] END SYNCHRONIZATION")
        except Exception as e:
            logger.error(f"[{recording.id}] Error while uploading to box {e}")


def fetch_recording(db_service, data_recording_directory_name):
    recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
    return recording


def sync_streams(data_parent_directory, recording):
    synchronization_service = SynchronizationServiceV2(
        data_parent_directory,
        recording,
        const.BASE_STREAM,
        const.SYNCHRONIZATION_STREAMS
    )
    synchronization_service.sync_streams()


def create_temp_directories(recording, temp_local_data_directory):
    local_raw_data_directory = os.path.join(temp_local_data_directory, recording.id, const.RAW)
    local_sync_data_directory = os.path.join(temp_local_data_directory, recording.id, const.SYNC)
    directories = {
        'local_raw': local_raw_data_directory,
        'local_sync': local_sync_data_directory
    }
    for directory in directories.values():
        if not os.path.exists(directory):
            os.makedirs(directory)
    return directories


def zip_raw_files(directories, recording_id):
    compress_data(directories['local_raw'], recording_id, const.DEPTH_AHAT, const.DEPTH_ZIP, const.DEPTH, "Depth")
    compress_data(directories['local_raw'], recording_id, const.DEPTH_AHAT, const.AB_ZIP, const.AB, "Active Brightness")
    compress_data(directories['local_raw'], recording_id, const.BASE_STREAM, const.FRAMES_ZIP, const.FRAMES,
                  "pv frames")


def zip_sync_files(directories, recording_id):
    compress_data(directories['local_sync'], recording_id, const.DEPTH_AHAT, const.DEPTH_ZIP, const.DEPTH, "Depth")
    compress_data(directories['local_sync'], recording_id, const.DEPTH_AHAT, const.AB_ZIP, const.AB,
                  "Active Brightness")
    compress_data(directories['local_sync'], recording_id, const.BASE_STREAM, const.FRAMES_ZIP, const.FRAMES,
                  "pv frames")


def compress_data(directory, recording_id, parent_directory, zip_file, directory_name, log_msg):
    local_parent_directory = os.path.join(directory, parent_directory)
    local_zip_file_path = os.path.join(local_parent_directory, zip_file)
    if not os.path.exists(local_zip_file_path):
        logger.info(f"[{recording_id}] Compressing {log_msg} data")
        start_compress_time = time.time()
        CompressDataService.compress_dir(local_parent_directory, directory_name)
        total_compress_time = time.strftime(
            "%H:%M:%S",
            time.gmtime(time.time() - start_compress_time)
        )
        logger.info(f"[{recording_id}] Done compressing {log_msg} data : {total_compress_time}")
    else:
        logger.info(f"[{recording_id}] Skipping compressing {log_msg} data")


def upload_to_box(box_service, recording, temp_local_data_directory):
    logger.info(f"[{recording.id}] BEGIN UPLOADING TO BOX")
    box_service.upload_from_nas(recording, temp_local_data_directory)
    logger.info(f"[{recording.id}] END UPLOADING TO BOX")


def begin_post_processing():
    data_parent_directory = "/home/ptg/CODE/data/hololens"
    temp_local_data_directory = "/home/ptg/CODE/data/hololens"

    db_service = FirebaseService()
    box_service = BoxService()
    max_workers = 10
    data_recording_directories = os.listdir(data_parent_directory)
    data_recording_directories = ['29_19', '29_15', '29_17', '29_22', '28_16', '27_38', '26_6', '26_7', '26_20',
                                  '26_22']
    data_recording_directories = ['1_7', '2_17', '7_2', '7_3', '8_25']
    data_recording_directories = ['16_3', '16_17', '16_20', '17_28', '17_36', '17_43', '18_8', '18_12', '21_32',
                                  '22_37']
    data_recording_directories = ['23_38', '23_41']
    data_recording_directories = ['4_120', '4_122', '16_110', '22_137', '12_16']
    data_recording_directories = ['4_120', '4_122', '16_110', '22_137']
    logger.info(f"Preparing to synchronize using ThreadPoolExecutor with max_workers = {max_workers}")
    # Create a ThreadPoolExecutor with a suitable number of threads (e.g., 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for data_recording_directory_name in data_recording_directories:
            executor.submit(
                process_directory,
                data_parent_directory,
                data_recording_directory_name,
                db_service,
                box_service,
                temp_local_data_directory
            )


def convert_recording_360p(
        data_parent_directory,
        data_recording_directory_name,
        db_service
):
    data_recording_directory_path = os.path.join(data_parent_directory, data_recording_directory_name)
    if os.path.isdir(data_recording_directory_path):
        recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
        recording_id = recording.id

        recording_360p_file_name = f'{recording_id}_360p.mp4'
        recording_4k_file_name = f'{recording_id}.MP4'
        local_gopro_path = os.path.join(data_parent_directory, recording_id, const.GOPRO)

        local_gopro_360p_path = os.path.join(local_gopro_path, recording_360p_file_name)
        local_gopro_4k_path = os.path.join(local_gopro_path, recording_4k_file_name)

        if not os.path.exists(local_gopro_360p_path):
            start_video_conversion_time = time.time()
            logger.info(f"[{recording.id}] BEGIN CONVERTING TO 360P VIDEO")

            logger.info(f'Started changing video resolution for {recording_id}')
            video_conversion_service = VideoConversionService()
            converted_file_path = video_conversion_service.convert_video(local_gopro_4k_path, local_gopro_360p_path)
            logger.info(f'Finished changing video resolution for {recording_id}')

            total_video_conversion_time = time.strftime(
                "%H:%M:%S",
                time.gmtime(time.time() - start_video_conversion_time)
            )
            logger.info(f"[{recording.id}] END CONVERTING TO 360P VIDEO : {total_video_conversion_time}")
        else:
            logger.info(f"[{recording.id}] Skipping converting to 360p video")


def multithreading_video_conversion():
    data_parent_directory = "/home/ptg/CODE/data/hololens"

    db_service = FirebaseService()
    max_workers = 10
    data_recording_directories = os.listdir(data_parent_directory)
    data_recording_directories = ['4_120', '4_122', '16_110', '22_137']
    logger.info("Preparing to synchronize using ThreadPoolExecutor with max_workers = 1")
    # Create a ThreadPoolExecutor with a suitable number of threads (e.g., 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for data_recording_directory_name in data_recording_directories:
            executor.submit(
                convert_recording_360p,
                data_parent_directory,
                data_recording_directory_name,
                db_service
            )


# def _transfer_directory( sftp_client, src_directory, dst_directory, is_file=False):
#     if not is_file:
#         sftp_client.makedirs(dst_directory)
#     for item in os.listdir(src_directory):
#         src_path = os.path.join(src_directory, item)
#         dst_path = os.path.join(dst_directory, item)
#         if os.path.isfile(src_path) or is_file:
#             try:
#                 sftp_client.stat(dst_path)
#                 logger.info(f"File {dst_path} already exists on NAS. Skipping transfer.")
#                 continue
#             except FileNotFoundError:
#                 logger.info(f"File {dst_path} does not exist on NAS . Transferring...")
#             sftp_client.put(src_path, dst_path)
#             logger.info(f'Transferred {item} to NAS')
#         elif os.path.isdir(src_path):
#             _transfer_directory(sftp_client, src_path, dst_path)
#
#
# def _timed_transfer_to_nas(recording_id, sftp_client, node_name, directory_path, remote_node_path, is_file=False):
#     start_time = time.time()
#     logger.info(f"[{recording_id}] Begin transfer to NAS {node_name} for recording {recording_id}")
#     if is_file:
#         remote_file_path = os.path.join(remote_node_path, node_name)
#         try:
#             sftp_client.stat(remote_file_path)
#             logger.info(f"[{recording_id}] File {remote_file_path} already exists on NAS. Skipping transfer.")
#             return
#         except FileNotFoundError:
#             logger.info(f"[{recording_id}] File {remote_file_path} does not exist on NAS. Transferring...")
#         sftp_client.put(directory_path, remote_file_path)
#     else:
#         _transfer_directory(sftp_client, directory_path, remote_node_path)
#     end_time = time.time()
#     logger.info(
#         f"[{recording_id}] End transfer to NAS {node_name} in {end_time - start_time} seconds for recording {recording_id}")
#
#
# def transfer_from_local_to_nas(recording_id, local_data_root_dir, remote_data_root_dir):
#     sftp_client = pysftp.Connection(const.NAS_HOST_IP, username=const.NAS_USERNAME, password=const.NAS_PASSWORD)
#     # sftp_client.cd(remote_data_root_dir)
#     remote_recording_directory = os.path.join(remote_data_root_dir, recording_id)
#     # mkdir_p(sftp_client, remote_recording_directory)
#     try:
#         sftp_client.stat(remote_recording_directory)
#     except FileNotFoundError:
#         sftp_client.mkdir(remote_recording_directory)
#     sftp_client.chdir(remote_recording_directory)
#
#     remote_hl2_raw_data_dir = os.path.join(remote_recording_directory, const.RAW)
#     try:
#         sftp_client.stat(remote_hl2_raw_data_dir)
#     except FileNotFoundError:
#         sftp_client.mkdir(remote_hl2_raw_data_dir)
#
#     remote_hl2_sync_data_dir = os.path.join(remote_recording_directory, const.SYNC)
#     try:
#         sftp_client.stat(remote_hl2_sync_data_dir)
#     except FileNotFoundError:
#         sftp_client.mkdir(remote_hl2_sync_data_dir)
#
#     remote_hl2_gopro_data_dir = os.path.join(remote_recording_directory, const.GOPRO)
#     try:
#         sftp_client.stat(remote_hl2_gopro_data_dir)
#     except FileNotFoundError:
#         sftp_client.mkdir(remote_hl2_gopro_data_dir)
#
#     local_hl2_root_dir = os.path.join(local_data_root_dir, 'hololens')
#     local_hl2_data_dir = os.path.join(local_hl2_root_dir, recording_id)
#
#     # 1. Transfer RAW data to NAS
#     for node in os.listdir(local_hl2_data_dir):
#         node_path = os.path.join(local_hl2_data_dir, node)
#         if os.path.isdir(node_path) and node not in (const.SYNC, const.GOPRO):
#             remote_node_path = os.path.join(remote_hl2_raw_data_dir, node)
#             _timed_transfer_to_nas(sftp_client, node, node_path, remote_node_path)
#         elif node not in (const.SYNC, const.GOPRO) and not os.path.isdir(node_path):
#             _timed_transfer_to_nas(sftp_client, node, node_path, remote_hl2_raw_data_dir, is_file=True)
#
#     # # 2. Transfer Synchronized data to NAS
#     for node in os.listdir(local_hl2_data_dir):
#         node_path = os.path.join(local_hl2_data_dir, node)
#         if os.path.isdir(node_path) and node not in (const.RAW, const.GOPRO):
#             remote_node_path = os.path.join(remote_hl2_raw_data_dir, node)
#             _timed_transfer_to_nas(sftp_client, node, node_path, remote_node_path)
#         elif node not in (const.RAW, const.GOPRO) and not os.path.isdir(node_path):
#             _timed_transfer_to_nas(sftp_client, node, node_path, remote_hl2_raw_data_dir, is_file=True)
#
#     # 3. Transfer GOPRO data to NAS
#     local_go_pro_file = os.path.join(local_data_root_dir, const.GOPRO, recording_id + '.MP4')
#     _timed_transfer_to_nas(sftp_client, recording_id + '.MP4', local_go_pro_file, remote_hl2_gopro_data_dir, is_file=True)
#
#     local_go_pro_360p_file = os.path.join(local_data_root_dir, const.GOPRO, recording_id + '_360p.mp4')
#     _timed_transfer_to_nas(sftp_client, recording_id + '_360p.mp4', local_go_pro_360p_file,
#                                 remote_hl2_gopro_data_dir, is_file=True)
#
#     sftp_client.close()


def create_directory_if_not_exists(sftp_client, directory_path):
    if not sftp_client.exists(directory_path):
        sftp_client.mkdir(directory_path)


def log_and_transfer(sftp_client, recording_id, src_path, dst_path, is_file):
    dst_path_exists = sftp_client.exists(dst_path)

    logger.info(
        f"[{recording_id}] File {dst_path} {'already exists' if dst_path_exists else 'does not exist'} on NAS. "
        f"{'Skipping transfer.' if dst_path_exists else 'Transferring...'}")

    if not dst_path_exists:
        if is_file:
            sftp_client.put(src_path, dst_path)
        else:
            _transfer_directory(sftp_client, src_path, dst_path)


def _transfer_directory(recording_id, sftp_client, src_directory, dst_directory):
    create_directory_if_not_exists(sftp_client, dst_directory)

    for item in os.listdir(src_directory):
        src_path = os.path.join(src_directory, item)
        dst_path = os.path.join(dst_directory, item)

        if os.path.isdir(src_path):
            _transfer_directory(sftp_client, src_path, dst_path)
        elif os.path.isfile(src_path):
            log_and_transfer(sftp_client, recording_id, src_path, dst_path, True)


def _timed_transfer_to_nas(recording_id, sftp_client, node_name, local_directory_path, remote_directory_path):
    start_time = time.time()

    logger.info(f"[{recording_id}] Begin transfer to NAS {node_name} for recording {recording_id}")

    log_and_transfer(sftp_client, recording_id, local_directory_path, remote_directory_path,
                     os.path.isfile(local_directory_path))

    total_transfer_time = time.strftime(
        "%H:%M:%S",
        time.gmtime(time.time() - start_time)
    )

    logger.info(f"[{recording_id}] End transfer to NAS {node_name} in {total_transfer_time}")


# def transfer_from_local_to_nas(recording_id, local_data_root_dir, remote_data_root_dir):
#     with pysftp.Connection(const.NAS_HOST_IP, username=const.NAS_USERNAME, password=const.NAS_PASSWORD) as sftp_client:
#         remote_recording_directory = os.path.join(remote_data_root_dir, recording_id)
#         create_directory_if_not_exists(sftp_client, remote_recording_directory)
#
#         data_types = [const.RAW, const.SYNC, const.GOPRO]
#         for data_type in data_types:
#             remote_data_dir = os.path.join(remote_recording_directory, data_type)
#             create_directory_if_not_exists(sftp_client, remote_data_dir)
#
#         local_hl2_root_dir = os.path.join(local_data_root_dir, 'hololens')
#         local_hl2_recording_dir = os.path.join(local_hl2_root_dir, recording_id)
#
#         # 1. Transfer RAW data to NAS
#         for node in os.listdir(local_hl2_recording_dir):
#             node_path = os.path.join(local_hl2_recording_dir, node)
#             if os.path.isdir(node_path) and node not in (const.SYNC, const.GOPRO):
#                 remote_node_path = os.path.join(remote_hl2_raw_data_dir, node)
#                 _timed_transfer_to_nas(sftp_client, node, node_path, remote_node_path)
#             elif node not in (const.SYNC, const.GOPRO) and not os.path.isdir(node_path):
#                 _timed_transfer_to_nas(sftp_client, node, node_path, remote_hl2_raw_data_dir, is_file=True)
#
#         # # 2. Transfer Synchronized data to NAS
#         for node in os.listdir(local_hl2_data_dir):
#             node_path = os.path.join(local_hl2_data_dir, node)
#             if os.path.isdir(node_path) and node not in (const.RAW, const.GOPRO):
#                 remote_node_path = os.path.join(remote_hl2_raw_data_dir, node)
#                 _timed_transfer_to_nas(sftp_client, node, node_path, remote_node_path)
#             elif node not in (const.RAW, const.GOPRO) and not os.path.isdir(node_path):
#                 _timed_transfer_to_nas(sftp_client, node, node_path, remote_hl2_raw_data_dir, is_file=True)
#
#         local_go_pro_file = os.path.join(local_data_root_dir, const.GOPRO, recording_id + '.MP4')
#         remote_gopro_file = os.path.join(remote_recording_directory, const.GOPRO, recording_id + '.MP4')
#         _timed_transfer_to_nas(sftp_client, recording_id + '.MP4', local_go_pro_file, remote_gopro_file)
#
#         local_go_pro_360p_file = os.path.join(local_data_root_dir, const.GOPRO, recording_id + '_360p.mp4')
#         remote_gopro_360p_file = os.path.join(remote_recording_directory, const.GOPRO, recording_id + '_360p.mp4')
#         _timed_transfer_to_nas(sftp_client, recording_id + '_360p.mp4', local_go_pro_360p_file, remote_gopro_360p_file)


def begin_unzipping():
    data_parent_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG"
    db_service = FirebaseService()
    recording_list = []
    for data_recording_directory_name in os.listdir(data_parent_directory):
        data_recording_directory_path = os.path.join(data_parent_directory, data_recording_directory_name)
        if os.path.isdir(data_recording_directory_path):
            recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
            recording_list.append(recording)
    recording_list.sort(key=lambda x: x.id)
    multithreading_unzip(recording_list, data_parent_directory)


if __name__ == '__main__':
    begin_post_processing()
    # multithreading_video_conversion()
# begin_unzipping()
