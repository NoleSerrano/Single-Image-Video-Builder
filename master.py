import subprocess
import sys

def create_video_from_image(image_path, video_path, duration):
    """
    Creates a video from a single image.

    :param image_path: Path to the image file.
    :param video_path: Path to the output video file.
    :param duration: Duration of the video in seconds.
    """
    try:
        # Constructing the ffmpeg command
        command = [
            'ffmpeg',
            '-loop', '1',
            '-i', image_path,
            '-c:v', 'libx264',
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1920:1080',
            video_path
        ]

        # Execute the command
        subprocess.run(command, check=True)
        print(f"Video created successfully: {video_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error in video creation: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python master.py <image_path> <video_path> <duration_in_seconds>")
        sys.exit(1)

    image_path, video_path, duration = sys.argv[1], sys.argv[2], sys.argv[3]
    create_video_from_image(image_path, video_path, duration)
