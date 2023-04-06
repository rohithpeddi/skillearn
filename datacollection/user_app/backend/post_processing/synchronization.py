import logging
import os
import pickle
import shutil
from typing import List

from ..hololens import hl2ss
from ..models.recording import Recording
from ..constants import Post_Processing_Constants as const
from ..logger_config import logger

UNIX_EPOCH = 11644473600


def create_directories(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def write_pickle_data(pickle_data, pickle_file_path):
    with open(pickle_file_path, 'wb') as pickle_file:
        pickle.dump(pickle_data, pickle_file)


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
        # self.synchronized_directory = os.path.join(self.synchronized_parent_directory, self.recording_id)
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
        with open(stream_pkl_file_path, 'rb') as stream_file:
            pkl_frames = pickle.load(stream_file)
            for pkl_frame in pkl_frames:
                ts, pose = pkl_frame
                if type(pose) is bytearray:
                    pose = hl2ss.unpack_si(pose)
                timestamp_to_stream_payload[ts] = pose
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
        if self.base_stream == const.PHOTOVIDEO:
            # 1. Create base stream keys used to synchronize the rest of the data
            self.timestamp_to_base_stream_frame = get_timestamp_to_stream_frame(self.base_stream_directory,
                                                                                stream_extension=".jpg",
                                                                                timestamp_index=-1)
            self.base_stream_keys = sorted(self.timestamp_to_base_stream_frame.keys())
            create_directories(self.base_stream_directory)
            create_directories(self.synchronized_base_stream_directory)

            # 2. Copy base stream frames into the synchronized output folder
            for base_stream_counter, base_stream_key in enumerate(self.base_stream_keys):
                src_file = os.path.join(self.base_stream_directory, self.timestamp_to_base_stream_frame[base_stream_key])
                dest_file = os.path.join(self.synchronized_base_stream_directory, self.pv_stream_suffix % base_stream_counter)
                shutil.copy(src_file, dest_file)
            # Synchronize PV Pose
            pv_pose_pkl = f'pv_pose.pkl'  # ToDo: Need to modify it to depth_ahat_pose.pkl
            pv_pose_file_path = os.path.join(self.data_directory, pv_pose_pkl)
            sync_pv_pose_file_path = os.path.join(self.synchronized_directory, pv_pose_pkl)
            self.create_synchronized_stream_pkl_data(pv_pose_file_path, sync_pv_pose_file_path)

            for stream_name in self.synchronize_streams:
                if stream_name == const.DEPTH_AHAT:
                    depth_parent_directory = os.path.join(self.data_directory, const.DEPTH_AHAT)
                    synchronized_depth_parent_directory = os.path.join(self.synchronized_directory, const.DEPTH_AHAT)

                    # 1. Synchronize Pose
                    depth_ahat_pkl = f'depth_pose.pkl'  # ToDo: Need to modify it to depth_ahat_pose.pkl
                    depth_pose_file_path = os.path.join(self.data_directory, depth_ahat_pkl)
                    sync_depth_pose_file_path = os.path.join(self.synchronized_directory, depth_ahat_pkl)
                    self.create_synchronized_stream_pkl_data(depth_pose_file_path, sync_depth_pose_file_path)

                    # 2. Synchronize Depth data
                    # ToDo: change it to DEPTH variables
                    ahat_depth_dir = f"dep_ahat_depth"
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

                elif stream_name == const.SPATIAL:
                    # 1. Synchronize spatial data
                    spatial_directory = os.path.join(self.data_directory, const.SPATIAL)
                    synchronized_spatial_directory = os.path.join(self.synchronized_directory, const.SPATIAL)
                    create_directories(synchronized_spatial_directory)
                    spatial_data_file = f'spatial_data.pkl'
                    spatial_file_path = os.path.join(spatial_directory, spatial_data_file)
                    sync_spatial_file_path = os.path.join(synchronized_spatial_directory, spatial_data_file)
                    self.create_synchronized_stream_pkl_data(spatial_file_path, sync_spatial_file_path)
                elif stream_name in const.VLC_LIST:
                    # TODO: Add VLC frame synchronization code
                    logger.log(logging.ERROR, f"Need to implement the VLC Frames Sync Code")
                else:
                    logger.log(logging.ERROR, f"Cannot synchronize {stream_name} data with PV as base stream")
                    continue


def test_sync_pv_base():
    base_stream = const.PHOTOVIDEO
    sync_streams = [const.DEPTH_AHAT, const.SPATIAL]
    data_parent_dir = "/home/bxc200008/Projects/PyCharm/data/mugpizza/SAMPLE/"
    rec_ids = [
        "MugPizza_PL2_P2_R1_0",
        "MugPizza_PL2_P4_R1_0",
        "MugPizza_PL2_P5_R1_0",
        "MugPizza_PL2_P7_R1_0",
    ]
    for rec_id in rec_ids:
        data_dir = os.path.join(data_parent_dir, rec_id)
        sync_parent_dir = os.path.join(data_dir, "sync")
        rec_instance_helper = rec_id.split('_')
        rec_instance = Recording(*rec_instance_helper[:-1], is_error=bool(int(rec_instance_helper[-1])))
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
