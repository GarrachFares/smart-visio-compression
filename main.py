from flask import Flask, request, jsonify
from video import get_video_info, compress_video
from azure_file_uploader import store_file_to_bucket
from image import imageCompress
from urllib.parse import urlparse
import os
import requests

app = Flask(__name__)

@app.route("/compress/video")
def compress_video_router():
    url = request.json['url']
    max_size_kb = request.json['max_size_kb']
    #parsed_url = urlparse(url)
    #image_name_with_extension = os.path.basename(parsed_url.path)
    response = requests.get(url)
    # 3. Open the response into a new file called instagram.ico
    open("input2.mp4", "wb").write(response.content)
    input_info = get_video_info("input2.mp4")

    duration = input_info[4]

    max_bitrate = max_size_kb * 8  // duration

    mx_bitrate = min(300,max_bitrate)


    str_btr = str(int(mx_bitrate)) + 'k'

    

    compress_video("input2.mp4", "output_compressed.mp4", bitrate=str_btr)
    output_info = get_video_info("output_compressed.mp4")
    file_path = store_file_to_bucket("output_compressed.mp4")
    return jsonify({
        'type': 'video',
        'compressed_url': file_path,
        'input_weight': input_info[1],
        'output_weight': output_info[1],
        'input_dimensions': input_info[2],
        'output_dimensions': output_info[2],
        'input_format': input_info[3],
        'output_format': output_info[3]
    })   

@app.route("/compress/image", methods=["POST"])
def compress_image_router():
    url = request.json['url']
    max_size_kb = request.json['max_size_kb']
    parsed_url = urlparse(url)
    image_name_with_extension = os.path.basename(parsed_url.path)
    output_image_path, _ = os.path.splitext(image_name_with_extension)
    output_image_path = output_image_path + ".webp"

    # Call the imageCompress function
    result = imageCompress(url, output_image_path, max_size_kb)
    file_path = store_file_to_bucket(result[0])
    os.remove(output_image_path)
    # Return the results as JSON
    return jsonify({
        'type': 'image',
        'compressed_url': file_path,
        'input_weight': result[1],
        'output_weight': result[2],
        'input_dimensions': result[3],
        'output_dimensions': result[4],
        'input_format': result[5],
        'output_format': result[6]
    })

