from PIL import Image
import os

import json
from dotenv import load_dotenv
import ffmpeg
import json
import math
import cv2
#getting the path of ffmpeg binary if its added using .env file
load_dotenv()
if os.environ.get('ffmpeg') is not None:
    ffmpeg_path = os.getenv("ffmpeg")
else:
    print("ffmpeg path not found please install ffmpeg binaries and add to environment variable or a .env file")
    print("or create a .env and add a ffmpeg variable with value of the path to the ffmpeg binary")
    exit(0)

if os.environ.get('ffprobe') is not None:
    ffprobe_path = os.getenv("ffprobe")
else:
    print("ffprobe path not found please install ffmpeg and add to environment variable")
    exit(0)    


#pixel colors
red=(255,0,0)
blue = (0, 0, 255)  # ignore this for now
one=(0,0,0)
zero = (255,255,255)

# separate class for resolutions
class resolutions:
    res_240p ={"width":426,"height":240,"total_pixels":426*240}
    res_360p ={"width":640,"height":360,"total_pixels":640*360}
    res_480p ={"width":640,"height":480,"total_pixels":640*480}
    #res_480p ={"width":854,"height":480,"total_pixels":854*480} # youtube recommended size for 480p
    res_720p ={"width":1280,"height":720,"total_pixels":1280*720}
    res_1080p ={"width":1920,"height":1080,"total_pixels":1920*1080}


#separate classes for encoder object and decoder object
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
    def __init__(self,filename,fps=6,pix_size=4,res=resolutions.res_480p,output_folder="data"):
        self.filename = filename
        self.output_folder = output_folder
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
    def rip_bytes(self):
        file = open(self.filename,"rb")
        print(f"reading bytes from:{file.name}")
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
            count+=1
        file.close()
        return bit_sequence
    
    #the output video file
    @property
    def fileout(self):
        infile = os.path.splitext(self.filename)
        file_name = infile[0] # get the name of the file
        extension = infile[1] # get the extenstion of file (txt,pdf,docx,etc.)
        #filename_ext_pixsize_.avi
        filename = file_name +"_"+ extension.strip(".") +"_"+ self.pix_size  +"_"+".avi"
        return os.path.join(filename)
        

    #encoder function that takes in the bytes and creates the frames
    def encode(self):

        if not os.path.exists("output"):
            os.mkdir("output")

        
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
        png_folder = self.output_folder

        # create the folder if it doesnt exist
        if not os.path.exists(png_folder):
            os.mkdir(png_folder)
        
        content=''.join(self.ripped_bytes)#.replace('\n','')
        image = Image.new('RGB', (width, height), color='white')
        
        #determine the no of frames 
        #if len(content) > total_pixels:
        #    no_of_frames = int((len(content)/total_pixels)+1)
        if len(content) > total_pixels:
            no_of_frames = int((len(content)*self.pix_size/total_pixels))+1

        #print(f"no of frames required:{no_of_frames}")
        for frame in range(no_of_frames):
            last_frame=frame
            #create a blank white image and overwrite the pixel values
            image = Image.new('RGB', (width, height), color='white')
            
            # this works and prints only 75 frames cause the frame value starts from 0 ;so 0 to 75 total 76 frames
            if count == len(content):
                    print("reached end of data bits")
                    break
                
            print(f"encoding frame :{frame} of {no_of_frames-1}",end="\r" )
            for x in range(0,width,pix_size):
                if count == len(content):
                    break
                for y in range(0,height,pix_size):
                    if count == len(content):
                        break
                    
                    curr_bit = content[count]
                    pix_color = one if curr_bit =='1' else zero
                    
                    for i in range(pix_size):
                        for j in range(pix_size):
                            image.putpixel((x+j,y+i),pix_color)
                    
                    

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
        for i in range(pix_size):
            for j in range(pix_size):
                image.putpixel((self.end_x+j, self.end_y+i), red)
        #image.save(f'data/encoded{last_frame}.png')
        image.save(os.path.join(png_folder,f"frame{last_frame}.png"))
        
        
        ####below this line is the ffmpeg encoder stuff


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
        print(f"done encoding to video :output/{self.fileout}")
    
    

    @property
    def metadata(self):
        """
        need to add metadata to the video itself
        such as the x and y coordinates of the end pixel of the raw bits
        add the original file name with extension to save when decoding
        hash of the file to verify the integrity? prolly will not be required
        
        """
        pass

#############################################################################################################
# the Decoder class below
#
class Decoder:
    
    def __init__(self,filename,output_folder="out"):
        self.filename=filename
        self.ripped_bytes =[]
        self.output_folder=output_folder
    
    @property
    def fileout(self):
        video_name = self.filename.split("_")
        return video_name[0] + "." + video_name[1]
    
    @property
    def metadata(self):
        #this method is to return the metadata about the video file in a json format
        m_data = ffmpeg.probe(self.filename,cmd=ffprobe_path) # type: ignore
        return m_data
    
    def extract_frames(self):
        #output pattern to take the video and convert to frames
        if not os.path.exists("frames"):
            os.mkdir("frames")
        
        output_pattern = os.path.join("frames","frame%d.png")
        (
            ffmpeg
            .input(self.filename)
            .output(output_pattern, start_number=0)  # Output frame pattern
            .run(cmd=ffmpeg_path)
        )

    def decode(self):

        self.extract_frames()

        no_of_frames = len(os.listdir("frames"))
        bits =""
        binary_bytes=[]
        #pix_size = int(math.sqrt(self.pixel_size)))
        pix_size = 2

        for frame in range(no_of_frames):
            x,y = 0,0
            image = Image.open(os.path.join("frames",f"frame_{frame}.png"))
            width, height = image.size
            pixels = image.load()
            print(f"decoding frame:{frame}")

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
                    if pix == 108 and frame ==no_of_frames-1: #after downloading from youtube pixel color changes
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

        
        
    
    

if __name__ == '__main__':
    pass