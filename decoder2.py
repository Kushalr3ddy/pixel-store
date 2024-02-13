from PIL import Image
import glob

import os
#image = Image.open("encoded.png")

red_color =(255,0,0)
one=(0,0,0)
zero = (255,255,255)

black =(255,255,255)
white =(0,0,0)
#define custom exception for reaching end of file
#ignore this for noe 

"""
class endoffile(Exception): 
    def __init__(self,description,message):  
        self.description =description
        self.message = message
"""

if not os.path.exists("out"):
    os.mkdir("out")
out = "out"

if not os.path.exists("frames"):
    os.mkdir("frames")
    
frames = "data" #from raw frames
#frames = "out" # from video frames
no_of_frames = len([x.endswith(".png") for x in os.listdir(frames) if x])

print(no_of_frames)
#exit(0)

all_pixels = []
bits_to_decode =[]
bits = ""
binary_bytes=[]


for frame in range(no_of_frames):
    x,y = 0,0
    image = Image.open(os.path.join(frames,f"encoded{frame}.png"))
    #image = Image.open(os.path.join(frames,f"frame_{frame}.png"))
    width, height = image.size
    pixels = image.load()
    print(f"decoding frame:{frame}")
    
    
    #print(image.size)
    for x in range(0,width,2):
        for y in range(0,height,2):
            
            pix=0
            for i in range(2):
                for j in range(2):
                    curr_pix = pixels[(x+j,y+i)] # check the bit checker below if you want to change this
                    pix += sum(curr_pix)/3

            pix/=4
            pix = int(pix)
            
            if pix == 85 and frame == no_of_frames-1:
            #if pix == 108: #after downloading from youtube pixel color changes
            #if pix == 108 and frame ==no_of_frames-1: #after downloading from youtube pixel color changes
            #if pix == red_color:
            
                print(f"reached end of file at:x:{x},y:{y}")
                print(f"len of bits:{len(bits)}")
                #print(pix,end="")
                #binary_bytes=[int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
                for i in range(0,len(bits),8):
                    curr_bit = int(bits[i:i+8],2)
                    binary_bytes.append(curr_bit) # type: ignore
                binary_bytes = bytes(binary_bytes)
                with open(f"{out}big_out.pdf", "wb") as file:
                    file.write(binary_bytes)
                    print("done writing bytes")
                    exit(0)


            else:
                if pix <= 127:
                #if pix == one:
                    bits+='1'
                elif pix > 127:
                #elif pix == zero:
                    bits+='0'
                #print(pix,end="")



