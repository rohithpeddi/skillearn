import copy
import json
import os
import os.path as osp
import shutil
from moviepy.editor import VideoFileClip
import os


def slice_video(video_file_path, recording_id, output_directory,
                max_duration=18 * 60):  # default max duration is 18 minutes (in seconds)
    # Load the video
    clip = VideoFileClip(video_file_path)

    # Get the video duration
    video_duration = clip.duration

    # If video duration is less than or equal to max_duration, no slicing is needed
    difference = round(video_duration) - max_duration
    if difference <= 60:
        print(f"[{recording_id}] Video duration is within the limit.")
        return
    # Calculate the number of slices needed
    num_slices = int(video_duration // max_duration)
    remainder_duration = video_duration % max_duration

    print("------------------------------------------------------------------")
    print(f"[{recording_id}] Slicing video into {num_slices + 1} parts")

    # Slice the video into max_duration parts
    for i in range(num_slices):
        start_time = i * max_duration
        end_time = (i + 1) * max_duration

        sliced_clip = clip.subclip(start_time, end_time)
        output_file = os.path.join(output_directory, f"{recording_id}_sliced_{i + 1}.mp4")
        sliced_clip.write_videofile(output_file, codec='libx264', audio_codec='aac',
                                    ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'ultrafast'])
        print(f"Saved {output_file}")

    # If there's any remainder video, save that too
    if remainder_duration > 0:
        start_time = num_slices * max_duration
        end_time = video_duration

        sliced_clip = clip.subclip(start_time, end_time)
        output_file = os.path.join(output_directory, f"{recording_id}_sliced_{num_slices + 1}.mp4")
        sliced_clip.write_videofile(output_file, codec='libx264', audio_codec='aac',
                                    ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'ultrafast'])
        print(f"Saved {output_file}")

    print("Deleting original video")
    os.remove(video_file_path)


def slice_longer_videos(base_path, videos_type="normal_error"):
    videos_path = osp.join(base_path, videos_type, "videos")
    for data_type in ["train", "val", "test"]:
        videos_data_path = osp.join(videos_path, data_type)
        for category in os.listdir(videos_data_path):
            category_videos_directory_path = osp.join(videos_data_path, category)
            for video in os.listdir(category_videos_directory_path):
                video_path = osp.join(category_videos_directory_path, video)
                recording_id = video.replace(".mp4", "")
                slice_video(video_path, recording_id, category_videos_directory_path)


def fetch_sliced_recording_annotation(start_time, end_time, sliced_recording_id, recording_id):
    sliced_recording_annotation_dict = dict()
    sliced_recording_annotation_dict['recording_id'] = sliced_recording_id
    sliced_recording_annotation_dict['steps'] = []
    step_annotations_copy = copy.deepcopy(step_annotations)
    for step_annotation in step_annotations_copy[recording_id]['steps']:
        if step_annotation['start_time'] >= start_time and step_annotation['end_time'] <= end_time:
            # step_annotation['start_time'] -= start_time
            # step_annotation['end_time'] -= start_time
            sliced_recording_annotation_dict['steps'].append(step_annotation)
        elif step_annotation['end_time'] > end_time > step_annotation['start_time'] >= start_time:
            step_annotation['end_time'] = end_time
            # step_annotation['start_time'] -= start_time
            # step_annotation['end_time'] -= start_time
            sliced_recording_annotation_dict['steps'].append(step_annotation)
        elif step_annotation['start_time'] < start_time < step_annotation['end_time'] <= end_time:
            step_annotation['start_time'] = start_time
            # step_annotation['start_time'] -= start_time
            # step_annotation['end_time'] -= start_time
            sliced_recording_annotation_dict['steps'].append(step_annotation)
        else:
            continue

    return sliced_recording_annotation_dict


def slice_annotations(video_file_path, recording_id, output_directory, max_duration=18 * 60):
    # Load the video
    clip = VideoFileClip(video_file_path)

    # Get the video duration
    video_duration = clip.duration

    # If video duration is less than or equal to max_duration, no slicing is needed
    difference = round(video_duration) - max_duration
    if difference <= 60:
        print(f"[{recording_id}] Video duration is within the limit.")
        return [step_annotations[recording_id]]
    # Calculate the number of slices needed
    num_slices = int(video_duration // max_duration)
    remainder_duration = video_duration % max_duration

    print("------------------------------------------------------------------")
    print(f"[{recording_id}] Slicing video into {num_slices + 1} parts")

    sliced_recording_annotation_dict_list = []
    # Slice the video into max_duration parts

    for i in range(num_slices):
        start_time = i * max_duration
        end_time = (i + 1) * max_duration
        sliced_recording_id = f"{recording_id}_sliced_{i + 1}"
        sliced_recording_annotation_dict = fetch_sliced_recording_annotation(start_time, end_time, sliced_recording_id,
                                                                             recording_id)
        if len(sliced_recording_annotation_dict['steps']) > 0:
            sliced_recording_annotation_dict_list.append(sliced_recording_annotation_dict)

    # If there's any remainder video, save that too
    if remainder_duration > 0:
        start_time = num_slices * max_duration
        end_time = video_duration
        sliced_recording_id = f"{recording_id}_sliced_{num_slices + 1}"
        sliced_recording_annotation_dict = fetch_sliced_recording_annotation(start_time, end_time, sliced_recording_id,
                                                                             recording_id)
        if len(sliced_recording_annotation_dict['steps']) > 0:
            sliced_recording_annotation_dict_list.append(sliced_recording_annotation_dict)

    return sliced_recording_annotation_dict_list


def slice_longer_annotations(base_path, videos_type="normal_error_done"):
    sliced_annotations_path = osp.join('../data/ERROR/sliced_step_annotations.json')
    sliced_step_annotations = dict()
    videos_path = osp.join(base_path, videos_type, "videos")
    for data_type in ["train", "val", "test"]:
        videos_data_path = osp.join(videos_path, data_type)
        for category in os.listdir(videos_data_path):
            category_videos_directory_path = osp.join(videos_data_path, category)
            for video in os.listdir(category_videos_directory_path):
                video_path = osp.join(category_videos_directory_path, video)
                recording_id = video.replace(".mp4", "")
                sliced_recording_annotation_dict_list = slice_annotations(video_path, recording_id,
                                                                          category_videos_directory_path)
                for sliced_recording_annotation_dict in sliced_recording_annotation_dict_list:
                    sliced_recording_id = sliced_recording_annotation_dict['recording_id']
                    sliced_step_annotations[sliced_recording_id] = sliced_recording_annotation_dict
    with open(sliced_annotations_path, 'w') as f:
        json.dump(sliced_step_annotations, f)


if __name__ == '__main__':
    activity_idx_step_idx_path = osp.join('../data/ERROR/activity_idx_step_idx.json')
    step_annotations_json_path = osp.join('../data/ERROR/step_annotations.json')
    step_idx_description_path = osp.join('../data/ERROR/step_idx_description.json')

    activity_idx_step_idx_map = json.load(open(activity_idx_step_idx_path, 'r'))
    step_annotations = json.load(open(step_annotations_json_path, 'r'))
    step_idx_description = json.load(open(step_idx_description_path, 'r'))

    raw_videos_path = osp.join('/home/rxp190007/DATA/error_dataset/data_2d/resolution_360p')
    # main()
    # slice_longer_annotations(base_path='/home/rxp190007/DATA')
