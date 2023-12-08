from flask import Flask, request, jsonify, render_template
from azure.storage.blob import generate_blob_sas, BlobServiceClient, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uuid
import os
from urllib.parse import urlparse
from PIL import Image
from moviepy.editor import VideoFileClip
import requests
from io import BytesIO


def compress_video(input_path, output_path, bitrate='500k'):
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, bitrate=bitrate)

def store_file_to_bucket(file_path):
    # Set the connection string to your Azure Blob Storage account and return file url
    
    load_dotenv()
    connection_string = str(os.getenv("CONNECTION_STRING"))
    account_key = str(os.getenv("ACCOUNT_KEY"))
    account_name = "compressedfiles" 
    container_name = "compressed"

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    #create a unique name for the blob
    unique_identifier = uuid.uuid4()
    blob_name = str(unique_identifier) + file_path #"testblobname2.mp4"#os.path.relpath(local_file_path, local_folder_path).replace("\\", "/")

    # Create a BlobClient object for the file
    blob_client = container_client.get_blob_client(blob_name)

    # Upload the file to Azure Blob Storage
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Set the expiration time for the SAS token
    expiration_time = datetime.utcnow() + timedelta(hours=1)  # Adjust the duration as needed

    # Set permissions for the SAS token
    permissions = BlobSasPermissions(read=True)  # Adjust permissions as needed

    # Generate SAS token
    sas_token = generate_blob_sas(account_name=account_name,
                                container_name=container_name, 
                                blob_name=blob_name, 
                                account_key=account_key,
                                permission=permissions,
                                expiry=expiration_time)

    # Construct the URL with the SAS token
    blob_url_with_sas = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

    #print("Public link with SAS token:", blob_url_with_sas)  
    return blob_url_with_sas  

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('/index.html')

@app.route("/compress/video")
def compress_video_router():
    compress_video("input.mp4", "output_compressed.mp4", bitrate='10k')
    file_path = store_file_to_bucket("output_compressed.mp4")
    return file_path    

@app.route("/compress/image", methods=["POST"])
def compress_image_router():
    url = request.json['url']
    max_size_kb = request.json['max_size_kb']
    max_size_kb = int(max_size_kb)
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
        'compressed_url': file_path,
        'input_weight': result[1],
        'output_weight': result[2],
        'input_dimensions': result[3],
        'output_dimensions': result[4],
        'input_format': result[5],
        'output_format': result[6]
    })


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