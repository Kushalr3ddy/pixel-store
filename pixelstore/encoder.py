from pixelstore.resolutions import Resolutions
from pixelstore.color import Colors

from PIL import Image
import os

import json
import math
import cv2
import numpy

#comment out the imports when pushing code

class Encoder:

    
    """
    
    Encoder attributes:
        
        >filename (input file to encode)
        >filesize
        >ripped bytes (rawbytes of the file)
        >output_filename(encoded video)
        >fps (for the video)
        >filetype(extension of the input file)
        >end_pixel
        >no of frames (of the video file)
        >hash of the file (optional for future usage)

        
    """
    def __init__(self,filename,fps=6,pix_size=4,res=Resolutions.res_480p,frame_folder="data",output_folder="output"):
        self.filename = filename
        self.frame_folder = frame_folder
        self.output_folder=output_folder
        
        self.ripped_bytes = self.rip_bytes() # size of file in no of bits where total_bits = total_bytes*8
        self.size = len(self.ripped_bytes) *8 # size of file in no of bits where total_bits = total_bytes*8
        #self.fileout =fileout
        self.fps = fps
        self.pix_size = pix_size # make sure the pix_sizes are only squares i.e 4,9,16.... and that they should divide the height and width perfectly
        self.res = res
        #below are the coordinate of the end pixel after the content bits are finished
        self.end_x =0
        self.end_y =0
        
    
        
        
    # function to rip the bytes from a file and convert it into an array of bytes
    def rip_bytes(self)->list:
        file = open(self.filename,"rb")
        print(f"reading bytes from:{file.name}")
        raw_bytes =file.read(1)
        bit_sequence = []
        padded_bytes=[] # irrelevant for now
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
            count+=1
        file.close()
        return bit_sequence
    
    #the output video file
    @property
    def fileout(self) ->str:
        infile = os.path.splitext(self.filename)
        file_name = infile[0] # get the name of the file
        extension = infile[1] # get the extenstion of file (txt,pdf,docx,etc.)
        #filename_ext_pixsize_.avi
        #filename = file_name +"_"+ extension.strip(".") +"_"+ self.pix_size  +"_"+".avi"
        filename = file_name +".avi"
        return os.path.join(filename)
        
    @staticmethod # needs limit and error checking 
    def etchpixel(image,x:int,y:int,pix_color:tuple,pix_size:int) ->None:
        for i in range(pix_size):
            for j in range(pix_size):
                image.putpixel((x+j,y+i),pix_color)

    #first frame for storing the metadata
    def embed_mdata(self) ->None:
        width = self.res["width"]
        height =self.res["height"]
        mdata_frame = Image.new('RGB',(width, height), color='white')
        mindex =0 # index for the metadata string
        endx = 0
        endy=0
        pix_size = int(math.sqrt(self.pix_size))

        print(f"length of metadata:{len(self.metadata)}")
        #exit(0)
        for x in range(0,width,pix_size):
            if mindex == len(self.metadata):
                break

            for y in range(0,height,pix_size):
                if mindex == len(self.metadata):
                    break
                pix_color = Colors.one if self.metadata[mindex] == "0" else Colors.zero
        
                Encoder.etchpixel(mdata_frame,x,y,pix_color,pix_size)
                
                
                
                endx=x
                endy=y
                mindex+=1
        
        #check where the bits end
        if endy+pix_size < height:
            endy+=pix_size
        else:
            endx+=1
            endy=0
        
        pix_color = Colors.red
        Encoder.etchpixel(mdata_frame,endx,endy,pix_color,pix_size)
        mdata_frame.save(os.path.join(self.frame_folder,f"frame0.png"))
        
        
    
    
    
    
    def generate_frame(self):
        pass
    
    
    
    
    #encoder function that takes in the bytes and creates the frames
    def encode(self):


        
        no_of_frames = 1
        
        # test with 480p for now later add other resolutions
        width = self.res["width"]
        height = self.res["height"]

        total_pixels = width * height
        x,y = 0,0
        count = 0
        last_frame =0
        
        pix_size = int(math.sqrt(self.pix_size))
        # this is for storing all the images (frames) that are created as a result of converting bits to pixels
        png_folder = self.frame_folder

        # create the folder if it doesnt exist
        if not os.path.exists(png_folder):
            print(f"{self.frame_folder}/ not found creating {self.frame_folder}/ ")
            os.mkdir(png_folder)
        
        content=''.join(self.ripped_bytes)#.replace('\n','')
        image = Image.new('RGB', (width, height), color='white')
        
        #determine the no of frames 
        #if len(content) > total_pixels:
        #    no_of_frames = int((len(content)/total_pixels)+1)
        if len(content) > total_pixels:
            no_of_frames = int((len(content)*self.pix_size/total_pixels))+1

        #print(f"no of frames required:{no_of_frames}")
        print(f"using folder:{os.path.join(self.frame_folder)} to store the frames")
        #exit(0)
        #put the metadata frame as frame0
        self.embed_mdata()
        
        for frame in range(1,no_of_frames+1):
            last_frame=frame
            #create a blank white image and overwrite the pixel values
            image = Image.new('RGB', (width, height), color='white')
            
            # this works and prints only 75 frames cause the frame value starts from 0 ;so 0 to 75 total 76 frames
            if count == len(content):
                    print("reached end of data bits")
                    break
                
            print(f"encoding frame :{frame} of {no_of_frames+1}",end="\r" )
            
            for x in range(0,width,pix_size):
                if count == len(content):
                    break
                for y in range(0,height,pix_size):
                    if count == len(content):
                        break
                    
                    curr_bit = content[count]
                    pix_color = Colors.one if curr_bit =='1' else Colors.zero
                    
                    Encoder.etchpixel(image,x=x,y=y,pix_color=pix_color,pix_size=pix_size)
                    
                    

                    count+=1
                    self.end_x=x
                    self.end_y=y

            #image.save(f'data/encoded{frame}.png')
            image.save(os.path.join(png_folder,f"frame{frame}.png"))
                
        #check where the bits end
        if self.end_y+pix_size < height:
            self.end_y+=pix_size
        else:
            self.end_x+=1
            self.end_y=0
        
        #put the red pixel after the last bit encoded to indicate the end bit
        """for i in range(pix_size):
            for j in range(pix_size):
                image.putpixel((self.end_x+j, self.end_y+i), red)"""
        Encoder.etchpixel(image,x=x,y=y,pix_color=pix_color,pix_size=pix_size)
        #image.save(f'data/encoded{last_frame}.png')
        image.save(os.path.join(png_folder,f"frame{last_frame}.png"))
        
        
        ####below this line is the ffmpeg encoder stuff

        """
        #image = Image.new
        input_pattern = os.path.join(png_folder,"frame%d.png")
        output_video = os.path.join("output",self.fileout)
        (
        ffmpeg
        .input(input_pattern,framerate = self.fps)
        .output(output_video, vcodec='huffyuv', pix_fmt='rgb24')
        .overwrite_output()
        .run(cmd=ffmpeg_path)
        )
        print(f"done encoding to video :output/{self.fileout}")"""
        video_name = os.path.join(self.output_folder,self.fileout)
        video = cv2.VideoWriter(video_name, 0, self.fps, (width,height)) # type:ignore
        # why n-1 frames is cause the final frame will be put separately
        for image in range(0,no_of_frames):
            video.write(cv2.imread(os.path.join(png_folder, f"frame{image}.png"))) # type:ignore
        
        #this is unnecessary
        outpath =os.path.join(png_folder,self.fileout)
        print(f"saved the video to :{outpath}")
    
    
    @property
    def metadata(self):
        """
        this function returns the metadata required in binary string format i.e "1000101..."
        first frame is reserved for metadata
        such as the x and y coordinates of the end pixel of the raw bits
        add the original file name with extension to save when decoding
        hash of the file to verify the integrity? prolly will not be required
        
        """
        metadataBytes=[]
        _metadata = {"pixel_size":self.pix_size,
                     "end_x" : self.end_x,
                     "end_y":self.end_y,
                     "filename":self.filename
                     }
        
        _metadata = str(_metadata)
        
        for char in _metadata:
        # pad the bytes to 8 bits and append to list
            metadataBytes.append(bin(ord(char))[2:].zfill(8))
         
        # join the binary values in the list and return as a string
        return ''.join(metadataBytes)
        #pass
