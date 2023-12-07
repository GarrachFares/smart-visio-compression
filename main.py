from flask import Flask
from moviepy.editor import VideoFileClip
#azure
from azure.storage.blob import generate_blob_sas, BlobServiceClient, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uuid
import os

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
def hello_world():
    # Example usage
    return "<p>Hello, World!</p>"

@app.route("/compress/video")
def compress_video_router():
    compress_video("input.mp4", "output_compressed.mp4", bitrate='10k')
    file_path = store_file_to_bucket("output_compressed.mp4")
    return file_path    

@app.route("/compress/image")
def compress_image_router():
    # Example usage
    compress_video("input.mp4", "output_compressed.mp4", bitrate='10k')
    file_path = store_file_to_bucket("output_compressed.mp4")
    return file_path        