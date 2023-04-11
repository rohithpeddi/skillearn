import logging
import os
import sys
from time import sleep
import os.path as osp

import numpy as np
import open3d as o3d
import open3d.core as o3c
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering

from .sequence_loader import SequenceLoader


# def add_path(path):
#     if path not in sys.path:
#         sys.path.insert(0, path)
#
#
# def initialize_paths():
#     this_dir = osp.dirname(__file__)
#
#     lib_path = osp.join(this_dir, "../../backend")
#     add_path(lib_path)
#
#
# initialize_paths()


class SequenceViewer:
    def __init__(self, rec_id=None, debug=False) -> None:
        self._rec_id = rec_id
        self._logger = self._init_logger(debug)
        self._loader = SequenceLoader(debug=debug, rec_id=rec_id)

    def load(self, sequence_folder):
        self._loader.load(sequence_folder)
        self._depth_width = self._loader.depth_width
        self._depth_height = self._loader.depth_height
        self._color_width = self._loader.pv_width
        self._color_height = self._loader.pv_height
        self._num_frames = self._loader.num_frames

    def run(self):
        self._width = 1200
        self._height = 1200
        self._count = 0
        # control flags
        self._flag_pause = False
        self._flag_change_pt_size = False
        # rendering config
        self._bg_color = (0.1, 0.1, 0.1, 1.0)
        self._show_axes = False
        self._show_skybox = False
        self._enable_lighting = False
        self._update_flags = rendering.Scene.UPDATE_POINTS_FLAG
        # self._update_flags = (rendering.Scene.UPDATE_POINTS_FLAG |
        #                     rendering.Scene.UPDATE_COLORS_FLAG |
        #                     (rendering.Scene.UPDATE_NORMALS_FLAG
        #                      if self.flag_normals else 0))
        # geometry
        self._pcd = o3d.t.geometry.PointCloud()
        self._pcd.point.positions = o3c.Tensor(
            np.zeros(
                (self._depth_width * self._depth_height, 3),
                dtype=np.float32,
            )
        )
        self._depth_img = None
        self._color_img = None

        self._app = gui.Application.instance
        self._app.initialize()
        self._window = self._app.create_window(
            "O3D Sequence Viewer", self._width, self._height
        )

        # add callbacks
        self._window.set_on_layout(self._on_layout)
        self._window.set_on_close(self._on_close)
        self._window.set_on_key(self._on_key)
        self._window.set_on_tick_event(self._on_tick)

        # initialize 3D widget
        self._widget3d = gui.SceneWidget()
        self._widget3d.scene = rendering.Open3DScene(self._window.renderer)
        self._widget3d.scene.set_background(self._bg_color)
        self._widget3d.scene.show_axes(self._show_axes)
        self._widget3d.scene.show_skybox(self._show_skybox)
        self._widget3d.scene.scene.enable_sun_light(self._enable_lighting)

        # point cloud material
        self._mat_pcd = rendering.MaterialRecord()
        self._mat_pcd.shader = "defaultUnlit"
        self._mat_pcd.point_size = int(2 * self._window.scaling)
        self._mat_pcd.base_color = (0.9, 0.9, 0.9, 1.0)

        # Options panel
        em = self._window.theme.font_size
        margin = 0.3 * em
        self._panel = gui.Vert(margin, gui.Margins(margin, margin, margin, margin))
        self._widgetColor = gui.ImageWidget(
            o3d.t.geometry.Image(
                o3c.Tensor.zeros(
                    (self._depth_height, self._depth_width, 3), dtype=o3c.uint8
                )
            )
        )
        self._panel.add_child(gui.Label("PV Image"))
        self._panel.add_child(self._widgetColor)
        self._widgetDepth = gui.ImageWidget(
            o3d.t.geometry.Image(
                o3c.Tensor.zeros(
                    (self._depth_height, self._depth_width, 3), dtype=o3c.uint8
                )
            )
        )
        self._panel.add_child(gui.Label("Depth Image (normalized)"))
        self._panel.add_child(self._widgetDepth)

        # add widgets
        self._window.add_child(self._widget3d)
        self._window.add_child(self._panel)

        # add point cloud
        self._widget3d.scene.add_geometry("pcd", self._pcd, self._mat_pcd)

        # setup camera
        self._update_camera()
        self._start_time = self._app.now
        self._app.run()

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

    def _on_layout(self, layout_context):
        contentRect = self._window.content_rect
        pref = self._panel.calc_preferred_size(layout_context, gui.Widget.Constraints())
        # panel_width = pref.width
        self._widget3d.frame = gui.Rect(
            0,
            0,
            pref.height,
            pref.height,
        )
        self._panel.frame = gui.Rect(
            self._widget3d.frame.get_right(),
            0,
            pref.width,
            pref.height,
        )
        self._window.size = gui.Size(pref.width * 2, pref.height)

    def _on_close(self):
        return True

    def _on_image(self, image):
        pass

    def _on_key(self, event):
        if event.key == gui.KeyName.SPACE:  # pause
            if event.type == gui.KeyEvent.DOWN:
                self._flag_pause = not self._flag_pause
                return True

        if event.key == gui.KeyName.Q:  # quit
            if event.type == gui.KeyEvent.DOWN:
                self._window.close()
                return True

        if event.key == gui.KeyName.S:  # save capture
            if event.type == gui.KeyEvent.DOWN:
                self._widget3D.scene.scene.render_to_image(self._on_image)
                return True

        if event.key == gui.KeyName.Z:  # change point size
            if event.type == gui.KeyEvent.DOWN:
                self._flag_change_pt_size = not self._flag_change_pt_size
                if self._flag_change_pt_size:
                    self._mat_pcd.point_size = int(1 * self._window.scaling)
                else:
                    self._mat_pcd.point_size = int(2 * self._window.scaling)
                self._widget3d.scene.update_material(self._mat_pcd)
                return True

        if event.key in [gui.KeyName.R, gui.KeyName.ZERO]:  # reset camera
            if event.type == gui.KeyEvent.DOWN:
                self._update_camera()
                return True

        if event.key == gui.KeyName.H:  # help
            if event.type == gui.KeyEvent.DOWN:
                self._print_help_info()
                return True

    def _print_help_info(self):
        print("=" * 60)
        print("Keyboard commands:")
        print("-" * 60)
        print("SPACE: pause")
        print("Q: quit")
        print("S: save capture")
        print("Z: change point size")
        print("H: print help info")
        print("=" * 60)

    def _on_tick(self):
        if self._flag_pause:
            return False
        sleep(0.02)
        self._step()
        self._app.run_in_thread(self.update)
        return True

    def _update_camera(self):
        fov = 60.0
        aspect_ratio = float(self._window.size.width) / float(self._window.size.height)
        near = 0.1
        far = 100.0
        fov_type = rendering.Camera.FovType.Vertical
        self._widget3d.scene.camera.set_projection(
            fov, aspect_ratio, near, far, fov_type
        )
        self._widget3d.scene.camera.look_at(
            (0, 0, 1), (0, 0, -0.5), (0, -1, 0)
        )  # center, eye, up

    def _step(self):
        self._loader.step()
        self._pcd.point.positions = o3c.Tensor(self._loader.points)
        self._depth_img = o3d.t.geometry.Image(
            o3c.Tensor((self._loader.depth_img * 4.0).astype(np.uint16))
        ).colorize_depth(scale=250.0, min_value=0.0, max_value=2.0)
        self._color_img = o3d.t.geometry.Image(o3c.Tensor(self._loader.color_img))
        self._count += 1

    def update(self):
        self._app.post_to_main_thread(self._window, self._update_3d_widget)
        self._app.post_to_main_thread(self._window, self._update_image_widget)
        self._app.post_to_main_thread(self._window, self._update_window_title)

    def _update_3d_widget(self):
        self._widget3d.scene.scene.update_geometry("pcd", self._pcd, self._update_flags)

    def _update_image_widget(self):
        self._widgetColor.update_image(self._color_img)
        self._widgetDepth.update_image(self._depth_img)

    def _update_window_title(self):
        fps = self._count / (self._app.now - self._start_time)
        self._window.title = f"SequenceViewer (FPS: {fps: 0.2f})"
        if self._count == self._num_frames:
            self._start_time = self._app.now
            self._count = 0


if __name__ == "__main__":
    curr_dir = os.path.dirname(__file__)

    sequence_folder = os.path.join(
        curr_dir, "../../../../../data/hololens/13_43/sync"
    )
    viewer = SequenceViewer()
    viewer.load(sequence_folder)
    viewer.run()
