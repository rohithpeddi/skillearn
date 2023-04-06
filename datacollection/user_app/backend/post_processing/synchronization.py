import logging
import os
import pickle
import shutil
from typing import List

from datacollection.user_app.backend.hololens import hl2ss
from datacollection.user_app.backend.models.recording import Recording
from datacollection.user_app.backend.constants import Post_Processing_Constants as ppc_const
from datacollection.user_app.backend.logger_config import logger

UNIX_EPOCH = 11644473600


def create_directories(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def write_pickle_data(pickle_data, pickle_file_path):
    with open(pickle_file_path, 'wb') as pickle_file:
        pickle.dump(pickle_data, pickle_file)


def read_stream_pkl_data(stream_pkl_file_path):
    pkl_frames = []
    with open(stream_pkl_file_path, 'rb') as stream_file:
        while stream_file.seekable():
            try:
                pkl_frames.append(pickle.load(stream_file))
            except EOFError:
                break
    return pkl_frames


def get_nearest_timestamp(data, timestamp):
    n = len(data)
    if n <= 0:
        return None
    elif n == 1:
        return 0
    left, right = 0, n - 1

    while (right - left) > 1:
        i = (right + left) // 2
        t = data[i]
        if t < timestamp:
            left = i
        elif t > timestamp:
            right = i
        else:
            return i
    idx = left if (abs(data[left] - timestamp) < abs(data[right] - timestamp)) else right
    # Need to check the time difference must not be more than a second. If it is return None
    return None if (abs(data[idx] - timestamp) > 1e8) else idx


def get_timestamp_to_stream_frame(
        stream_directory,
        stream_extension,
        timestamp_index=-1
):
    stream_extension_length = len(stream_extension)
    stream_frames = [frame for frame in os.listdir(stream_directory) if frame.endswith(stream_extension)]

    def get_timestamp_from_stream_file_name(stream_file_name):
        _splits = (stream_file_name[:-stream_extension_length].split("_"))
        if _splits[timestamp_index] == "depth" or _splits[timestamp_index] == "ab":
            return int(_splits[timestamp_index - 1])
        return int(_splits[timestamp_index])

    stream_frames = sorted(stream_frames, key=lambda x: get_timestamp_from_stream_file_name(x))

    timestamp_to_stream_frame = {}
    for stream_frame in stream_frames:
        timestamp = get_timestamp_from_stream_file_name(stream_frame)
        timestamp_to_stream_frame[timestamp] = stream_frame

    return timestamp_to_stream_frame


class Synchronization:

    def __init__(
            self,
            base_stream: str,
            synchronize_streams: List[str],
            data_parent_directory: str,
            synchronized_parent_directory: str,
            recording: Recording
    ):
        self.base_stream = base_stream
        self.synchronize_streams = synchronize_streams
        self.data_parent_directory = data_parent_directory
        self.synchronized_parent_directory = synchronized_parent_directory
        self.recording = recording
        self.recording_id = self.recording.get_recording_id()

        self.data_directory = os.path.join(self.data_parent_directory, self.recording_id)
        self.synchronized_directory = self.synchronized_parent_directory

        self.base_stream_directory = os.path.join(self.data_directory, self.base_stream)
        self.synchronized_base_stream_directory = os.path.join(self.synchronized_directory, self.base_stream)

        self.timestamp_to_base_stream_frame = None
        self.base_stream_keys = None

        self.pv_stream_suffix = "color-%06d.jpg"
        self.depth_stream_suffix = "depth-%06d.png"
        self.vlc_stream_suffix = "vlc-%06d.jpg"

    def create_synchronized_stream_pkl_data(self, stream_pkl_file_path, synchronized_stream_output_directory):
        # 1. Load pickle file data into a dictionary
        timestamp_to_stream_payload = {}
        pkl_frames = read_stream_pkl_data(stream_pkl_file_path)
        for pkl_frame in pkl_frames:
            # TODO: Remove the else part after the pickle file is fixed
            ts, payload = pkl_frame if type(pkl_frame) is tuple else (pkl_frame.timestamp, pkl_frame.payload)
            if type(payload) is bytearray:
                payload = hl2ss.unpack_si(payload)
            timestamp_to_stream_payload[ts] = payload
        # 2. Use the base_stream_keys and loaded pickle file data to synchronize them
        stream_keys = sorted(timestamp_to_stream_payload.keys())
        synced_timestamp_to_stream_payload = {}
        for base_stream_key in self.base_stream_keys:
            stream_ts_idx = get_nearest_timestamp(stream_keys, base_stream_key)
            stream_timestamp = stream_keys[stream_ts_idx]
            stream_payload = timestamp_to_stream_payload[stream_timestamp]
            synced_timestamp_to_stream_payload[base_stream_key] = (stream_payload, stream_timestamp)
        # TODO: Add a logger statement here
        write_pickle_data(synced_timestamp_to_stream_payload, synchronized_stream_output_directory)

    def create_synchronized_stream_frames(self, stream_directory, stream_extension,
                                          synchronized_stream_output_directory, stream_suffix):
        timestamp_to_stream_frame = get_timestamp_to_stream_frame(stream_directory, stream_extension)
        stream_keys = sorted(timestamp_to_stream_frame.keys())

        for base_stream_counter, base_stream_key in enumerate(self.base_stream_keys):
            stream_ts_idx = get_nearest_timestamp(stream_keys, base_stream_key)
            stream_timestamp = stream_keys[stream_ts_idx]
            shutil.copy(os.path.join(stream_directory, timestamp_to_stream_frame[stream_timestamp]),
                        os.path.join(synchronized_stream_output_directory, stream_suffix % base_stream_counter))
        return

    # TODO: Complete code when Microphone data is considered as base stream for synchronization
    # --------- Base streams: PV, Microphone
    # --------- Synchronize Streams: PV, Depth-Ahat, Depth-Lt, Spatial, VLC frames
    # a. Depth cannot be base stream
    # b. If Microphone is base stream, we can duplicate frame and artificially increase frame rate of video
    # 1. Get base stream timestamps, associated files
    # 2. In a for loop, check for each of the synchronize streams
    # 3. Based on the stream, synchronize Pose, Payload -- if depth then synchronize ab and depth frames
    def sync_streams(self):
        if self.base_stream == ppc_const.PHOTOVIDEO:
            # 1. Create base stream keys used to synchronize the rest of the data
            base_stream_frames_dir = os.path.join(self.base_stream_directory, "frames")
            self.timestamp_to_base_stream_frame = get_timestamp_to_stream_frame(base_stream_frames_dir,
                                                                                stream_extension=".jpg",
                                                                                timestamp_index=-1)
            self.base_stream_keys = sorted(self.timestamp_to_base_stream_frame.keys())
            synchronized_frames_dir = os.path.join(self.synchronized_base_stream_directory, "frames")
            create_directories(synchronized_frames_dir)

            # 2. Copy base stream frames into the synchronized output folder
            for base_stream_counter, base_stream_key in enumerate(self.base_stream_keys):
                src_file = os.path.join(base_stream_frames_dir,
                                        self.timestamp_to_base_stream_frame[base_stream_key])
                dest_file = os.path.join(synchronized_frames_dir,
                                         self.pv_stream_suffix % base_stream_counter)
                shutil.copy(src_file, dest_file)
            # Synchronize PV Pose
            # pv_pose_pkl = f'{self.recording.id}_pv_pose.pkl'
            # pv_pose_file_path = os.path.join(self.base_stream_directory, pv_pose_pkl)
            # sync_pv_pose_file_path = os.path.join(self.synchronized_directory, pv_pose_pkl)
            # self.create_synchronized_stream_pkl_data(pv_pose_file_path, sync_pv_pose_file_path)

            for stream_name in self.synchronize_streams:
                if stream_name == ppc_const.DEPTH_AHAT:
                    depth_parent_directory = os.path.join(self.data_directory, ppc_const.DEPTH_AHAT)
                    synchronized_depth_parent_directory = os.path.join(self.synchronized_directory,
                                                                       ppc_const.DEPTH_AHAT)

                    # 1. Synchronize Pose
                    depth_ahat_pkl = f'{self.recording.id}_depth_ahat_pose.pkl'  # ToDo: Need to modify it to depth_ahat_pose.pkl
                    depth_pose_file_path = os.path.join(self.data_directory, depth_ahat_pkl)
                    sync_depth_pose_file_path = os.path.join(self.synchronized_directory, depth_ahat_pkl)
                    self.create_synchronized_stream_pkl_data(depth_pose_file_path, sync_depth_pose_file_path)

                    # 2. Synchronize Depth data
                    # ToDo: change it to DEPTH variables
                    ahat_depth_dir = f"depth_ahat"
                    depth_data_directory = os.path.join(self.data_directory, ahat_depth_dir)
                    # synchronized_depth_data_directory = os.path.join(synchronized_depth_parent_directory, DEPTH)
                    synchronized_depth_data_directory = os.path.join(self.synchronized_directory, ahat_depth_dir[4:])
                    create_directories(synchronized_depth_data_directory)
                    self.create_synchronized_stream_frames(depth_data_directory, ".png",
                                                           synchronized_depth_data_directory, self.depth_stream_suffix)

                    # 3. Synchronize Active Brightness data
                    # ToDo: change it to AB variables
                    ahat_ab_dir = f"dep_ahat_ab"
                    depth_ab_directory = os.path.join(self.data_directory, ahat_ab_dir)
                    # synchronized_depth_data_directory = os.path.join(synchronized_depth_parent_directory, DEPTH)
                    synchronized_depth_ab_directory = os.path.join(self.synchronized_directory, ahat_ab_dir[4:])
                    create_directories(synchronized_depth_ab_directory)
                    self.create_synchronized_stream_frames(depth_ab_directory, ".png",
                                                           synchronized_depth_ab_directory, self.depth_stream_suffix)

                elif stream_name == ppc_const.SPATIAL:
                    # 1. Synchronize spatial data
                    spatial_directory = os.path.join(self.data_directory, ppc_const.SPATIAL)
                    synchronized_spatial_directory = os.path.join(self.synchronized_directory, ppc_const.SPATIAL)
                    create_directories(synchronized_spatial_directory)
                    spatial_data_file = f'{self.recording.id}_spatial.pkl'
                    spatial_file_path = os.path.join(spatial_directory, spatial_data_file)
                    sync_spatial_file_path = os.path.join(synchronized_spatial_directory, spatial_data_file)
                    self.create_synchronized_stream_pkl_data(spatial_file_path, sync_spatial_file_path)
                elif stream_name in ppc_const.VLC_LIST:
                    # TODO: Add VLC frame synchronization code
                    logger.log(logging.ERROR, f"Need to implement the VLC Frames Sync Code")
                else:
                    logger.log(logging.ERROR, f"Cannot synchronize {stream_name} data with PV as base stream")
                    continue


def test_sync_pv_base():
    base_stream = ppc_const.PHOTOVIDEO
    # sync_streams = [ppc_const.DEPTH_AHAT, ppc_const.SPATIAL]
    sync_streams = [ppc_const.SPATIAL]
    data_parent_dir = "/home/ptg/CODE/data/hololens/"
    rec_ids = [
        "4_23",
        # "28_22",
    ]
    for rec_id in rec_ids:
        data_dir = os.path.join(data_parent_dir, rec_id)
        sync_parent_dir = os.path.join(data_dir, "sync")
        rec_instance = Recording(id=rec_id, activity_id=0, is_error=False, steps=[])
        pv_sync_stream = Synchronization(
            base_stream=base_stream,
            synchronize_streams=sync_streams,
            data_parent_directory=data_parent_dir,
            synchronized_parent_directory=sync_parent_dir,
            recording=rec_instance,
        )
        pv_sync_stream.sync_streams()


if __name__ == '__main__':
    test_sync_pv_base()
