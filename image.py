from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
import requests
import os

def imageCompress(url, output_image_path, max_size_kb):
     # Download the image file
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    # Get input details
    input_weight = len(response.content) // 1024  # Size in KB
    input_dimensions = img.size
    input_format = img.format

    # Convert the image to RGB mode, as WebP format doesn't support RGBA
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Start with high quality
    quality = 90

    # Save the image again with reduced quality in WebP format
    img.save(output_image_path, 'webp', quality=quality)

    # While the image size is larger than the max size, reduce the quality
    while os.path.getsize(output_image_path) > max_size_kb * 1024 and quality > 0:
        quality -= 10  # Reduce quality by 10 each time
        img.save(output_image_path, 'webp', quality=quality)
    # Get output details
    output_weight = os.path.getsize(output_image_path) // 1024  # Size in KB
    output_dimensions = img.size
    output_format = 'WEBP'

    return output_image_path, input_weight, output_weight, input_dimensions, output_dimensions, input_format, output_format


if __name__ == '__main__':
    app.run(debug=True)