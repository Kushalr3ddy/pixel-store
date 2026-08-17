import ffmpeg
import os

def compress_video(input_file, output_file, crf=23):
    ffmpeg.input(input_file).output(output_file, **{'c:v': 'libx264', 'crf': crf}).run()

input_file = os.path.join("output","bigc.avi")
output_file = '50_compressed.mp4'
compression_factor = 50  # Adjust this value to change the compression level

compress_video(input_file, output_file, crf=compression_factor)