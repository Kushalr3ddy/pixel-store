import cv2
import os
from PIL import Image
import glob

# Path to the video file
video_path = 'video.mp4'

# open the video file
cap = cv2.VideoCapture(video_path)


frame_count = 0


while True:
    # Read a frame from the video
    ret, frame = cap.read()

    # Check if frame was successfully read
    if not ret:
        break

    # Save the frame as an image
    cv2.imwrite(f'test/frame_{frame_count}.png', frame)

    # Increment frame count
    frame_count += 1

# Release the video capture object and close the window
cap.release()
cv2.destroyAllWindows()






#image = Image.open("encoded.png")


white =(0,0,0)
black =(255,255,255)
red_color =(255,0,0)

#define custom exception for reaching end of file
#ignore this for noe 
"""
class endoffile(Exception): 
    def __init__(self,description,message):  
        self.description =description
        self.message = message
"""
no_of_frames = len(glob.glob1("out/","*.jpg"))

print(no_of_frames)
#exit(0)

all_pixels = []
bits_to_decode =[]
bits = ""
binary_bytes=[]

for frame in range(no_of_frames):
    x,y = 0,0
    image = Image.open(f"out/frame_{frame}.jpg")
    width, height = image.size
    pixels = image.load()
    print(f"decoding frame:{frame}")
    
    #pixels = image.getdata() # experiment with this once (see pillow docs)
    #print(image.size)
    for x in range(width):
        for y in range(height):
            
            pix = pixels[(x,y)]
            if tuple(pix) == red_color:
                print(f"reached end of file at:x:{x},y:{y}")
                #print(pix,end="")
                #binary_bytes=[int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
                for i in range(0,len(bits),8):
                    curr_bit = int(bits[i:i+8],2)
                    binary_bytes.append(curr_bit)
                binary_bytes = bytes(binary_bytes)
                with open("final_out.pdf", "wb") as file:
                    file.write(binary_bytes)


            else:
                if pix == white:
                    bits+='1'
                elif pix==black:
                    bits+='0'
                #print(pix,end="")



