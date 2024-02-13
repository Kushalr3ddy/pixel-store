import ffmpeg
import os
from dotenv import load_dotenv

load_dotenv()

ffmpeg_path = os.getenv("ffmpeg")
print(ffmpeg_path)

#exit(0)
# Input video file
#input_video = 'output_video.avi'

input_video = 'output video.mp4'
#input_video = 'videoplayback.mp4'

# Output folder for extracted frames
output_folder = 'out'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)


# Create the output folder if it doesn't exist
#ffmpeg.input(input_video).output(output_folder).run(overwrite_output=True)
#os.chdir("out/")
# Extract frames from the video
(
    ffmpeg
    .input(input_video)
    .output(os.path.join(output_folder,'frame_%d.png'), start_number=0)  # Output frame pattern
    .run(cmd=ffmpeg_path,overwrite_output=True)
)
