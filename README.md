# sdxl-prompt-slideshow-gen
**SDXL Prompt Slideshow Generator**

This will go through a folder of SDXL images, extract the prompts and place them in the bottom part of the video with a drop shadow.

- Point it at a folder of SDXL images.
- Point it at an output folder and name the video.
- Adjust your settings
- Hit Generate

**Usage**

- Bring up GUI
`python ./slideshow.py`

![image](https://github.com/purzbeats/sdxl-prompt-slideshow-gen/assets/97489706/e61479ba-8609-4d71-afcd-d186e3e72ea3)

There are some probably some dependencies you will have to `pip install`

`debug_prompts.py` currently doesn't have a GUI, I was just using it to query the folder of images and see if the prompts work, you'll have to manually change the folder at the bottom to match the folder you want to scan

**Example Output**
https://github.com/purzbeats/sdxl-prompt-slideshow-gen/assets/97489706/cda3adcc-89b6-4889-abd9-e346edc27e7d

I used ChatGPT to make this tool, so _please_ feel free to make it much better.
