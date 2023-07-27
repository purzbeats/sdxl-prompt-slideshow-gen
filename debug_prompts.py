import os
import json
import subprocess

def extract_prompt_text(image_path):
    cmd = ['exiftool', '-s', '-Prompt', '-b', image_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    prompt_json = result.stdout.strip()
    # print("ExifTool output:", prompt_json)  # Add this print statement

    prompt_data = json.loads(prompt_json)

    # Access the 'text' field from the nested dictionary
    prompt_text = prompt_data.get('6', {}).get('inputs', {}).get('text', '')
    return prompt_text

def debug_extract_prompts(images_folder):
    image_files = [f for f in os.listdir(images_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]

    for image_file in image_files:
        image_path = os.path.join(images_folder, image_file)
        prompt = extract_prompt_text(image_path)
        print(f"Image: {image_file}, Prompt: {prompt}")

if __name__ == "__main__":
    images_folder = "/ai/thing/test/"
    debug_extract_prompts(images_folder)
