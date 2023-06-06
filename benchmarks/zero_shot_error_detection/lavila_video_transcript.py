import urllib

import decord
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

import torch
import torchvision.transforms as transforms
import torchvision.transforms._transforms_video as transforms_video

import sys

from datacollection.user_app.backend.app.models.narration import Narration
from lavila.eval_narrator import decode_one

sys.path.insert(0, './')

from lavila.lavila.data.video_transforms import Permute
from lavila.lavila.data.datasets import get_frame_ids, video_loader_by_frames
from lavila.lavila.models.models import VCLM_OPENAI_TIMESFORMER_BASE_GPT2, VCLM_OPENAI_TIMESFORMER_LARGE_336PX_GPT2_XL
from lavila.lavila.models.tokenizer import MyGPT2Tokenizer

import json
import os
import os.path as osp
import yaml


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)


def initialize_paths():
    this_dir = osp.dirname(__file__)

    lib_path = osp.join(this_dir, "../../datacollection")
    add_path(lib_path)


def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Error while parsing YAML file: {e}")


initialize_paths()

from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.models.activity import Activity
from moviepy.editor import VideoFileClip


def create_directory(output_directory):
    if not osp.exists(output_directory):
        os.makedirs(output_directory)


class LavilaVideoTranscript:

    def __init__(self, recording: Recording, video_directory, output_directory):
        self.video_directory = video_directory
        self.recording = recording

        self.num_segments = 4
        if os.path.exists(os.path.join(self.video_directory, f'{self.recording.id}_360p.mp4')):
            self.video_path = os.path.join(self.video_directory, f'{self.recording.id}_360p.mp4')
        else:
            self.video_path = os.path.join(self.video_directory, f'{self.recording.id}_360p.MP4')

        self._prepare_video_params()
        self.num_return_sequences = 10

        self.output_directory = output_directory
        os.makedirs(self.output_directory, exist_ok=True)

        self.output_file_path = os.path.join(self.output_directory, f'{self.recording.id}_narration.json')

        self.frames_per_second = 30
        self.clip_duration = 2

        self.total_clip_frames = self.frames_per_second * self.clip_duration

        self.db_service = FirebaseService()
        self.is_cuda = torch.cuda.is_available()
        print("Using cuda" if self.is_cuda else "Using cpu")

        self._load_models()

    def _prepare_video_params(self):
        self.num_seg = 4
        self.video_reader = decord.VideoReader(self.video_path)

        self.crop_size = 336
        self.val_transform = transforms.Compose([
            Permute([3, 0, 1, 2]),
            transforms.Resize(self.crop_size),
            transforms.CenterCrop(self.crop_size),
            transforms_video.NormalizeVideo(mean=[108.3272985, 116.7460125, 104.09373615000001],
                                            std=[68.5005327, 66.6321579, 70.32316305])
        ])

        self.total_video_frames = len(self.video_reader)
        self.total_iterations = self.total_video_frames // self.num_seg

    def _load_models(self):
        self.checkpoint_name = 'vclm_openai_timesformer_large_336px_gpt2_xl.pt_ego4d.jobid_246897.ep_0003.md5sum_443263.pth'
        self.checkpoint_path = os.path.join('modelzoo/', self.checkpoint_name)
        os.makedirs('modelzoo/', exist_ok=True)
        if not os.path.exists(self.checkpoint_path):
            print('downloading model to {}'.format(self.checkpoint_path))
            urllib.request.urlretrieve(
                'https://dl.fbaipublicfiles.com/lavila/checkpoints/narrator/{}'.format(self.checkpoint_name),
                self.checkpoint_path)

        print("instantiating model")
        # instantiate the model, and load the pre-trained weights
        self.lavila_model = VCLM_OPENAI_TIMESFORMER_LARGE_336PX_GPT2_XL(
            text_use_cls_token=False,
            project_embed_dim=256,
            gated_xattn=True,
            timesformer_gated_xattn=False,
            freeze_lm_vclm=False,  # we use model.eval() anyway
            freeze_visual_vclm=False,  # we use model.eval() anyway
            num_frames=4,
            drop_path_rate=0.
        )
        print('loading model from {}'.format(self.checkpoint_path))
        self.checkpoint = torch.load(self.checkpoint_path, map_location='cpu')

        state_dict = OrderedDict()
        for k, v in self.checkpoint['state_dict'].items():
            state_dict[k.replace('module.', '')] = v

        self.lavila_model.load_state_dict(state_dict, strict=True)
        print("model loaded and sending to cuda")
        if self.is_cuda:
            self.lavila_model.cuda()
        self.lavila_model.eval()
        print("model in evaluation mode")

    def generate_narration(self):
        narration_dict_list = []
        for iteration in range(self.total_iterations):
            print('iteration {}/{}'.format(iteration, self.total_iterations))

            start_frame_id = iteration * self.total_clip_frames
            end_frame_id = min((iteration + 1) * self.total_clip_frames, self.total_video_frames)

            frame_ids = get_frame_ids(start_frame_id, end_frame_id, num_segments=self.num_segments, jitter=False)
            frames = video_loader_by_frames('./', self.video_path, frame_ids)
            frames = self.val_transform(frames)
            frames = frames.unsqueeze(0)  # fake a batch dimension

            tokenizer = MyGPT2Tokenizer('gpt2-xl', add_bos=True)
            with torch.no_grad():
                if self.is_cuda:
                    frames = frames.cuda(non_blocking=True)
                image_features = self.lavila_model.encode_image(frames)
                generated_text_ids, ppls = self.lavila_model.generate(
                    image_features,
                    tokenizer,
                    target=None,  # free-form generation
                    max_text_length=77,
                    top_k=None,
                    top_p=0.95,  # nucleus sampling
                    num_return_sequences=self.num_return_sequences,  # number of candidates: 10
                    temperature=0.7,
                    early_stopping=True,
                )

            print('-----------------')
            for i in range(self.num_return_sequences):
                generated_text_str = decode_one(generated_text_ids[i], tokenizer)
                narration_dict = {
                    "start": start_frame_id / self.frames_per_second,
                    "end": end_frame_id / self.frames_per_second,
                    "narration": generated_text_str
                }
                narration_dict_list.append(narration_dict)
                print('{}: {}'.format(i, generated_text_str))

        with open(self.output_file_path, 'w') as f:
            narration_json_data = json.dumps(narration_dict_list, indent=4)
            json.dump(narration_json_data, f, indent=4)

        narration = Narration(self.recording.id, narration_dict_list)
        self.db_service.update_narration(narration)


if __name__ == '__main__':
    recording_id = "8_3"
    firebase_service = FirebaseService()
    recording = Recording.from_dict(firebase_service.fetch_recording(recording_id))
    video_directory = "/data/ANNOTATION/"
    output_directory = "/data/NARRATION/"
    lavila_video_transcript = LavilaVideoTranscript(recording, video_directory, output_directory)
    lavila_video_transcript.generate_narration()
