from PIL import Image, ImageDraw, ImageFont
import os

def resize_image(input_path, output_path, target_height=760, heading_height=50, font_size=20):
    # Load the image
    with Image.open(input_path) as img:
        # Calculate the new width to maintain resolution, not aspect ratio
        new_width = int(img.width * (target_height / img.height))

        # Resize the image
        resized_img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)

        # Create a new image with white background for the heading
        new_img = Image.new('RGB', (new_width, target_height + heading_height), 'white')
        new_img.paste(resized_img, (0, heading_height))

        # Prepare to add a heading
        draw = ImageDraw.Draw(new_img)

        # Specify a TrueType font
        font_path = "arial.ttf"  # Replace with the path to a TTF font file on your system
        font = ImageFont.truetype(font_path, font_size)

        text = os.path.splitext(os.path.basename(input_path))[0]

        # Estimate text width and height
        text_width = len(text) * font_size * 0.5  # Rough estimation
        text_height = font_size  # Based on font size

        # Calculate text position
        text_x = (new_width - text_width) // 2
        text_y = (heading_height - text_height) // 2

        # Draw a box around the heading
        # box_margin = 5
        # box = [(text_x - box_margin, text_y - box_margin),
        #        (text_x + text_width + box_margin, text_y + text_height + box_margin)]
        # draw.rectangle(box, outline="black", fill="white")

        # Add the text
        draw.text((text_x, text_y), text, fill="black", font=font)

        # Save the new image
        new_img.save(output_path)

# Example usage



def process_all_images(folder_path, output_folder, target_height=760, heading_height=50, font_size=20):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Construct the full file path
        input_path = os.path.join(folder_path, filename)

        # Check if it's a file and not a directory
        if os.path.isfile(input_path):
            # Construct the output file path
            output_path = os.path.join(output_folder, filename)

            # Resize the image
            resize_image(input_path, output_path, target_height, heading_height, font_size)
            print(f"Processed {filename}")

# Specify the folder path and output folder
folder_path = 'unedited_image'  # Update this to the path of your images folder
output_folder = 'edited_image'  # Update this to your desired output folder path

# Process all images in the folder
process_all_images(folder_path, output_folder)
