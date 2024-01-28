from PIL import Image

import os
import json
from dotenv import load_dotenv
import ffmpeg
import json
#getting the path of ffmpeg binary
load_dotenv()
ffmpeg_path = os.getenv("ffmpeg")
ffprobe_path = os.getenv("ffprobe")


#pixel colors
red=(255,0,0)
blue = (0, 0, 255)  # ignore this for now
one=(0,0,0)
zero = (255,255,255)

# resolutions
res_240p ={"width":426,"height":240,"total_pixels":426*240}
res_360p ={"width":426,"height":360,"total_pixels":426*360}
res_480p ={"width":426,"height":240,"total_pixels":426*240}
res_720p ={"width":426,"height":240,"total_pixels":426*240}
res_1080p ={"width":426,"height":240,"total_pixels":426*240}


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
    def __init__(self,filename,fps=1):
        self.filename = filename
        self.size = len(self.ripped_bytes) *8 # size of file in no of bits
        #self.fileout =fileout
        self.fps = fps
        
        
    @property
    def ripped_bytes(self):
        file = open(self.filename,"rb")
        
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
        return bit_sequence
    
    @property
    def fileout(self):
        filename = os.path.splitext(self.filename)
        file_name = filename[0] # get the name of the file
        extension = filename[1] # get the extenstion of file (txt,pdf,docx,etc.)

        return file_name +"_"+ extension.strip(".") +"_"+".avi"
        

    def encode(self):
        
        no_of_frames = 1
        width, height = 640,480 # test with 480p for now later add other resolutions
        total_pixels = width * height
        x,y = 0,0
        count = 0
        last_frame =0
        
        # this is for storing all the images (frames) that are created as a result of converting bits to pixels
        png_folder ="frames"

        # create the folder if it doesnt exist
        if not os.path.exists(png_folder):
            os.mkdir(png_folder)
        
        content=''.join(self.ripped_bytes)#.replace('\n','')
        image = Image.new('RGB', (width, height), color='white')
        
        #determine the no of frames 
        if len(content) > total_pixels:
            no_of_frames = int((len(content)/total_pixels)+1)
        
        #print(f"no of frames required:{no_of_frames}")
        for frame in range(no_of_frames):
            last_frame=frame
            #create a blank white image and overwrite the pixel values
            image = Image.new('RGB', (width, height), color='white')
            
            # this works and prints only 75 frames cause the frame value starts from 0 ;so 0 to 75 total 76 frames
            if count == len(content):
                    print("reached end of data bits")
                    break
                
            print(f"encoding frame :{frame}" )
            for x in range(width):
                if count == len(content):
                        print("reached end of data bits")
                        break
                    
                for y in range(height):
                    if count == len(content):
                        print("reached end of data bits")
                        break
                    

                    curr_bit = content[count]
                    if curr_bit == '0':
                        image.putpixel((x, y), zero)
                    if curr_bit == '1':
                    
                        image.putpixel((x, y), one)
                    self.end_x=x
                    self.end_y=y
                    count+=1

            #image.save(f'data/encoded{frame}.png')
            image.save(os.path.join(png_folder,f"frame{frame}.png"))
                
        #check where the bits end
        if self.end_y < height:
            self.end_y+=1
        else:
            self.end_x+=1
            self.end_y=0
        
        #put the red pixel after the last bit encoded to indicate the end bit
        image.putpixel((self.end_x, self.end_y), red)
        #image.save(f'data/encoded{last_frame}.png')
        image.save(os.path.join(png_folder,f"frame{last_frame}.png"))
        
        
        ####below this line is the ffmpeg encoder stuff


        #image = Image.new
        input_pattern = os.path.join(png_folder,"frame%d.png")
        output_video = self.fileout
        (
        ffmpeg
        .input(input_pattern,framerate = self.fps)
        .output(output_video, vcodec='huffyuv', pix_fmt='rgb24')
        .overwrite_output()
        .run(cmd=ffmpeg_path)
        )
        print(f"done encoding to video :{self.fileout}")
    
    @property
    def end_pixels(self):
        return (self.end_x,self.end_y) #convert this to json ?

    @property
    def metadata(self):
        """
        need to add metadata to the video itself
        such as the x and y coordinates of the end pixel of the raw bits
        add the original file name with extension to save when decoding
        hash of the file to verify the integrity? prolly will not be required
        
        """
        pass

# the Decoder class below
#
class Decoder:
    
    def __init__(self,filename):
        self.filename=filename
        self.ripped_bytes =[]
    
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

        for frame in range(no_of_frames):
            x,y = 0,0
            image = Image.open(f"out/frame_{frame}.png")
            width, height = image.size
            pixels = image.load()
            print(f"decoding frame:{frame}")

            #pixels = image.getdata() # experiment with this once (see pillow docs)
            #print(image.size)
            for x in range(width):
                for y in range(height):

                    pix = pixels[(x,y)]
                    if tuple(pix) == red:
                        print(f"reached end of file at:x:{x},y:{y}")
                        #print(pix,end="")
                        #binary_bytes=[int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
                        for i in range(0,len(bits),8):
                            curr_bit = int(bits[i:i+8],2)
                            binary_bytes.append(curr_bit) # type: ignore
                        binary_bytes = bytes(binary_bytes)
                        with open("big_out.pdf", "wb") as file:
                            file.write(binary_bytes)


                    else:
                        if pix == one:
                            bits+='1'
                        elif pix==zero:
                            bits+='0'
                        #print(pix,end="")
        
        
    
    

if __name__ == '__main__':
    # enc1= Encoder("bigc.pdf")
    # print(enc1.size)
    # print(enc1.filename)
    # print(enc1.fileout)
    # print(enc1.fps)
    # #print(enc1.ripped_bytes)
    # enc1.encode()
    # print(f"end pixels are{enc1.end_pixels}")
    dec1 = Decoder("bigc_pdf_.avi")
    print(eval(dec1.metadata["streams"][0]["r_frame_rate"]))
    print(dec1.fileout)
