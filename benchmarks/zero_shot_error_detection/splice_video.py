from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os


def splice_video(video_path, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    video = VideoFileClip(video_path)
    duration = video.duration

    num_intervals = int(duration // 5)

    for i in range(num_intervals):
        start = i * 5
        end = min(duration, (i + 1) * 5)

        output_file_name = f'12_2_{i}.mp4'
        output_file_path = os.path.join(output_directory, output_file_name)

        ffmpeg_extract_subclip(video_path, start, end, targetname=output_file_path)


if __name__ == '__main__':
    video_path = '/home/rxp190007/DATA/ANNOTATION/12_2/12_2_360p.mp4'
    output_directory = '/home/rxp190007/DATA/ANNOTATION/12_2/12_2_360p_spliced'
    splice_video(video_path, output_directory)
