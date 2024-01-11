import ffmpeg
#NOTE: this requires having ffmpeg installed
# Path to the folder containing PNG files
png_folder = 'data/'

# Input PNG file pattern
input_pattern = png_folder + 'frame_%d.png'

# Output video file name
output_video = 'output_video.avi'

# Create a video using ffmpeg with Lagarith codec
(
    ffmpeg
    .input(input_pattern, framerate=1)  # Set frame rate
    .output(output_video, vcodec='lagarith', pix_fmt='rgb24')  # Lagarith codec with RGB24 pixel format
    .run()
)
