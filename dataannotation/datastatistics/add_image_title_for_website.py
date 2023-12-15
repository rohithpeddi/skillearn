import json
import os

from PIL import Image, ImageDraw, ImageFont


def generate_title(image_name, title_text, font_size=50):
	task_graph_image_input_path = f"{task_graph_image_input_directory}/{image_name}.png"
	task_graph_image_output_path = f"{task_graph_image_output_directory}/{image_name}.png"
	image = Image.open(task_graph_image_input_path)
	
	# Choose a font
	font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
	font = ImageFont.truetype(font_path, font_size)
	
	# Define the size of the image
	image_width, image_height = image.size
	# Create a new image with additional space at the top for the title
	# Define the size of the additional space
	additional_space = 100  # 100 pixels for the title
	
	# Create a new image with the additional space
	new_image_height = image_height + additional_space
	new_image = Image.new("RGB", (image_width, new_image_height), "white")
	new_image.paste(image, (0, additional_space))
	
	# Create a draw object
	draw = ImageDraw.Draw(image)
	
	# Calculate width and height of the text to be added
	text_width, text_height = draw.textsize(title_text, font=font)
	
	# Calculate X, Y position of the title text
	x = (image_width - text_width) / 2
	# Calculate X, Y position of the title text on the new image
	# Y position should be in the additional space, so we use half of the additional space minus half of the text height
	y = (additional_space - text_height) // 2
	
	# Draw the title text on the image
	draw.text((x, y), title_text, font=font, fill="black")
	
	# Save the edited image
	new_image.save(task_graph_image_output_path)


def fetch_title_text():
	activity_division_statistics = json.load(
		open(f"{processed_files_directory}/v{version}/recipe_error_normal_division_statistics.json", 'r')
	)
	activity_names = []
	for activity_name, activity_statistics in activity_division_statistics.items():
		if type(activity_statistics) is not dict:
			continue
		activity_names.append(activity_name)
	
	activity_names = sorted(activity_names)
	
	image_name_title_text_map = {}
	for activity_name in activity_names:
		title_text = f"{activity_name}"
		image_name = activity_name.replace(" ", "")
		image_name_title_text_map[image_name] = title_text
	
	return image_name_title_text_map


def main():
	image_name_title_text_map = fetch_title_text()
	for image_name, title_text in image_name_title_text_map.items():
		generate_title(image_name, title_text)


if __name__ == "__main__":
	processed_files_directory = "./processed_files"
	version = 5
	task_graph_image_input_directory = f"task_graph_images/{version}/screenshots"
	task_graph_image_output_directory = f"task_graph_images/{version}/modified"
	os.makedirs(task_graph_image_output_directory, exist_ok=True)
	os.makedirs(task_graph_image_input_directory, exist_ok=True)
	main()
