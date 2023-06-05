import numpy as np


def load_npy_file(file_path):
	data = np.load(file_path)
	return data


# Provide the file path of your .npy file
npy_file_path = r'D:\DATA\OPEN\BreakfastII_15fps_qvga_sync\Breakfast\Breakfast\features\P03_cam01_P03_coffee.npy'

# Call the load_npy_file function
loaded_data = load_npy_file(npy_file_path)

# Print the loaded data
print(loaded_data)
