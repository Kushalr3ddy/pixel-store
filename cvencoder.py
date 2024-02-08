import cv2
import os

import numpy as np
import math




# resolutions
res_240p ={"width":426,"height":240,"total_pixels":426*240}
res_360p ={"width":640,"height":360,"total_pixels":640*360}
#res_480p ={"width":640,"height":480,"total_pixels":640*480}
res_480p ={"width":854,"height":480,"total_pixels":854*480} # youtube recommended size for 480p
res_720p ={"width":1280,"height":720,"total_pixels":1280*720}
res_1080p ={"width":1920,"height":1080,"total_pixels":1920*1080}


# initially no of frames is 1 if the no of bits < no of pixels
no_of_frames=1

#defining the pixels to represent colors 
red_color =(255,0,0)
blue_color = (0, 0, 255)  

green_color=(0,255,0)
one=(0,0,0)
zero = (255,255,255)

#file = open("padded_bytes.txt","r")
#read the file containing raw bit data as strings and remove the newline characters
file = open("bigc.pdf","rb")

if not os.path.exists("data"):
    os.mkdir("data")    

png_folder ="data"


raw_bytes =file.read(1)
bit_sequence = []
padded_bytes=[]
count =0


while raw_bytes:
    curr_byte = bin(int.from_bytes(raw_bytes,byteorder="big"))
    curr_byte = curr_byte[2:]
    if len(curr_byte) < 8:
        # fill up the lsb so if a byte is 1010 it will become 00001010
        # this is done so it becomes 8 bits ie one whole byte for easy parsing later on
        curr_byte = curr_byte.zfill(8)
        padded_bytes.append(count)
    #print((curr_byte))#,end=" ")
    raw_bytes = file.read(1)
    bit_sequence.append(curr_byte)
    

content=''.join(bit_sequence)#.replace('\n','')
print(len(content))




# Define the image width and height
image_width = res_480p["width"]
image_height = res_480p["height"]



# Create a black image
black_image = 255 * np.ones((image_height, image_width, 3), dtype=np.uint8)  # 3 channels (BGR)

# set pixel values based on binary content
index = 0
pix_size=4 # make sure that these are square number i.e 4,9,16....
pix_size =int(math.sqrt(pix_size))

for y in range(0,image_height,pix_size):
    for x in range(0,image_width,pix_size):
        if content[index] == '1':
            pix_color = [0, 0, 0]  # Set pixel to black
        else:
            pix_color = [255, 255, 255]  # Set pixel to white
        
        for i in range(pix_size):
            for j in range(pix_size):
                black_image[y+j, x+i] = pix_color

        index += 1

# Display the image
cv2.imshow('Black and White Image', black_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
