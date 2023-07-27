import os
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog, messagebox

# Step 1: Use exiftool to extract text from the 'Prompt' category
def extract_prompt_text(image_path):
    cmd = ['exiftool', '-s', '-Prompt', '-b', image_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    prompt_json = result.stdout.strip()
    prompt_data = json.loads(prompt_json)

    # Access the 'text' field from the nested dictionary
    prompt_text = prompt_data.get('6', {}).get('inputs', {}).get('text', '')
    return prompt_text

# Function to wrap text to fit within a specific width
def wrap_text(text, font, max_width):
    lines = []
    current_line = ''
    words = text.split()
    for word in words:
        test_line = current_line + word + ' '
        if font.getsize(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + ' '
    if current_line:
        lines.append(current_line.strip())
    return lines

# Function to create the video slideshow and overlay metadata
def create_slideshow(images_folder, output_folder, output_file_name, font_size, max_text_width, image_duration):
    image_files = [f for f in os.listdir(images_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
    video_files = []

    for image_file in image_files:
        image_path = os.path.join(images_folder, image_file)
        prompt = extract_prompt_text(image_path)
        print(f"Image: {image_file}, Prompt: {prompt}")

        # Use PIL to open the image and set the Prompt tag in the image metadata
        img = Image.open(image_path)

        # Generate a separate image for the prompt text
        line_padding = 2  # Padding between lines of text
        max_prompt_height = 210  # Maximum height for the prompt image
        img_height = max_prompt_height + line_padding  # Initial height with padding for the first line
        prompt_image = Image.new('RGBA', (600, img_height), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(prompt_image)
        font = ImageFont.truetype('arial.ttf', size=font_size)

        # Wrap the text to fit within the available width
        wrapped_lines = wrap_text(prompt, font, max_text_width)
        line_height = draw.textsize("A", font=font)[1]

        # Calculate the total height required for the text
        total_text_height = len(wrapped_lines) * line_height + (len(wrapped_lines) - 1) * line_padding

        # Adjust the prompt image height if it exceeds the maximum allowed height
        if total_text_height > max_prompt_height:
            img_height = total_text_height + line_padding
            prompt_image = Image.new('RGBA', (600, img_height), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(prompt_image)

        # Calculate the y-coordinate to center the text vertically
        text_y = (prompt_image.height - total_text_height) / 2

        # Draw the wrapped text on the prompt image
        for line in wrapped_lines:
            text_width, text_height = draw.textsize(line, font=font)
            text_x = (max_text_width - text_width) / 2
            draw.text((text_x, text_y), line, font=font, fill='white')
            text_y += line_height + line_padding

        # Overlay the prompt image on the original image
        img.paste(prompt_image, (int((img.width - 600) / 2), img.height - img_height), prompt_image)

        # Save the image with the prompt overlay
        image_with_prompt_path = os.path.join(output_folder, f"prompt_{image_file}")
        img.save(image_with_prompt_path)

        # Use ffmpeg to create the video from the image with prompt overlay
        output_file = os.path.join(output_folder, f"output_{image_file}.mp4")
        cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', image_with_prompt_path,
            '-vf', f'drawtext=text=\'\':fontsize={font_size}:fontcolor=white:x=10:y=h-th-200',
            '-t', str(image_duration), '-c:a', 'copy', output_file
        ]
        subprocess.run(cmd)

        video_files.append(output_file)

        # Clean up the image with the Prompt overlay
        os.remove(image_with_prompt_path)

    # Concatenate all generated videos into one final video
    final_output_file = os.path.join(output_folder, f"{output_file_name}.mp4")
    concat_list_file = 'concat.txt'
    with open(concat_list_file, 'w') as f:
        for video_file in video_files:
            f.write(f"file '{video_file}'\n")

    concat_cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list_file,
        '-c', 'copy', final_output_file
    ]
    subprocess.run(concat_cmd)

    # Clean up intermediate video files and the list file
    for video_file in video_files:
        os.remove(video_file)
    os.remove(concat_list_file)

def browse_input_folder():
    input_folder = filedialog.askdirectory()
    input_folder_var.set(input_folder)

def browse_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_var.set(output_folder)

def generate_slideshow():
    images_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    output_file_name = output_file_var.get()
    font_size = int(font_size_var.get())
    max_text_width = int(max_width_var.get())
    image_duration = int(image_duration_var.get())

    if not images_folder or not os.path.isdir(images_folder):
        messagebox.showerror("Error", "Invalid input images folder.")
        return

    if not output_folder or not os.path.isdir(output_folder):
        messagebox.showerror("Error", "Invalid output folder.")
        return

    if not output_file_name:
        messagebox.showerror("Error", "Please enter a valid output file name.")
        return

    if not 20 <= font_size <= 50:
        messagebox.showerror("Error", "Font size should be between 20 and 50.")
        return

    if not max_text_width > 0:
        messagebox.showerror("Error", "Max text width should be greater than 0.")
        return

    if not 1 <= image_duration <= 10:
        messagebox.showerror("Error", "Image duration should be between 1 and 10 seconds.")
        return

    create_slideshow(images_folder, output_folder, output_file_name, font_size, max_text_width, image_duration)
    messagebox.showinfo("Success", "Slideshow generated successfully.")

if __name__ == "__main__":
    # Create the GUI window
    root = tk.Tk()
    root.title("SDXL Prompt Slideshow Generator")

    # Variables to store user inputs
    input_folder_var = tk.StringVar()
    output_folder_var = tk.StringVar()
    output_file_var = tk.StringVar()
    font_size_var = tk.StringVar(value="30")  # Default font size
    max_width_var = tk.StringVar(value="600")  # Default max text width
    image_duration_var = tk.StringVar(value="5")  # Default image duration

    # Labels and entry fields for user inputs
    tk.Label(root, text="Input SDXL Images Folder:").grid(row=0, column=0)
    tk.Entry(root, textvariable=input_folder_var, width=40).grid(row=0, column=1)
    tk.Button(root, text="Browse", command=browse_input_folder).grid(row=0, column=2)

    tk.Label(root, text="Output Folder:").grid(row=1, column=0)
    tk.Entry(root, textvariable=output_folder_var, width=40).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=browse_output_folder).grid(row=1, column=2)

    tk.Label(root, text="Output File Name:").grid(row=2, column=0)
    tk.Entry(root, textvariable=output_file_var).grid(row=2, column=1)
    
    tk.Label(root, text=".mp4 added automatically").grid(row=3, column=1)

    tk.Label(root, text="Prompt Font Size (20-50):").grid(row=4, column=0)
    tk.Entry(root, textvariable=font_size_var).grid(row=4, column=1)

    tk.Label(root, text="Max Prompt Text Width:").grid(row=5, column=0)
    tk.Entry(root, textvariable=max_width_var).grid(row=5, column=1)

    tk.Label(root, text="Image Duration (1-10 sec):").grid(row=6, column=0)
    tk.Entry(root, textvariable=image_duration_var).grid(row=6, column=1)

    # Generate button
    tk.Button(root, text="Generate Slideshow", command=generate_slideshow).grid(row=7, column=0, columnspan=3)

    root.mainloop()
