import subprocess
import sys

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

def create_video(image_path, audio_path, video_path, frame_rate=30, video_width=1920, video_height=1080):
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

        # Constructing the ffmpeg command
        command = [
            'ffmpeg',
            '-loop', '1',
            '-framerate', str(frame_rate),
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'libx264',
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
    if len(sys.argv) != 5:
        print("Usage: python master.py <image_path> <audio_path> <video_path> <frame_rate>")
        sys.exit(1)

    image_path, audio_path, video_path, frame_rate = sys.argv[1:5]
    create_video(image_path, audio_path, video_path, frame_rate=int(frame_rate))
