from pixelstore.resolutions import Resolutions
from pixelstore.color import Colors

from pixelstore import hash_gen
from PIL import Image
import os

import json
import math
import cv2
import numpy
import hashlib
#comment out the imports when pushing code

# how many pixels wide each metadata bit is
# keeping this big and fixed so the metadata frame doesnt get wrecked by compression
# also the decoder can read this even before it knows the actual data pix_size (thats stored inside the metadata itself lmao chicken and egg)
METADATA_CELL = 8

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
        >frame folder (directory to save the frames createds)

        
    """
    # pix_size = how many pixels make up one bit; keep it a perfect square (4->2x2, 16->4x4, 64->8x8)
    # bumped the default from 4 to 16 cause 2x2 cells get diluted to death by youtube compression
    # 4x4 survives the youtube bitrate cap; only drop back to 4 if youre sure the video stays lossless
    def __init__(self,filename,fps=24,pix_size=16,res=Resolutions.res_480p,frame_folder="generated_frames",output_folder="output"):
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
        self.end_x =-1 # keeping this as -1 cause 0 is a valid coordinate and decoder starts biching if its set to None
        self.end_y =-1 # keeping this as -1 cause 0 is a valid coordinate and decoder starts biching if its set to None
        self.no_of_frames=1
        
    
        
        
    # function to rip the bytes from a file and convert it into an array of bytes
    def rip_bytes(self)->list:
        file = open(self.filename,"rb")
        print(f"reading bytes from:{file.name}")
        raw_bytes =file.read(1)# reads the first byte of a file
        bit_sequence = []
        padded_bytes=[] # irrelevant for now
        count =0
        while raw_bytes: # reads a file till the bytes run out
            curr_byte = bin(int.from_bytes(raw_bytes,byteorder="big"))
            curr_byte = curr_byte[2:]
            if len(curr_byte) < 8:
                # fill up the lsb so if a byte is 1010 it will become 00001010
                # this is done so it becomes 8 bits ie one whole byte for easy parsing later on
                curr_byte = curr_byte.zfill(8) # check if this affects the checksum
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
         #filename = file_name +".mp4"
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
        # metadata frame always uses the fat fixed cell size, NOT the data pix_size (else decoder cant read it)
        pix_size = METADATA_CELL

        # grab the metadata bitstring ONCE here, the property re hashes the whole file every single time you touch it so calling it in the loop condition was hashing bigc like 900 times lmao
        mdata = self.metadata
        for x in range(0,width,pix_size):
            if mindex == len(mdata):
                break

            for y in range(0,height,pix_size):
                if mindex == len(mdata):
                    break
                pix_color = Colors.one if mdata[mindex] == "1" else Colors.zero
        
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
        
        #encode the end red pixel in the metadata(first) frame
        #pix_color = Colors.red
        #Encoder.etchpixel(mdata_frame,endx,endy,pix_color,pix_size)
        mdata_frame.save(os.path.join(self.frame_folder,f"frame0.png"))
        
        
    
    
    
    
    
    
    
    
    
    #encoder function
    def encode(self):


        
        #no_of_frames = 1
        
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
        
        rawbytes = self.ripped_bytes
        content=''.join(self.ripped_bytes)#.replace('\n','')
        image = Image.new('RGB', (width, height), color='white')
        
        #determine the no of frames
        # bits_per_frame = how many bits actually fit in one frame. each bit eats pix_size pixels not 1, so its total_pixels/pix_size NOT total_pixels
        # this is what the old code got wrong and thats why big files got chopped down to a single frame
        bits_per_frame = total_pixels // self.pix_size
        # no_of_frames = ceil of bits/bits_per_frame, ceil so the leftover bits that dont fill a whole frame still get their own frame
        self.no_of_frames = math.ceil(len(content) / bits_per_frame)

        #print(f"no of frames required:{no_of_frames}")
        print(f"using folder:{os.path.join(self.frame_folder)} to store the frames")
        #exit(0)
        # NOTE metadata (frame0) used to be embedded here BEFORE the loop and thats why it was always trash
        # end_x/end_y and nbits dont exist yet at this point, they only get filled while encoding
        # so moved the embed_mdata() call to AFTER the loop, look below
        for frame in range(1,self.no_of_frames+1):
            last_frame=frame
            #create a blank white image and overwrite the pixel values
            image = Image.new('RGB', (width, height), color='white')
            
            # this works and prints only 75 frames cause the frame value starts from 0 ;so 0 to 75 total 76 frames
            if count == len(content):
                    print("reached end of data bits")
                    break
                
            print(f"encoding frame :{frame} of {self.no_of_frames}",end="\r" )
            
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

        # last_frame = the real no of frames we actually wrote, can be less than no_of_frames if we hit the end of the bits and broke early
        self.no_of_frames = last_frame
        # nbits = exact count of data bits we wrote. the last frame is padded with white so without this the decoder cant tell the real bits from the padding
        self.nbits = count

        # NOW end_x/end_y and nbits are actually filled so its safe to write the metadata frame (frame0)
        self.embed_mdata()
        self.create_video()

        
    # function to create the video
    def create_video(self) ->None:
        width = self.res["width"]
        height = self.res["height"]
        png_folder = self.frame_folder
        """
        function to create the video
        """
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
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder)
            
        # video_name = where the avi gets dumped. the 0 in VideoWriter is the fourcc = raw/uncompressed so we dont lose bits at this stage
        video_name = os.path.join(self.output_folder,self.fileout)
        video = cv2.VideoWriter(video_name, 0, self.fps, (width,height)) # type:ignore
        # gotta go +1 here, frames on disk are frame0(metadata) upto frame{no_of_frames}(last data frame) so range needs to include the last one
        # old code did range(0,no_of_frames) and silently dropped the final data frame lol
        for image in range(0,self.no_of_frames+1):
            video.write(cv2.imread(os.path.join(self.frame_folder, f"frame{image}.png"))) # type:ignore
        video.release()

        outpath =os.path.join(self.output_folder,self.fileout)
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
        file_hash = hash_gen.get_md5(self.filename) #checksum of the original file
        metadataBytes=[] # ignore this for now
        if self.end_y == -1 or self.end_x == -1:
            print("metadata not getting updated dumbfuk")
            
        _metadata = {
                    "end_x" : self.end_x,
                    "end_y":self.end_y,
                    "nbits": getattr(self, "nbits", 0), # exact no of data bits, decoder cuts the bitstream down to this so the white padding at the end doesnt get turned into junk bytes
                    "pix_size": self.pix_size, # tell the decoder the data cell size, without this it would just guess 2x2 and desync the whole file
                    "filename":os.path.basename(self.filename), # basename only, dont want ./ or full paths ending up in the output name
                    "checksum":file_hash # md5 of the original file so decoder can check it came out clean
                    }

        # json.dumps not str(dict), str gives single quotes and json.loads on the decoder side shits itself on those
        _metadata = json.dumps(_metadata)

        for char in _metadata:
        # pad the bytes to 8 bits and append to list
            metadataBytes.append(bin(ord(char))[2:].zfill(8))
         
        # join the binary values in the list and return as a string
        return ''.join(metadataBytes)
        #pass
