import os

from datacollection.user_app.backend.post_processing.SequenceViewer import SequenceViewer

if __name__ == "__main__":
    curr_dir = os.path.dirname(__file__)

    rec_id = "4_22"
    sequence_folder = f"../../../../data/hololens/{rec_id}/sync"
    viewer = SequenceViewer(rec_id=rec_id)
    viewer.load(sequence_folder)
    viewer.run()
