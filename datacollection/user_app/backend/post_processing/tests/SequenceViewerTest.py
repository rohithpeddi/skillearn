import os
import _init_paths
from datacollection.backend.post_processing.SequenceViewer import SequenceViewer

if __name__ == "__main__":
    curr_dir = os.path.dirname(__file__)

    sequence_folder = os.path.join(
        curr_dir, "../../../../data/mugpizza/SAMPLE/MugPizza_PL2_P2_R1_0/sync/"
    )
    viewer = SequenceViewer()
    viewer.load(sequence_folder)
    viewer.run()
