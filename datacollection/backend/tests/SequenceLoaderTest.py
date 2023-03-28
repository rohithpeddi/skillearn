import os
import numpy as np
import _init_paths
from datacollection.backend.post_processing.SequenceLoader import SequenceLoader


if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    sequence_folder = os.path.join(
        curr_dir, "../../../../data/mugpizza/SAMPLE/MugPizza_PL2_P2_R1_0/sync/"
    )
    loader = SequenceLoader(debug=True)
    loader.load(sequence_folder)

    print("device_id:\n", loader.device_id)
    print("depth_mode:\n", loader.depth_mode)
    print("pv_width:\n", loader.pv_width)
    print("pv_height:\n", loader.pv_height)
    print("depth_width:\n", loader.depth_width)
    print("depth_height:\n", loader.depth_height)
    print("num_frames:\n", loader.num_frames)
    # print("pv_extrinsic:\n", loader.pv_extrinsic)
    print("pv_intrinsic:\n", loader.pv_intrinsic)
    # print("depth_extrinsic:\n", loader.depth_extrinsic)
    print("depth_xy1:\n", loader.depth_xy1)
    print("depth_scale:\n", loader.depth_scale)

    loader.step()
    print("frame_id:\n", loader.frame_id)
    points = loader.points
    print("pcd:\n", np.max(points, axis=0), np.min(points, axis=0))
    depth_img = loader.depth_img
    print("depth_img:\n", np.max(depth_img), np.min(depth_img))
