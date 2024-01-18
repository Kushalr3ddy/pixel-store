import ffmpeg
import os

from dotenv import load_dotenv

load_dotenv()
ffmpeg_path = os.getenv("ffmpeg")
#ffmpeg_path = "C:\\Users\\pikki\\Desktop\\everything\\pixel-store\\ffmpeg_build\\bin\\ffmpeg.exe"
print(ffmpeg_path)
#os.system(f"{os.getenv('ffmpeg')} -version")
#exit(0)
#NOTE: this requires having ffmpeg installed
# Path to the folder containing PNG files
png_folder = 'data/'

if not os.path.exists(png_folder):
    os.mkdir(png_folder)


# Input PNG file pattern
input_pattern = png_folder + 'encoded%d.png'

# Output video file name
output_video = 'output_video.avi'

# Create a video using ffmpeg with Lagarith codec
(
    ffmpeg
    .input(input_pattern, framerate=1)  # Set frame rate
    .output(output_video, vcodec='huffyuv', pix_fmt='rgb24')  # Lagarith codec with RGB24 pixel format
    .run(cmd=ffmpeg_path)
)
