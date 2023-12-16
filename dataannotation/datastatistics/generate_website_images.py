import os

from PIL import Image


def main():
	# 1. Load image files from a directory
	# 2. Change the name of each image to a number ranging from 0 to 24
	# 3. Save the images in a new directory
	counter = 0
	for filename in os.listdir(image_input_directory):
		if filename.endswith(".png"):
			image = Image.open(image_input_directory + filename)
			output_filename = f"{counter:06}.PNG"  # Formats the number with six digits, padding with zeros
			image.save(image_output_directory + output_filename)
			counter += 1
		else:
			print("Not a png file")


if __name__ == '__main__':
	version = 6
	image_input_directory = f"task_graphs/images/v{version}/"
	image_output_directory = f"task_graphs/website_images/v{version}/"
	os.makedirs(image_output_directory, exist_ok=True)
	main()
