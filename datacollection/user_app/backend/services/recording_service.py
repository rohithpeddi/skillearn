import os
import threading
from ..models.recording import Recording
# from ..post_processing.post_processing_service import PostProcessingService
from ..services.hololens_service import HololensService
from ..services.open_gopro_service import OpenGoProService
from ..logger_config import logger


def create_directories(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


class RecordingService:

    def __init__(self, recording: Recording):
        self.recording = recording

        if self.recording.recording_info.is_go_pro_enabled():
            self.go_pro_service = OpenGoProService()

        if self.recording.recording_info.is_hololens_enabled():
            self.hololens_service = HololensService()

        self.file_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(self.file_dir, "../../../../../data")
        self.go_pro_dir = os.path.join(self.data_dir, "gopro")
        self.hololens_dir = os.path.join(self.data_dir, "hololens")

        create_directories(self.go_pro_dir)
        create_directories(self.hololens_dir)

    def start_recording(self):

        recording_info = self.recording.recording_info

        if recording_info is None:
            logger.error("Recording info is None")
            return

        recording_threads = []
        if recording_info.is_hololens_enabled():
            logger.info("Starting hololens recording")
            # self.hololens_service = HololensService()
            hololens_thread = threading.Thread(target=self.hololens_service.start_recording,
                                               args=(self.recording, self.hololens_dir,))
            recording_threads.append(hololens_thread)

        if recording_info.is_go_pro_enabled():
            logger.info("Starting gopro recording")
            # self.go_pro_service = OpenGoProService() # ToDo: Blocking call
            go_pro_thread = threading.Thread(target=self.go_pro_service.start_recording)
            recording_threads.append(go_pro_thread)

        for thread in recording_threads:
            thread.start()

        for thread in recording_threads:
            thread.join()

    def stop_recording(self):
        recording_info = self.recording.recording_info

        if recording_info is None:
            logger.error("Recording info is None")
            return

        recording_threads = []
        if recording_info.is_hololens_enabled():
            logger.info("Stopping hololens recording")
            hololens_thread = threading.Thread(target=self.hololens_service.stop_recording)
            recording_threads.append(hololens_thread)

        if recording_info.is_go_pro_enabled():
            logger.info("Stopping gopro recording")
            go_pro_thread = threading.Thread(target=self.go_pro_service.stop_recording,
                                             args=(self.go_pro_dir, self.recording.id,))
            recording_threads.append(go_pro_thread)

        for thread in recording_threads:
            thread.start()

        for thread in recording_threads:
            thread.join()

        logger.info("Stopped all threads related to recording")

    def post_process_recording(self):
        # post_processing_service = PostProcessingService(self.recording)
        #
        # # 1. Convert the 4K video to 360P video
        # gopro_dir = os.path.join(post_processing_service.data_parent_directory, self.go_pro_dir)
        # video_file_path = os.path.join(gopro_dir, self.recording.id + '.mp4')
        # post_processing_service.change_video_resolution(video_file_path)

        # Thread - 1
        # 1. Push the 360P to the box

        # Thread - 2
        # 1. Synchronize the data and store in them in new files

        # 2. Zip the folders and store them in NAS

        pass
