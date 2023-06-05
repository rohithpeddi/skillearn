import time
from datetime import datetime, timedelta

from moviepy.editor import VideoFileClip
import os

import subprocess


def execute_ffmpeg_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if process.returncode != 0:
        raise Exception(f'Error executing ffmpeg command: {command}\n{error}')
    else:
        return output, error


def convert_seconds_to_ffmpeg_time(seconds):
    delta = timedelta(seconds=seconds)
    time = datetime(1, 1, 1) + delta
    ffmpeg_time = time.strftime("%H:%M:%S.%f")[:-3]
    return ffmpeg_time


def build_ffmpeg_splice_command(input_video_path, start_time, clip_length, output_video_path):
    start_time = convert_seconds_to_ffmpeg_time(start_time)
    clip_length = convert_seconds_to_ffmpeg_time(clip_length)
    command = f"ffmpeg -ss {start_time} -t {clip_length} -i {input_video_path} -c copy {output_video_path}"
    return command


def splice_video(video_path, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    video = VideoFileClip(video_path)
    duration = video.duration

    num_intervals = int(duration // 5)

    for i in range(num_intervals):
        start = i * 5
        end = (i + 1) * 5

        clip_length = min(duration-start, end - start)

        print(f'Splicing {video_path} from {start} to {end}...')

        output_file_name = f'12_2_{i}.mp4'
        output_file_path = os.path.join(output_directory, output_file_name)

        command = build_ffmpeg_splice_command(video_path, start, clip_length, output_file_path)

        execute_ffmpeg_command(command)
        time.sleep(1)


if __name__ == '__main__':
    video_path = '/home/rxp190007/DATA/ANNOTATION/12_2/12_2_360p.mp4'
    output_directory = '/home/rxp190007/DATA/ANNOTATION/12_2/12_2_360p_spliced'
    splice_video(video_path, output_directory)
