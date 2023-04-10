# TODO:
# 1. Each method takes a list of directories as input
# 2. Performs the necessary function as described by the method name
import os

from .SequenceViewer import SequenceViewer
from .nas_transfer_service import NASTransferService
from .synchronization_service import SynchronizationService
from .video_conversion_service import VideoConversionService
from ..constants import Post_Processing_Constants as const
from ..logger_config import logger
from ..services.box_service import BoxService
from ..services.firebase_service import FirebaseService


class PostProcessingService:

    def __init__(
            self,
            recording,
            data_parent_directory="../../../../../data"
    ):
        self.recording = recording
        self.data_parent_directory = data_parent_directory

        self.box_service = BoxService()
        self.db_service = FirebaseService()
        self.nas_transfer_service = NASTransferService(self.recording, self.data_parent_directory)

    def change_video_resolution(self, video_file_path, resolution=None):
        logger.info(f'Started changing video resolution for {self.recording.id}')
        video_conversion_service = VideoConversionService()
        converted_file_path = video_conversion_service.convert_video(video_file_path)
        logger.info(f'Finished changing video resolution for {self.recording.id}')
        return converted_file_path

    def synchronize_data(self):
        data_directory = os.path.join(self.data_parent_directory, self.recording.id)
        sync_parent_directory = os.path.join(data_directory, const.SYNC)
        base_stream = const.PHOTOVIDEO
        sync_streams = [const.DEPTH_AHAT, const.SPATIAL]
        pv_sync_stream = SynchronizationService(
            base_stream=base_stream,
            synchronize_streams=sync_streams,
            data_parent_directory=self.data_parent_directory,
            synchronized_parent_directory=sync_parent_directory,
            recording=self.recording
        )
        logger.info(f'Started synchronization for {self.recording.id}')
        pv_sync_stream.sync_streams()
        logger.info(f'Finished synchronization for {self.recording.id}')

    def verify_3d_information(self):
        sequence_folder = os.path.join(self.data_parent_directory, self.recording.id, const.SYNC)
        sequence_viewer = SequenceViewer()
        sequence_viewer.load(sequence_folder)
        sequence_viewer.run()

    def push_go_pro_360_to_box(self, file_path):
        converted_file_path = self.change_video_resolution(file_path)
        self.box_service.upload_go_pro_360_video(self.recording, converted_file_path)

    def push_data_to_NAS(self):
        self.nas_transfer_service.transfer_from_local_to_nas()

    def push_NAS_data_to_box(self):
        pass

    def generate_audio(self):
        pass

    def generate_video(self):
        pass

    def generate_muxed_audio_video(self):
        pass

