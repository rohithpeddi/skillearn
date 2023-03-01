import os
import numpy as np
import cv2
import pickle
import yaml
import logging
import open3d.core as o3c


class SequenceLoader:
    def __init__(self, device="cuda:0", debug=False):
        self.device = device
        self.logger = self._init_logger(debug)

    def load(self, sequence_folder):
        self.logger.debug("Loading sequence from %s", os.path.basename(sequence_folder))
        self._data_folder = sequence_folder
        self._device_o3d = o3c.Device(self.device)
        meta_file = os.path.join(self._data_folder, "meta.yaml")
        (
            self._device_id,
            self._depth_mode,
            self._pv_width,
            self._pv_height,
            self._depth_width,
            self._depth_height,
            self._num_frames,
        ) = self.load_meta_data(meta_file)
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        self.calib_folder = os.path.join(
            curr_dir, "../../data/calibration", self._device_id
        )
        self._pv2rig, self._pv_intrinsic = self.load_pv_calibration_info(
            self._pv_width, self._pv_height
        )
        (
            self._depth2rig,
            self._depth_xy1,
            self._depth_scale,
        ) = self.load_depth_calibration_info(depth_mode=self._depth_mode)

        self._frame_id = -1
        self._points = None
        self._colors = None
        self._depth_img = None
        self._color_img = None

    def _init_logger(self, debug):
        logger = logging.getLogger("SequenceViewer")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if debug else logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def _load_data_from_pickle_file(self, file_path):
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        return data

    def _load_data_from_bin_file(self, file_path):
        data = np.fromfile(file_path, dtype=np.float32)
        return data

    def _load_data_from_yaml_file(self, file_path):
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        return data

    def _load_rgb_image(self, file_path):
        img = cv2.imread(file_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def _load_depth_image(self, file_path):
        self.logger.debug("Loading depth image from %s", file_path)
        img = cv2.imread(file_path, cv2.IMREAD_ANYDEPTH)
        return img

    def load_meta_data(self, file_path):
        self.logger.debug("Loading meta data from %s", file_path)
        data = self._load_data_from_yaml_file(file_path)
        device_id = data["device_id"]
        depth_mode = data["depth_mode"]
        pv_width = data["pv_width"]
        pv_height = data["pv_height"]
        depth_width = data["depth_width"]
        depth_height = data["depth_height"]
        num_frames = data["num_frames"]
        self.logger.debug("Meta data loaded")
        return (
            device_id,
            depth_mode,
            pv_width,
            pv_height,
            depth_width,
            depth_height,
            num_frames,
        )

    def load_extrinsic_matrix(self, file_path):
        data = self._load_data_from_bin_file(file_path)
        T = data.reshape(4, 4).transpose()
        return T

    def load_intrinsic_matrix(self, file_path):
        data = self._load_data_from_bin_file(file_path)
        K = data.reshape(4, 4).transpose()
        return K[:3, :3]

    def load_depth_calibration_info(self, depth_mode="ahat"):
        assert depth_mode in ["ahat", "longthrow"]
        depth_calib_folder = os.path.join(self.calib_folder, f"rm_depth_{depth_mode}")
        extrinsic = self.load_extrinsic_matrix(
            os.path.join(depth_calib_folder, "extrinsics.bin")
        )
        scale = self._load_data_from_bin_file(
            os.path.join(depth_calib_folder, "scale.bin")
        ).item()
        uv2xy = self._load_data_from_bin_file(
            os.path.join(depth_calib_folder, "uv2xy.bin")
        ).reshape((-1, 2))
        n = np.linalg.norm(uv2xy, axis=1)
        xy1 = np.concatenate(
            (uv2xy, np.ones((uv2xy.shape[0], 1), dtype=np.float32)), axis=-1
        )
        return extrinsic, xy1, scale

    def load_pv_calibration_info(self, width, height):
        pv_calib_folder = os.path.join(self.calib_folder, "personal_video")
        extrinsic = self.load_extrinsic_matrix(
            os.path.join(pv_calib_folder, "extrinsics.bin")
        )
        intrinsic = self.load_intrinsic_matrix(
            os.path.join(pv_calib_folder, f"1000_{width}_{height}/intrinsics.bin")
        )
        return extrinsic, intrinsic

    def _get_points_in_cam_space(
        self, depth, scale=1000.0, depth_min=0.1, depth_max=3.0
    ):
        depth = depth.astype(np.float32)
        depth /= scale
        depth[depth < depth_min] = 0.0
        depth[depth > depth_max] = 0.0
        depth = np.tile(depth.flatten().reshape((-1, 1)), (1, 3))
        points = depth * self._depth_xy1
        points = points[points[:, 2] > 0.0]
        return points

    def cam2world(self, points, cam2world):
        homog_points = np.hstack((points, np.ones((points.shape[0], 1))))
        world_points = np.matmul(cam2world, homog_points.T)
        return world_points.T[:, :3], cam2world

    def _get_points_in_world_space(
        self, points_cam, rig2world_transform, rig2cam_transform
    ):
        cam2world_transform = np.matmul(
            rig2world_transform, np.linalg.inv(rig2cam_transform)
        )
        homog_points = np.hstack((points_cam, np.ones((points_cam.shape[0], 1))))
        world_points = np.matmul(cam2world_transform, homog_points.T)
        world_points = world_points.T[:, :3]
        return world_points

    def update_pcd(self):
        depth_file = os.path.join(
            self._data_folder, "frames/depth/depth-{:06d}.png".format(self._frame_id)
        )
        depth = self._load_depth_image(depth_file)
        points = self._get_points_in_cam_space(depth, scale=250.0)
        return points, depth

    def step(self):
        self._frame_id = (self._frame_id + 1) % self._num_frames
        self._points, self._depth_img = self.update_pcd()
        self._color_img = self._load_rgb_image(
            os.path.join(
                self._data_folder, "frames/pv/color-{:06d}.jpg".format(self._frame_id)
            )
        )

    @property
    def device_id(self):
        return self._device_id

    @property
    def depth_mode(self):
        return self._depth_mode

    @property
    def pv_width(self):
        return self._pv_width

    @property
    def pv_height(self):
        return self._pv_height

    @property
    def depth_width(self):
        return self._depth_width

    @property
    def depth_height(self):
        return self._depth_height

    @property
    def num_frames(self):
        return self._num_frames

    @property
    def pv2rig(self):
        return self._pv2rig

    @property
    def pv_intrinsic(self):
        return self._pv_intrinsic

    @property
    def depth2rig(self):
        return self._depth2rig

    @property
    def depth_xy1(self):
        return self._depth_xy1

    @property
    def depth_scale(self):
        return self._depth_scale

    @property
    def frame_id(self):
        return self._frame_id

    @property
    def points(self):
        return self._points

    @property
    def depth_img(self):
        return self._depth_img

    @property
    def color_img(self):
        return self._color_img
