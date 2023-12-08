from moviepy.editor import VideoFileClip
import os

def get_video_info(file_path):
    # Load the video clip
    video_clip = VideoFileClip(file_path)

    # Get video duration
    duration = video_clip.duration

    # Get video dimensions (width x height)
    dimensions = video_clip.size

    video_format = get_file_extension(file_path)
    # Get video size in bytes
    #file_size = video_clip.fps * duration * video_clip.bitrate / 8.0

    size_in_kbytes = os.path.getsize(file_path) // 1024

    return file_path, size_in_kbytes , dimensions , video_format , duration



def compress_video(input_path, output_path, bitrate='500k'):
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, bitrate=bitrate)    


def get_file_extension(file_name):
    # Use os.path.splitext() to split the file name and get the extension
    _, extension = os.path.splitext(file_name)
    
    # Remove the dot from the extension
    extension = extension.lstrip(".")

    return extension.lower()  # Convert to lowercase for consistency (optional)
