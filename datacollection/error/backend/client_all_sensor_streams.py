# ------------------------------------------------------------------------------
# This script records video from the HoloLens front RGB camera and audio from
# the HoloLens microphone to a mp4 file. Press space to start recording and esc
# to stop.
# ------------------------------------------------------------------------------
import queue
import threading
from fractions import Fraction

import av
import cv2
import numpy as np
from pynput import keyboard

import hl2ss

# Settings --------------------------------------------------------------------

# HoloLens address
HOLOLENS_IP = "192.168.1.149"

# Camera parameters
# See etc/hl2_capture_formats.txt for a list of supported formats.
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080
FRAMERATE = 30

# Video encoding profile
video_profile = hl2ss.VideoProfile.H265_MAIN

# Encoded video stream average bits per second
# Must be > 0
video_bitrate = 5 * 1024 * 1024
depth_bitrate = 8 * 1024 * 1024

# Decoded format
decoded_format = 'bgr24'

# Audio encoding profile
audio_profile = hl2ss.AudioProfile.AAC_24000

# Video filename
video_filename = '../frames/pv/pv_video.mp4'

depth_port = hl2ss.StreamPort.RM_DEPTH_AHAT
video_port = hl2ss.StreamPort.PERSONAL_VIDEO
# Operating mode
# 0: video
# 1: video + rig pose
# 2: query calibration (single transfer)
depth_mode = hl2ss.StreamMode.MODE_1
video_mode = hl2ss.StreamMode.MODE_1

# PNG filter
png_filter = hl2ss.PngFilterMode.Paeth

# ------------------------------------------------------------------------------

hl2ss.start_subsystem_pv(HOLOLENS_IP, hl2ss.StreamPort.PERSONAL_VIDEO)

tsfirst = None
enable = True
start_event = threading.Event()


def recv_pv(stream_video, lock, packetqueue, time_base, host, width, height, framerate, video_profile, video_bitrate):
    global tsfirst
    global enable

    codec_video = av.CodecContext.create(hl2ss.get_video_codec_name(video_profile), 'r')
    client = hl2ss.rx_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO, hl2ss.ChunkSize.PERSONAL_VIDEO,
                         hl2ss.StreamMode.MODE_0, width, height, framerate, video_profile, video_bitrate)
    client.open()

    while (enable):
        data = client.get_next_packet()
        lock.acquire()
        if (not tsfirst):
            tsfirst = data.timestamp
        lock.release()
        for packet in codec_video.parse(data.payload):
            packet.stream = stream_video
            packet.pts = data.timestamp - tsfirst
            packet.dts = packet.pts
            packet.time_base = time_base
            packetqueue.put((packet.pts, packet))

    client.close()


def recv_mc(stream_audio, lock, packetqueue, time_base, host, audio_profile):
    global tsfirst
    global enable

    codec_audio = av.CodecContext.create(hl2ss.get_audio_codec_name(audio_profile), 'r')
    client = hl2ss.rx_microphone(host, hl2ss.StreamPort.MICROPHONE, hl2ss.ChunkSize.MICROPHONE, audio_profile)
    client.open()

    while (enable):
        data = client.get_next_packet()
        lock.acquire()
        leave = tsfirst is None
        lock.release()
        if (leave):
            continue
        for packet in codec_audio.parse(data.payload):
            packet.stream = stream_audio
            packet.pts = data.timestamp - tsfirst
            packet.dts = packet.pts
            packet.time_base = time_base
            packetqueue.put((packet.pts, packet))

    client.close()


def recv_depth():
    global tsfirst
    global enable
    client = hl2ss.rx_decoded_rm_depth_ahat(HOLOLENS_IP, depth_port, hl2ss.ChunkSize.RM_DEPTH_AHAT, depth_mode, video_profile, depth_bitrate)
    client.open()

    while (enable):
        data = client.get_next_packet()
        lock.acquire()
        leave = tsfirst is None
        lock.release()
        if leave:
            continue
        print('Pose at time {ts}'.format(ts=data.timestamp))
        print(data.pose)
        cv2.imshow('Depth', data.payload.depth / np.max(data.payload.depth))  # Normalized for visibility
        cv2.imshow('AB', data.payload.ab / np.max(data.payload.ab))  # Normalized for visibility
        cv2.imwrite(f'../frames/depth/Depth_{data.timestamp}.png', data.payload.depth)
        cv2.imwrite(f'../frames/ab/AB_{data.timestamp}.png', data.payload.ab)
        cv2.waitKey(1)

    client.close()


def on_press(key):
    global start_event
    global enable

    # if (key == keyboard.Key.space):
    #     start_event.set()
    # elif (key == keyboard.Key.esc):
    #     enable = False

    return enable


listener = keyboard.Listener(on_press=on_press)
listener.start()

print('Press space to start recording')
# start_event.wait()
start_event.set()
print('Recording started')
print('Press esc to stop')

container = av.open(video_filename, 'w')
stream_video = container.add_stream(hl2ss.get_video_codec_name(video_profile), rate=FRAMERATE)
stream_audio = container.add_stream(hl2ss.get_audio_codec_name(audio_profile),
                                    rate=hl2ss.Parameters_MICROPHONE.SAMPLE_RATE)

lock = threading.Lock()
packetqueue = queue.PriorityQueue()
time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)

thread_pv = threading.Thread(target=recv_pv, args=(
    stream_video, lock, packetqueue, time_base, HOLOLENS_IP, CAMERA_WIDTH, CAMERA_HEIGHT, FRAMERATE, video_profile, video_bitrate))
thread_mc = threading.Thread(target=recv_mc, args=(stream_audio, lock, packetqueue, time_base, HOLOLENS_IP, audio_profile))
thread_depth = threading.Thread(target=recv_depth)

thread_pv.start()
thread_mc.start()
thread_depth.start()

while (enable):
    tuple = packetqueue.get()
    ts = tuple[0]
    container.mux(tuple[1])

container.close()

thread_pv.join()
thread_mc.join()
thread_depth.join()
listener.join()

print('Recording stopped')

hl2ss.stop_subsystem_pv(HOLOLENS_IP, hl2ss.StreamPort.PERSONAL_VIDEO)
