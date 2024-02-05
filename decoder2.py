from PIL import Image
import glob

import os
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

if not os.path.exists("out"):
    os.mkdir("out")
out = "out"

if not os.path.exists("frames"):
    os.mkdir("frames")
    
frames = "data"
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
    width, height = image.size
    pixels = image.load()
    print(f"decoding frame:{frame}")
    
    #pixels = image.getdata() # experiment with this once (see pillow docs)
    #print(image.size)
    for x in range(0,width,2):
        for y in range(0,height,2):
            pix_r =0
            pix_g =0
            pix_b =0
            
            for i in range(2):
                for j in range(2):
                    pix_r += pixels[(x+j,y+i)][0]
                    pix_g += pixels[(x+j,y+i)][1]
                    pix_b += pixels[(x+j,y+i)][2]
                    
            r_avg = int(pix_r/4)
            g_avg = int(pix_g/4)
            b_avg = int(pix_b/4)

            rgb_avg = (r_avg,b_avg,g_avg)
            pix = (r_avg,b_avg,g_avg)
            #pix = (r_avg+g_avg+b_avg)/3 # check the bit checker below if you want to change this
            if pix == red_color:
                print(f"reached end of file at:x:{x},y:{y}")
                print(f"len of bits:{len(bits)}")
                #print(pix,end="")
                #binary_bytes=[int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
                for i in range(0,len(bits),8):
                    curr_bit = int(bits[i:i+8],2)
                    binary_bytes.append(curr_bit) # type: ignore
                binary_bytes = bytes(binary_bytes)
                with open("big_out.pdf", "wb") as file:
                    file.write(binary_bytes)
                    print("done writing bytes")
                    exit(0)


            else:
                if sum(pix)/3 >= 127:
                    bits+='1'
                elif sum(pix)/3 <127:
                    bits+='0'
                #print(pix,end="")



