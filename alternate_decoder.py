import ffmpeg
import os

# Input video file
input_video = 'output_video.avi'

# Output folder for extracted frames
output_folder = 'out/'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)


# Create the output folder if it doesn't exist
#ffmpeg.input(input_video).output(output_folder).run(overwrite_output=True)

# Extract frames from the video
(
    ffmpeg
    .input(input_video)
    .output('frame_%d.png', start_number=0)  # Output frame pattern
    .run()
)
