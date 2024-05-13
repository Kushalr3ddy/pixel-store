from pixelstore.resolutions import Resolutions
from pixelstore.color import Colors

from PIL import Image
import os
import json
import math
import cv2
import numpy


#comment out the imports when pushing code

#############################################################################################################
# the Decoder class below
#############################################################################################################

class Decoder:
    
    def __init__(self,filename,frame_folder="frames"):# out is the folder to output the extracted frames
        self.filename=filename # video file name
        self.ripped_bytes =[] # to store the extracted frames
        self.extraction_folder=frame_folder # the output folder for the frames? the embedded_file
    
    @property
    def fileout(self):
        video_name = self.filename.split("_")
        return video_name[0] + "." + video_name[1]
    
    @property
    def metadata(self):
        mdataFramePath = os.path.join(self.extraction_folder,"frame0.png")
        if not os.path.exists(mdataFramePath):
            print("metadata frame not found i.e frame0.png not found")
            print(f"extracting frames from {self.filename}")
            self.extract_frames()
        print(f"metadata frame found at: {self.extraction_folder}/")
        
        im = Image.open(os.path.join(self.extraction_folder,"frame0.png"))
        width,height =im.size
        pixels = im.load()
        mdata_bits=[]
        binary_bytes=[]
        check=1
        for x in range(0,width,2):
            if not check:
                break
            for y in range(0,height,2):
                if not check:
                    break
                r_avg=0
                g_avg=0
                b_avg=0
                
                
                pix=0
                for i in range(2):
                    for j in range(2):
                        r,g,b = pixels[(x+j,y+i)]
                        r_avg +=r
                        g_avg+=g
                        b_avg+=b
                        
                        
                        #curr_pix = pixels[(x+j,y+i)] # check the bit checker below if you want to change this
                        #pix += sum(curr_pix)/3
                r_avg/=4
                g_avg/=4
                b_avg/=4
                
                #pix/=4
                #pix = int(pix)
                
                #pix = pixels[(x,y)]
                
                #print(pix,end = ", ")
                #if pix == Colors.red:# or int(sum(pix)/3) == 108:
                #if pix == 108:
                #if pix[0] > pix[1] and pix[0] > pix[2]:
                if r_avg > 150 and g_avg < 100 and b_avg < 100:
                    print(f"found red pixel at x:{x} y:{y}")
                    try:
                        mdata = str(mdata_bits)
                        for i in range(0,len(mdata_bits),8):
                            byte = int(mdata[i:i+8],2) # type: ignore
                            binary_bytes.append(byte) # type: ignore
                        binary_bytes = bytes(binary_bytes)
                        #return mdata
                        return binary_bytes
                    
                    
                    
                    except Exception as e:
                        print(mdata)
                        raise(e)
                        print("something wrong with the metadata extraction:")
                        print(e)
                else:
                    curr_bit = "1" if pix == Colors.one else "0"
                    mdata_bits.append(curr_bit)
                
        return "lmao"
    
    def extract_frames(self):
        #output pattern to take the video and convert to frames
        if not os.path.exists(self.extraction_folder):
            os.mkdir(self.extraction_folder)
        
        video_file = cv2.VideoCapture(self.filename) # type: ignore
  
        # Used as counter variable 
        count = 0
    
        # checks whether frames were extracted 
        
        frameno = 0
        while(True):
            ret,frame = video_file.read()
            if ret:
                # if video is still left continue creating images
                
                print(f"extracting frame:{frameno}",end="\r")

                cv2.imwrite(os.path.join(self.extraction_folder,f"frame{frameno}.png"), frame) # type: ignore
                frameno += 1
            else:
                break
        video_file.release()
        cv2.destroyAllWindows() # type: ignore
        
    
    
            




    def decode(self):

        self.extract_frames()

        no_of_frames = len(os.listdir(self.extraction_folder))
        bits =""
        binary_bytes=[]
        #pix_size = int(math.sqrt(self.pixel_size)))
        pix_size = 2

        for frame in range(1,no_of_frames):
            x,y = 0,0
            image = Image.open(os.path.join(self.extraction_folder,f"frame_{frame}.png"))
            width, height = image.size
            pixels = image.load()
            print(f"decoding frame:{frame}")
            
            for x in range(0,width,pix_size):
                for y in range(0,height,pix_size):

                    pix=0
                    for i in range(2):
                        for j in range(2):
                            curr_pix = pixels[(x+j,y+i)] # check the bit checker below if you want to change this
                            pix += sum(curr_pix)/3

                    pix/=4
                    pix = int(pix)

                    #if pix == 85 and frame == no_of_frames-1:
                    #if pix == 108: #after downloading from youtube pixel color changes
                    if pix == 108 and frame == no_of_frames-1: #after downloading from youtube pixel color changes
                    #if pix == red_color:

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
                        if pix <= 127:
                        #if pix == one:
                            bits+='1'
                        elif pix > 127:
                        #elif pix == zero:
                            bits+='0'
                        #print(pix,end="")
