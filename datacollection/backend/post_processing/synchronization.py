import os
import pickle
import shutil
from fractions import Fraction

import av
import cv2

from datacollection.backend import hl2ss

UNIX_EPOCH = 11644473600


def create_directories(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def load_pkl_data(pkl_path):
    with open(pkl_path, 'rb') as f:
        pkl_data = pickle.load(f)
    return pkl_data


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


def get_frames_timestamps(image_dir_path, img_ext=".jpg"):
    images = [img for img in os.listdir(image_dir_path) if img.endswith(img_ext)]
    images = sorted(images, key=lambda x: int((x[:-4].split("_"))[-1]))
    img_ts_dict = {}
    for img_path in images:
        ts = int((img_path[:-4].split("_"))[-1])
        img_ts_dict[ts] = img_path
    return img_ts_dict


def get_depth_timestamps(image_dir_path, img_ext=".png"):
    images = [img for img in os.listdir(image_dir_path) if img.endswith(img_ext)]
    images = sorted(images, key=lambda x: int((x[:-4].split("_"))[-2]))
    img_ts_dict = {}
    for img_path in images:
        ts = int((img_path[:-4].split("_"))[-2])
        img_ts_dict[ts] = img_path
    return img_ts_dict


def sync_pkl_data(sync_keys, pkl_data_list):
    pkl_data_ts_sync = {}
    pkl_ts_data = {}
    for data in pkl_data_list:
        pkl_ts_data[data[0]] = data[1]
    pkl_keys = sorted(pkl_ts_data.keys())
    for sync_key in sync_keys:
        pkl_ts_idx = get_nearest_timestamp(pkl_keys, sync_key)
        pkl_ts = pkl_keys[pkl_ts_idx]
        pkl_data = pkl_ts_data[pkl_ts]
        pkl_data_ts_sync[sync_key] = (pkl_data, pkl_ts)
    print(f"{len(pkl_data_list)} -> {len(pkl_data_ts_sync)}")
    return pkl_data_ts_sync


def sync_pose_with_pv(data_dir_path):
    data_poses = [
        'depth',
        'pv',
        'rm_vlc_leftleft',
        'rm_vlc_leftfront',
        'rm_vlc_rightfront',
        'rm_vlc_rightright',
    ]
    pv_dir_path = os.path.join(data_dir_path, "pv")
    pv_images = get_frames_timestamps(pv_dir_path)
    sync_dir_path = os.path.join(data_dir_path, 'sync')
    print(len(pv_images))
    for pose_data in data_poses:
        pose_data_path = os.path.join(data_dir_path, f'{pose_data}_pose.pkl')
        sync_pose_data_path = os.path.join(sync_dir_path, f'{pose_data}_pose.pkl')
        pkl_data_list = load_pkl_data(pose_data_path)
        pv_keys = sorted(pv_images.keys())
        pkl_data_ts_sync = sync_pkl_data(pv_keys, pkl_data_list)
        with open(sync_pose_data_path, 'wb') as f:
            pickle.dump(pkl_data_ts_sync, f)
    pass


def sync_data_with_pv(data_dir_path):
    vlc_dirs = ['vlc_ll', 'vlc_lf', 'vlc_rf', 'vlc_rr', ]
    pv_dir_path = os.path.join(data_dir_path, "pv")
    depth_dir_path = os.path.join(data_dir_path, "dep_ahat_depth")
    pv_images = get_frames_timestamps(pv_dir_path)
    depth_images = get_depth_timestamps(depth_dir_path)
    print(len(pv_images))
    print(len(depth_images))
    vlc_images_list = []
    for vlc_dir in vlc_dirs:
        vlc_images_list.append(get_frames_timestamps(os.path.join(data_dir_path, vlc_dir)))
        print(len(vlc_images_list[-1]))

    pv_depth_ts_sync = {}
    pv_keys = sorted(pv_images.keys())
    depth_keys = sorted(depth_images.keys())
    vlc_sorted_keys = [sorted(vlc_img.keys()) for vlc_img in vlc_images_list]
    for pv_key in pv_keys:
        dep_ts_idx = get_nearest_timestamp(depth_keys, pv_key)
        dep_ts = depth_keys[dep_ts_idx]
        pv_image, depth_image = pv_images[pv_key], depth_images[dep_ts]
        vlc_timestamps = []
        vlc_images = []
        for i in range(len(vlc_sorted_keys)):
            vlc_ts_idx = get_nearest_timestamp(vlc_sorted_keys[i], pv_key)
            vlc_timestamps.append(vlc_sorted_keys[i][vlc_ts_idx])
            vlc_images.append(vlc_images_list[i][vlc_sorted_keys[i][vlc_ts_idx]])
        pv_depth_ts_sync[pv_key] = (pv_image, depth_image, dep_ts, *vlc_images, *vlc_timestamps)
    print(len(pv_depth_ts_sync))

    sync_dir_path = os.path.join(data_dir_path, 'sync')
    depth_sync_path = os.path.join(sync_dir_path, 'depth')
    pv_sync_path = os.path.join(sync_dir_path, 'pv')
    create_directories(pv_sync_path)
    create_directories(depth_sync_path)
    vlc_dir_paths = []
    vlc_sync_paths = []
    for i in range(4):
        vlc_dir_paths.append(os.path.join(data_dir_path, vlc_dirs[i]))
        vlc_sync_paths.append(os.path.join(sync_dir_path, vlc_dirs[i]))
        create_directories(vlc_sync_paths[i])
    # Need to make a copy of the depth image
    idx = 0
    for pv_key in pv_keys:
        pv_jpg = pv_depth_ts_sync[pv_key][0]
        dep_png = pv_depth_ts_sync[pv_key][1]
        # dep_png = dep_png[:-21] + str(pv_key) + "_depth.png"
        sync_pv_jpg = "color-%06d.jpg"
        sync_dep_png = "depth-%06d.png"
        sync_vlc_jpg = "vlc-%06d.jpg"
        shutil.copy(os.path.join(pv_dir_path, pv_jpg), os.path.join(pv_sync_path, sync_pv_jpg % idx))
        shutil.copy(os.path.join(depth_dir_path, dep_png), os.path.join(depth_sync_path, sync_dep_png % idx))
        for i in range(4):
            vlc_jpg = pv_depth_ts_sync[pv_key][3 + i]
            shutil.copy(os.path.join(vlc_dir_paths[i], vlc_jpg), os.path.join(vlc_sync_paths[i], sync_vlc_jpg % idx))
        idx += 1


def mux_audio_video(data_dir_path):
    time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)
    pv_dir_path = os.path.join(data_dir_path, "pv")
    mc_dir_path = os.path.join(data_dir_path, "mc")
    pv_images = get_frames_timestamps(pv_dir_path)
    audio_data_list = load_pkl_data(os.path.join(mc_dir_path, "audio_data.pkl"))
    print(len(pv_images))
    print(len(audio_data_list))

    # pv_audio_ts_sync = {}
    # pv_keys = sorted(pv_images.keys())
    # audio_data = {}
    # for data in audio_data_list:
    #     audio_data[data[0]] = data[1]
    # audio_keys = sorted(audio_data.keys())
    # for pv_key in pv_keys:
    #     audio_ts_idx = get_nearest_timestamp(audio_keys, pv_key)
    #     audio_ts = audio_keys[audio_ts_idx]
    #     pv_image, audio_bytes = pv_images[pv_key], audio_data[audio_ts]
    #     pv_audio_ts_sync[pv_key] = (pv_image, audio_bytes, audio_ts)
    pv_audio_ts_sync = sync_pkl_data()
    print(len(pv_audio_ts_sync))

    sync_path = os.path.join(data_dir_path, "sync")
    create_directories(sync_path)
    video_path = os.path.join(sync_path, "video_mux.mp4")
    container = av.open(video_path, 'w')
    # Video encoding profile
    video_profile = hl2ss.VideoProfile.H264_HIGH
    framerate = 30
    # Audio encoding profile
    audio_profile = hl2ss.AudioProfile.AAC_24000
    stream_audio = container.add_stream(
        hl2ss.get_audio_codec_name(audio_profile), rate=hl2ss.Parameters_MICROPHONE.SAMPLE_RATE)
    stream_video = container.add_stream(
        hl2ss.get_video_codec_name(video_profile), rate=framerate)

    video_format = 'bgr24'

    codec_video = av.CodecContext.create(hl2ss.get_video_codec_name(video_profile), 'r')
    codec_audio = av.CodecContext.create(hl2ss.get_audio_codec_name(audio_profile), 'r')
    pv_timestamps = list(pv_images.keys())
    tsfirst = pv_timestamps[0]
    tslast = pv_timestamps[-1]

    # Audio PV sync feed is not continuous and doesn't work
    # for pv_key in pv_audio_ts_sync.keys():
    #     for packet in codec_audio.parse((pv_audio_ts_sync[pv_key][1])):
    #         packet.stream = stream_audio
    #         packet.pts = pv_key - tsfirst
    #         packet.dts = packet.pts
    #         packet.time_base = time_base
    #         container.mux(packet)
    #     pv_img = cv2.imread(os.path.join(pv_dir_path, pv_images[pv_key]))
    #     cv2.imshow('image', pv_img)
    #     cv2.waitKey(1)
    #     av_frame = av.VideoFrame.from_ndarray(pv_img, format=video_format)
    #     packet = stream_video.encode(av_frame)
    #     if packet is not None:
    #         container.mux(packet)

    # Audio Feed is continuous
    for audio_data in audio_data_list:
        ts = audio_data[0]
        if ts < tsfirst or ts > tslast:
            continue
        for packet in codec_audio.parse((audio_data[1])):
            packet.stream = stream_audio
            packet.pts = ts - tsfirst
            packet.dts = packet.pts
            packet.time_base = time_base
            container.mux(packet)

    count = 0
    for pv_image_key in pv_images.keys():
        pv_img = cv2.imread(os.path.join(pv_dir_path, pv_images[pv_image_key]))
        pv_img = pv_img.astype(pv_img.dtype, order='C', copy=False)
        cv2.imshow('image', pv_img)
        cv2.waitKey(1)
        av_frame = av.VideoFrame.from_ndarray(pv_img, format=video_format)
        # av_frame.pts = pv_image_key - tsfirst
        # av_frame.time_base = time_base
        packet = stream_video.encode(av_frame)
        if packet is not None:
            container.mux(packet)
        count += 1
        # if count > 1000:
        #     break

    # Finish encoding the stream
    while True:
        try:
            packet = stream_video.encode()
        except av.AVError:  # End of file raises AVError since after av 0.4
            break
        if packet is None:
            break
        container.mux(packet)
    container.close()


def sync_data():
    root_path = "/home/bxc200008/Projects/PyCharm/skillearn/data/mugpizza/SAMPLE/"
    data_paths = [
        'MugPizza_PL2_P2_R1',
        'MugPizza_PL2_P4_R1',
        'MugPizza_PL2_P5_R1',
        'MugPizza_PL2_P7_R1',
    ]
    for data_path in data_paths:
        data_dir_path = os.path.join(root_path, data_path)
        mux_audio_video(data_dir_path)
        sync_pose_with_pv(data_dir_path)
        sync_data_with_pv(data_dir_path)


def main():
    data_dir_path = "~/Projects/PyCharm/skillearn/data/Coffee_PL1_P1_R5"
    # data_dir_path = "~/Projects/PyCharm/skillearn/data/Coffee_P1_P1_R1/"
    # data_dir_path = "~/Projects/PyCharm/skillearn/data/mugpizza/SAMPLE/MugPizza_PL2_P2_R1/"
    # data_dir_path = "~/Projects/PyCharm/skillearn/data/mugpizza/SAMPLE/MugPizza_PL2_P4_R1/"
    # sync_data_with_pv(data_dir_path)
    # mux_audio_video(data_dir_path)
    # sync_pose_with_pv(data_dir_path)
    sync_data()


if __name__ == '__main__':
    main()
