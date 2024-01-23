import subprocess
import sys
import os

def get_audio_duration(audio_path):
    """
    Returns the duration of the audio file in seconds.

    :param audio_path: Path to the audio file.
    :return: Duration in seconds.
    """
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

def calculate_video_duration(audio_duration, frame_rate):
    """
    Adjusts the video duration to include the entire audio, potentially adding one frame.

    :param audio_duration: Duration of the audio in seconds.
    :param frame_rate: Frame rate of the video.
    :return: Adjusted video duration in seconds.
    """
    # Calculate the number of frames needed for the audio duration
    total_frames = round(audio_duration * frame_rate)

    # Adjust for frame rate to get the video duration
    return total_frames / frame_rate

def find_files_by_extension(directory, extensions):
    """
    Find the first file in the given directory that matches one of the extensions.

    :param directory: Directory to search in.
    :param extensions: List of file extensions to look for.
    :return: Path to the found file or None if no file is found.
    """
    for file in os.listdir(directory):
        if any(file.lower().endswith(ext) for ext in extensions):
            return file
    return None

def create_video(image_path, audio_path, video_path, frame_rate=24, video_width=1920, video_height=1080, use_gpu=True):
    """
    Creates a video from a single image and an audio file.

    :param image_path: Path to the image file.
    :param audio_path: Path to the audio file.
    :param video_path: Path to the output video file.
    :param frame_rate: Frame rate of the video.
    :param video_width: Width of the video.
    :param video_height: Height of the video.
    """
    try:
        audio_duration = get_audio_duration(audio_path)
        video_duration = calculate_video_duration(audio_duration, frame_rate)

        # Calculate the necessary scale for the image
        scale_cmd = f"scale='min({video_width}/iw,{video_height}/ih)*iw':'min({video_width}/iw,{video_height}/ih)*ih'"
        pad_cmd = f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2"

        video_codec = 'h264_nvenc' if use_gpu else 'libx264'

        # Constructing the ffmpeg command
        command = [
            'ffmpeg',
            '-loop', '1',
            '-framerate', str(frame_rate),
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'h264_nvenc' if use_gpu else 'libx264',
            '-t', str(video_duration),
            '-vf', f"{scale_cmd},{pad_cmd}",
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            video_path
        ]

        # Execute the command
        subprocess.run(command, check=True)
        print(f"Video created successfully: {video_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error in video creation: {e}")

if __name__ == "__main__":
    

    if len(sys.argv) == 5:
        image_path, audio_path, video_path, frame_rate, use_gpu = sys.argv[1:6]
    else:
        print("No arguments provided. Searching for image and audio files in the current directory...")
        image_path = find_files_by_extension('.', ['.jpg', '.jpeg', '.png'])
        audio_path = find_files_by_extension('.', ['.mp3', '.wav', '.aac'])

        if not image_path or not audio_path:
            print("Could not find an image and/or audio file in the current directory.")
            sys.exit(1)

        # Default values
        video_path = os.path.splitext(audio_path)[0] + ".mp4"
        frame_rate = 24
        use_gpu = False  # Default GPU usage

    create_video(image_path, audio_path, video_path, frame_rate=int(frame_rate), use_gpu=use_gpu)
