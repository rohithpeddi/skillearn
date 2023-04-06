import shlex
import subprocess
import time


class ConvertGoProVideo:
    FFMPEG_PATH = '/usr/bin/ffmpeg'
    RES_360P = '360p'
    RES_720P = '720p'
    RES_1080P = '1080p'

    RES_MAP = {
        RES_360P: {
            'width': 640,
            'height': 360
        },
        RES_720P: {
            'width': 1280,
            'height': 720
        },
        RES_1080P: {
            'width': 1920,
            'height': 1080
        },
    }

    # Example:          ffmpeg -i -y -hwaccel cuda input_vd.MP4 -vf scale=640:360 -c:a copy output_vd.mp4
    # FFMPEG_COMMAND = 'ffmpeg -i -y -hwaccel cuda {input_file} -vf scale={scale} -c:a copy {output_file}'
    FFMPEG_COMMAND = '{} -y -hwaccel cuda -i {} -vf scale={} -c:a copy {}'

    def __init__(self, gopro_video_file, conversion_type=RES_360P, ffmpeg_path=FFMPEG_PATH):
        self.gopro_video_file = gopro_video_file
        self.conversion_type = conversion_type
        self.gopro_video_file_converted = self.gopro_video_file.replace('.MP4', f'_{self.conversion_type}.mp4')
        self.ffmpeg_path = ffmpeg_path
        pass

    def get_ffmpeg_scale(self):
        return f'{self.RES_MAP[self.conversion_type]["width"]}:{self.RES_MAP[self.conversion_type]["height"]}'

    def convert_gopro_video(self):
        convert_command = self.FFMPEG_COMMAND.format(
            self.ffmpeg_path,
            self.gopro_video_file,
            self.get_ffmpeg_scale(),
            self.gopro_video_file_converted,
        )
        start_time = time.time()
        print(f'FFMPEG command: {convert_command}')
        subprocess.call(shlex.split(convert_command))
        end_time = time.time()
        print(f'Conversion took {(end_time - start_time):.2f} seconds')


if __name__ == '__main__':
    cgv = ConvertGoProVideo(gopro_video_file='../../../../../data/gopro/4_23.MP4')
    cgv.convert_gopro_video()
