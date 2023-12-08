# Image and Video Compression App

This is a Python Flask application that allows users to compress both images and videos. It provides a simple web api for users to upload their media files, which are then processed and compressed.

## Features

- Image compression: Upload and compress image files.
- Video compression: Upload and compress video files.
- User-friendly web api.

## the API

this API contains two endpoints :
-/compress/image
-/compress/video

with the body containing :
{
	"url":"your_image_url/your_video_url",
	"max_size_kb": 100
}

## Prerequisites

Make sure you have the following installed before running the application:

- Python 3.x
- Flask
- Pillow (PIL Fork)
- moviepy
- (Any additional dependencies)

You can install the dependencies using the following command:

```bash

pip install -r dependencies.txt

then 

python app.py






