import os

from datacollection.user_app.backend.post_processing.SequenceViewer import SequenceViewer

if __name__ == "__main__":
    curr_dir = os.path.dirname(__file__)

    sequence_folder = "../../../../data/hololens/13_43/sync"
    viewer = SequenceViewer()
    viewer.load(sequence_folder)
    viewer.run()
