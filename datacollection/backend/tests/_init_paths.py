import sys
import os


def add_path(path):
    if path not in sys.path:
        sys.path.append(path)


curr_dir = os.path.dirname(__file__)

root_path = os.path.dirname(curr_dir)
add_path(root_path)
