# ------------------------------------------------------------------------------
# This script records video from the HoloLens front RGB camera and audio from
# the HoloLens microphone to a mp4 file. Press space to start recording and esc
# to stop.
# ------------------------------------------------------------------------------
import multiprocessing as mp
import os
import queue
import threading
import time
from fractions import Fraction

import av
import cv2
import numpy as np
from pynput import keyboard

import datacollection.error.backend.hl2ss as hl2ss
import datacollection.error.backend.hl2ss_mp as hl2ss_mp

# Settings --------------------------------------------------------------------
tsFirst = None
rm_pv_enable = True
rm_vlc_depth_enable = True
start_event = threading.Event()

# HoloLens address
HOLOLENS_IP = "192.168.10.133"

# Camera parameters
# See etc/hl2_capture_formats.txt for a list of supported formats.
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080
FRAMERATE = 30

# Video encoding profile
# video_profile = hl2ss.VideoProfile.H265_MAIN
video_profile = hl2ss.VideoProfile.H264_BASE

# Encoded video stream average bits per second
# Must be > 0
video_bitrate = 5 * 1024 * 1024

# Decoded format
decoded_format = 'bgr24'

# Audio encoding profile
audio_profile = hl2ss.AudioProfile.AAC_24000

# Video filename
video_filename = '../frames/pv_video.mp4'
video_port = hl2ss.StreamPort.PERSONAL_VIDEO
# Operating mode
# 0: video
# 1: video + rig pose
# 2: query calibration (single transfer)
video_mode = hl2ss.StreamMode.MODE_1

# Ports
ports = [
    # hl2ss.StreamPort.PERSONAL_VIDEO,
    hl2ss.StreamPort.RM_VLC_LEFTFRONT,
    hl2ss.StreamPort.RM_VLC_LEFTLEFT,
    hl2ss.StreamPort.RM_VLC_RIGHTFRONT,
    hl2ss.StreamPort.RM_VLC_RIGHTRIGHT,
    hl2ss.StreamPort.RM_DEPTH_AHAT,
    hl2ss.StreamPort.RM_DEPTH_LONGTHROW
]

# RM VLC parameters
vlc_mode = hl2ss.StreamMode.MODE_1
vlc_profile = hl2ss.VideoProfile.H264_BASE
vlc_bitrate = 1 * 1024 * 1024

# RM Depth AHAT parameters
ahat_mode = hl2ss.StreamMode.MODE_1
ahat_profile = hl2ss.VideoProfile.H264_BASE
ahat_bitrate = 8 * 1024 * 1024

# RM Depth Long Throw parameters
lt_mode = hl2ss.StreamMode.MODE_1
lt_filter = hl2ss.PngFilterMode.Paeth

# PV parameters
pv_mode = hl2ss.StreamMode.MODE_1
# pv_width = 1280
# pv_height = 720
pv_width = CAMERA_WIDTH
pv_height = CAMERA_HEIGHT
pv_framerate = 30
pv_profile = hl2ss.VideoProfile.H265_MAIN
pv_bitrate = 5 * 1024 * 1024
pv_format = 'bgr24'

# Maximum number of frames in buffer
buffer_elements = 300


# ------------------------------------------------------------------------------


def recv_pv(stream_video, lock, packetqueue, time_base, host, width, height, framerate, video_profile, video_bitrate):
    global tsFirst
    global rm_pv_enable

    codec_video = av.CodecContext.create(hl2ss.get_video_codec_name(video_profile), 'r')
    client = hl2ss.rx_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO, hl2ss.ChunkSize.PERSONAL_VIDEO,
                         hl2ss.StreamMode.MODE_0, width, height, framerate, video_profile, video_bitrate)
    client.open()

    while (rm_pv_enable):
        data = client.get_next_packet()
        lock.acquire()
        if (not tsFirst):
            tsFirst = data.timestamp
        lock.release()
        for packet in codec_video.parse(data.payload):
            packet.stream = stream_video
            packet.pts = data.timestamp - tsFirst
            packet.dts = packet.pts
            packet.time_base = time_base
            packetqueue.put((packet.pts, packet))
    client.close()


def recv_mc(stream_audio, lock, packetqueue, time_base, host, audio_profile):
    global tsFirst
    global rm_pv_enable

    codec_audio = av.CodecContext.create(hl2ss.get_audio_codec_name(audio_profile), 'r')
    client = hl2ss.rx_microphone(host, hl2ss.StreamPort.MICROPHONE, hl2ss.ChunkSize.MICROPHONE, audio_profile)
    client.open()

    while (rm_pv_enable):
        data = client.get_next_packet()
        lock.acquire()
        leave = tsFirst is None
        lock.release()
        if (leave):
            continue
        for packet in codec_audio.parse(data.payload):
            packet.stream = stream_audio
            packet.pts = data.timestamp - tsFirst
            packet.dts = packet.pts
            packet.time_base = time_base
            packetqueue.put((packet.pts, packet))

    client.close()


def on_press(key):
    global start_event
    global rm_pv_enable
    global rm_vlc_depth_enable

    if (key == keyboard.Key.space):
        start_event.set()
    elif (key == keyboard.Key.esc):
        time.sleep(1)
        rm_vlc_depth_enable = False
        rm_pv_enable = False
    return rm_pv_enable


def update_recording_status(key):
    global rm_pv_enable
    global rm_vlc_depth_enable

    time.sleep(1)
    rm_vlc_depth_enable = False
    rm_pv_enable = False

    return rm_pv_enable


def display_basic(port, data, video_writer, display=False):
    port_name = hl2ss.get_port_name(port)
    if display:
        cv2.imshow(port_name, data.payload)
    if video_writer is not None:
        video_writer.write(data.payload)
        return
    if port == hl2ss.StreamPort.PERSONAL_VIDEO:
        cv2.imwrite(f'../frames/pv/{port_name}_{data.timestamp}.png', data.payload)
    else:
        cv2.imwrite(f'../frames/vlc/{port_name}_{data.timestamp}.png', data.payload)


def display_depth(port, data, video_writer=None, display=False):
    port_name = hl2ss.get_port_name(port)
    if display:
        cv2.imshow(port_name + '-depth', data.payload.depth * 8)  # Scaled for visibility
        cv2.imshow(port_name + '-ab', data.payload.ab / np.max(data.payload.ab))  # Normalized for visibility
    cv2.imwrite(f'../frames/depth/{port_name}_{data.timestamp}.png', data.payload.depth)
    cv2.imwrite(f'../frames/ab/{port_name}_{data.timestamp}.png', data.payload.ab)


def mux_audio_video(packetqueue, container):
    global rm_pv_enable
    while (rm_pv_enable):
        tuple = packetqueue.get()
        ts = tuple[0]
        container.mux(tuple[1])


def record_rm_vlc_depth(lock, sinks, DISPLAY_MAP, WRITERS_MAP):
    global tsFirst
    global rm_vlc_depth_enable

    while (rm_vlc_depth_enable):
        lock.acquire()
        leave = tsFirst is None
        lock.release()
        if (leave):
            continue
        for port in ports:
            data = sinks[port].get_most_recent_frame()
            if (data is not None):
                DISPLAY_MAP[port](port, data, WRITERS_MAP[port])
        cv2.waitKey(1)


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def create_frames_dirs(parent_dir):
    # parent_dir = '../frames'
    create_dir(os.path.join(parent_dir, 'ab'))
    create_dir(os.path.join(parent_dir, 'depth'))
    # create_dir(os.path.join(parent_dir, 'pv'))
    # create_dir(os.path.join(parent_dir, 'vlc'))


def hl2_record_sensor_streams(recording_path, hololens_ip=None, keyboard_listener=False):
    global HOLOLENS_IP
    if hololens_ip is not None:
        HOLOLENS_IP = hololens_ip
    create_frames_dirs(recording_path)
    DISPLAY_MAP = {
        hl2ss.StreamPort.RM_VLC_LEFTFRONT: display_basic,
        hl2ss.StreamPort.RM_VLC_LEFTLEFT: display_basic,
        hl2ss.StreamPort.RM_VLC_RIGHTFRONT: display_basic,
        hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: display_basic,
        hl2ss.StreamPort.RM_DEPTH_AHAT: display_depth,
        hl2ss.StreamPort.RM_DEPTH_LONGTHROW: display_depth,
        hl2ss.StreamPort.PERSONAL_VIDEO: display_basic
    }

    # Research Mode Visible Light Cameras (4 cameras, 640x480 @ 30 FPS, Grayscale, H264 or HEVC encoded)
    # Ref: https://stackoverflow.com/questions/50037063/save-grayscale-video-in-opencv
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPG # case-sensitive Codecs
    vlc_fourcc = cv2.VideoWriter_fourcc(*'H264')  # mp4v, H264, DIVX # case-sensitive Codecs
    vlc_fps = 30
    vlc_width = 640
    vlc_height = 480
    WRITERS_MAP = {
        hl2ss.StreamPort.RM_VLC_LEFTFRONT: cv2.VideoWriter(os.path.join(recording_path, 'vlc_lf.mp4'), vlc_fourcc, vlc_fps,
                                                           (vlc_width, vlc_height), 0),
        hl2ss.StreamPort.RM_VLC_LEFTLEFT: cv2.VideoWriter(os.path.join(recording_path, 'vlc_ll.mp4'), vlc_fourcc, vlc_fps,
                                                          (vlc_width, vlc_height), 0),
        hl2ss.StreamPort.RM_VLC_RIGHTFRONT: cv2.VideoWriter(os.path.join(recording_path, 'vlc_rf.mp4'), vlc_fourcc,
                                                            vlc_fps, (vlc_width, vlc_height), 0),
        hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: cv2.VideoWriter(os.path.join(recording_path, 'vlc_rr.mp4'), vlc_fourcc,
                                                            vlc_fps, (vlc_width, vlc_height), 0),
        hl2ss.StreamPort.RM_DEPTH_AHAT: None,
        # cv2.VideoWriter(os.path.join(folder_path, 'depth_ahat.avi'), fourcc, fps, (width, height)),
        hl2ss.StreamPort.RM_DEPTH_LONGTHROW: None,
        # cv2.VideoWriter(os.path.join(folder_path, 'depth_lt.avi'), fourcc, fps, (width, height)),
        hl2ss.StreamPort.PERSONAL_VIDEO: None,
        # cv2.VideoWriter(os.path.join(folder_path, 'pv.mp4'), fourcc, fps, (width, height)),
    }

    listener = None
    if keyboard_listener:
        listener = keyboard.Listener(on_press=on_press, args=())
        listener.start()

    client_rc = hl2ss.tx_rc(HOLOLENS_IP, hl2ss.IPCPort.REMOTE_CONFIGURATION)
    hl2ss.start_subsystem_pv(HOLOLENS_IP, hl2ss.StreamPort.PERSONAL_VIDEO)
    client_rc.wait_for_pv_subsystem(True)

    producer = hl2ss_mp.producer()
    producer.configure_rm_vlc(True, HOLOLENS_IP, hl2ss.StreamPort.RM_VLC_LEFTFRONT, hl2ss.ChunkSize.RM_VLC, vlc_mode,
                              vlc_profile, vlc_bitrate)
    producer.configure_rm_vlc(True, HOLOLENS_IP, hl2ss.StreamPort.RM_VLC_LEFTLEFT, hl2ss.ChunkSize.RM_VLC, vlc_mode,
                              vlc_profile, vlc_bitrate)
    producer.configure_rm_vlc(True, HOLOLENS_IP, hl2ss.StreamPort.RM_VLC_RIGHTFRONT, hl2ss.ChunkSize.RM_VLC, vlc_mode,
                              vlc_profile, vlc_bitrate)
    producer.configure_rm_vlc(True, HOLOLENS_IP, hl2ss.StreamPort.RM_VLC_RIGHTRIGHT, hl2ss.ChunkSize.RM_VLC, vlc_mode,
                              vlc_profile, vlc_bitrate)
    producer.configure_rm_depth_ahat(True, HOLOLENS_IP, hl2ss.StreamPort.RM_DEPTH_AHAT, hl2ss.ChunkSize.RM_DEPTH_AHAT,
                                     ahat_mode, ahat_profile, ahat_bitrate)
    producer.configure_rm_depth_longthrow(True, HOLOLENS_IP, hl2ss.StreamPort.RM_DEPTH_LONGTHROW,
                                          hl2ss.ChunkSize.RM_DEPTH_LONGTHROW, lt_mode, lt_filter)
    producer.configure_pv(True, HOLOLENS_IP, hl2ss.StreamPort.PERSONAL_VIDEO, hl2ss.ChunkSize.PERSONAL_VIDEO, pv_mode,
                          pv_width, pv_height, pv_framerate, pv_profile, pv_bitrate, pv_format)

    for port in ports:
        producer.initialize(port, buffer_elements)
        producer.start(port)

    manager = mp.Manager()
    consumer = hl2ss_mp.consumer()
    sinks = {}

    for port in ports:
        sinks[port] = consumer.create_sink(producer, port, manager, None)
        sinks[port].get_attach_response()

    container = av.open(video_filename, 'w')
    stream_video = container.add_stream(hl2ss.get_video_codec_name(video_profile), rate=FRAMERATE)
    stream_audio = container.add_stream(hl2ss.get_audio_codec_name(audio_profile),
                                        rate=hl2ss.Parameters_MICROPHONE.SAMPLE_RATE)

    lock = threading.Lock()
    packetqueue = queue.PriorityQueue()
    time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)

    thread_pv = threading.Thread(target=recv_pv, args=(
        stream_video, lock, packetqueue, time_base, HOLOLENS_IP, CAMERA_WIDTH, CAMERA_HEIGHT, FRAMERATE, video_profile,
        video_bitrate))
    thread_mc = threading.Thread(target=recv_mc,
                                 args=(stream_audio, lock, packetqueue, time_base, HOLOLENS_IP, audio_profile))
    thread_mux = threading.Thread(target=mux_audio_video, args=(packetqueue, container))
    thread_rm_record = threading.Thread(target=record_rm_vlc_depth, args=(lock, sinks, DISPLAY_MAP, WRITERS_MAP))

    if keyboard_listener:
        print('Press space to start recording')
        start_event.wait()
        print('Recording started')
        print('Press esc to stop')
    else:
        print('Recording started')

    thread_pv.start()
    thread_mc.start()

    thread_mux.start()
    # thread_rm_record.start()

    while (rm_vlc_depth_enable):
        if tsFirst is None:
            continue
        for port in ports:
            data = sinks[port].get_most_recent_frame()
            if (data is not None):
                DISPLAY_MAP[port](port, data, WRITERS_MAP[port])
        cv2.waitKey(1)

    # thread_rm_record.join()
    for port in ports:
        if WRITERS_MAP[port] is None:
            continue
        WRITERS_MAP[port].release()
    container.close()

    for port in ports:
        sinks[port].detach()

    for port in ports:
        producer.stop(port)

    thread_pv.join()
    thread_mc.join()
    thread_mux.join()

    hl2ss.stop_subsystem_pv(HOLOLENS_IP, hl2ss.StreamPort.PERSONAL_VIDEO)
    client_rc.wait_for_pv_subsystem(False)

    if keyboard_listener:
        listener.join()

    print('Recording stopped')


if __name__ == '__main__':
    hl2_record_sensor_streams(recording_path='../frames', keyboard_listener=True)
