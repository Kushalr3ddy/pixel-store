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
        frame_path = os.path.join(self.extraction_folder,"frame0.png")
        print(frame_path)
        if not os.path.exists(frame_path):#,"frame0.png")):
            print("metadata frame not found i.e frame0.png not found")
            return None
        im = Image.open(os.path.join(self.extraction_folder,"frame0.png"))
        width,height =im.size
        pixels = im.load()
        mdata_bits=[]
        binary_bytes=[]
        for x in range(0,width,2):
            for y in range(0,height,2):
                pix = pixels[(x,y)]
                if pix == Colors.red:# or int(sum(pix)/3) == 108:
                    print("foudn red pixel")
                    try:
                        mdata = str(mdata_bits)
                        for i in range(0,len(mdata_bits),8):
                            bit = int(mdata_bits[i:i+8],2)
                            binary_bytes.append(bit) # type: ignore
                        binary_bytes = bytes(binary_bytes)
                        return mdata
                    
                    except Exception as e:
                        print("something wrong with the metadata extraction:")
                        print(e)
                curr_bit = "1" if pix == Colors.one else "0"
                mdata_bits.append(curr_bit)
                
    
    
    
    
    
    
    @staticmethod
    def extract_data(image):
        width, height = image.size
        pixels = image.load()
        
        
        #pixels = image.getdata() # experiment with this once (see pillow docs)
        #print(image.size)
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
    
    

        
        
    
    def extract_frames(self):
        #output pattern to take the video and convert to frames
        if not os.path.exists(self.extraction_folder):
            os.mkdir(self.extraction_folder)
        
        video_file = cv2.VideoCapture(self.filename)
  
        # Used as counter variable 
        count = 0
    
        # checks whether frames were extracted 

        frameno = 0
        while(True):
            ret,frame = video_file.read()
            if ret:
                # if video is still left continue creating images
                
                print(f"extracting frame:{frameno}",end="\r")

                cv2.imwrite(os.path.join(self.extraction_folder,f"frame{frameno}.png"), frame)
                frameno += 1
            else:
                break
        video_file.release()
        cv2.destroyAllWindows()
        
    
    
            




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
            print(f"decoding frame:{frame}")
    
