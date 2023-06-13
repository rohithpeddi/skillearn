import os
import numpy as np


def check_npy_files(file_path):
	try:
		npy_file = np.load(file_path)
	except Exception as e:
		print(e)
		print("The file {} is corrupted.".format(file_path))
		return False
	return True


# Provide the path to the directory containing the npy files
directory_path = r"D:\DATA\OPEN\BreakfastII_15fps_qvga_sync\breakfast_i3d\breakfast_i3d\features\P03_cam01_P03_cereals.npy"
check_npy_files(directory_path)
