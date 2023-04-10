import logging
import os
import pickle

import cv2
import numpy as np
import yaml

from open3d import core as o3c
from datacollection.user_app.backend.hololens import hl2ss, hl2ss_3dcv, hl2ss_utilities


class SequenceLoader:
    def __init__(self, device="cuda:0", debug=False, rec_id=None):
        self.device = device
        self.rec_id = rec_id
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
            curr_dir, "../../../../../data/calibration", self._device_id
        )
        self._pv2rig, self._pv_intrinsic = self.load_pv_calibration_info(
            self._pv_width, self._pv_height
        )
        self._principal_point, self._focal_length, self._intrinsics = self.load_calibration_data(
            self._pv_width, self._pv_height
        )
        (
            self._depth2rig,
            self._depth_xy1,
            self._depth_scale,
        ) = self.load_depth_calibration_info(depth_mode=self._depth_mode)

        self.spatial_data = self.load_spatial_data()
        self.pv_pose_data = self.load_pv_pose_data()

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
        num_frames = data["num_of_frames"]
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

    def load_calibration_data(self, width, height):
        pv_calib_folder = os.path.join(self.calib_folder, "personal_video")
        principal_point = self._load_data_from_bin_file(
            os.path.join(pv_calib_folder, f"1000_{width}_{height}/principal_point.bin")
        )
        focal_length = self._load_data_from_bin_file(
            os.path.join(pv_calib_folder, f"1000_{width}_{height}/focal_length.bin")
        )
        # @formatter:off
        intrinsics = np.array([
            [-focal_length[0],      0,                  0, 0],
            [0,                     focal_length[1],    0, 0],
            [principal_point[0],    principal_point[1], 1, 0],
            [0,                     0,                  0, 1]], dtype=np.float32)
        # @formatter:on
        radial_distortion = self._load_data_from_bin_file(
            os.path.join(pv_calib_folder, f"1000_{width}_{height}/radial_distortion.bin")
        )
        tangential_distortion = self._load_data_from_bin_file(
            os.path.join(pv_calib_folder, f"1000_{width}_{height}/tangential_distortion.bin")
        )
        projection = self._load_data_from_bin_file(
            os.path.join(pv_calib_folder, f"1000_{width}_{height}/projection.bin")
        )
        return principal_point, focal_length, intrinsics

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

    def load_spatial_data(self):
        spatial_data_folder = os.path.join(self._data_folder, "spatial")
        spatial_data = self._load_data_from_pickle_file(os.path.join(spatial_data_folder, f"{self.rec_id}_spatial.pkl"))
        spatial_data = list(spatial_data.values())
        print(len(spatial_data))
        return spatial_data

    def load_pv_pose_data(self):
        pv_pose_data = self._load_data_from_pickle_file(
            os.path.join(self._data_folder, "pv", f"{self.rec_id}_pv_pose.pkl")
        )
        pv_pose_data = list(pv_pose_data.values())
        print(len(pv_pose_data))
        return pv_pose_data

    def update_pcd(self):
        depth_file = os.path.join(
            self._data_folder, "depth_{}/depth/depth-{:06d}.png".format(self.depth_mode, self._frame_id)
        )
        depth = self._load_depth_image(depth_file)
        points = self._get_points_in_cam_space(depth, scale=250.0)
        return points, depth

    @classmethod
    def project_points(cls, image, P, points, radius, color, thickness):
        for x, y in hl2ss_3dcv.project_to_image(hl2ss_3dcv.to_homogeneous(points), P):
            cv2.circle(image, (int(x), (int(y))), radius, color, thickness)

    def project_spatial(self, image, pv_pose, data_si: hl2ss.unpack_si):
        # Marker properties
        radius = 2
        color = (0, 255, 255)
        thickness = 3

        if hl2ss.is_valid_pose(pv_pose) and (data_si is not None):
            projection = hl2ss_3dcv.projection(self._intrinsics, hl2ss_3dcv.world_to_reference(pv_pose))
            si = data_si
            if si.is_valid_hand_left():
                self.project_points(image, projection, hl2ss_utilities.si_unpack_hand(si.get_hand_left()).positions,
                                    radius, color, thickness)
            if si.is_valid_hand_right():
                self.project_points(image, projection, hl2ss_utilities.si_unpack_hand(si.get_hand_right()).positions,
                                    radius, color, thickness)

    def step(self):
        self._frame_id = (self._frame_id + 1) % self._num_frames
        self._points, self._depth_img = self.update_pcd()
        self._color_img = self._load_rgb_image(
            os.path.join(
                self._data_folder, "pv/frames/color-{:06d}.jpg".format(self._frame_id)
            )
        )
        self._color_pose = self.pv_pose_data[self._frame_id][0]
        self._spatial = self.spatial_data[self._frame_id][0]
        self.project_spatial(self._color_img, self._color_pose, self._spatial)

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
