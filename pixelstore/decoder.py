from pixelstore.resolutions import Resolutions
from pixelstore.color import Colors

from PIL import Image
import os
import json
import math
import cv2
import numpy
import functools

#comment out the imports when pushing code

class Decoder:
    
    def __init__(self,filename,frame_folder="frames",metadata=None):
        self.filename=filename # video file name
        self.ripped_bytes =[] # to store the extracted frames
        self.extraction_folder=frame_folder # the output folder for the frames? the embedded_file
        
        #fileout
        #self.metadata = self.get_metadata() # this instead of @property as the @property keeps calling function
        #self.metadata = metadata # this instead of @property as the @property keeps calling function
        #if not self.metadata:
        #    self.metadata = self.get_metadata()
        #self.metadata = "lmaoaoa"

    # this function replaces the ' with " so the json.loads doesnt shit itself
    def clean_json(self,raw_json:str)->str:
        if raw_json == None:
            print("json is None")
            return
        try:
            raw_json  = raw_json.replace("\'","\"")
            #raw_json = json.loads(raw_json)
            return raw_json
        except Exception as e:
            print("something wrong with json parsing")
            print(e)


    @property
    def fileout(self):
        #video_name = self.filename.split("_")
        #return video_name[0] + "." + video_name[1]
        if self.metadata == None: # more effiecient ig?
            self.metadata = self.get_metadata()

        raw_json  = self.metadata
        raw_json  = self.clean_json(raw_json)
        raw_json = json.loads(raw_json)

        out_filename = raw_json["filename"]
        return out_filename

    @property
    def pixel_size(self)->int:
        
     
        
        #if self.metadata ==None:
        #    self.metadata = self.get_metadata()

        #mdata = self.metadata

        #mdata = json.loads(self.metadata)
        mdata = self.clean_json(self.metadata)
        
        pix_size = json.loads(mdata)
        pix_size = pix_size["pixel_size"]
        #return self.clean_json(mdata)
        return pix_size
        


    #@functools.cached_property
    #def get_metadata(self)->str:
    @property
    def metadata(self)->str:
        mdataFramePath = os.path.join(self.extraction_folder,"frame0.png")
        if not os.path.exists(mdataFramePath):
            print("metadata frame not found i.e frame0.png not found")
            print(f"extracting frames from {self.filename}")
            self.extract_frames()
        #print(f"metadata frame found at: {self.extraction_folder}/frame0.png")
        #print(f"current working directory:{os.getcwd()}")
        im = Image.open(os.path.join(self.extraction_folder,"frame0.png"))
        #width,height =im.size
        #pixels = im.load()
        
        #str_mdata = None
        
        str_mdata = self.get_pixel_values(im,True) # set single frame to true
        try:
            str_mdata = self.get_pixel_values(im,True) # set single frame to true
        
        except Exception as e:
            print(str_mdata)
            #raise(e) # ye ik this stoopid
            print("something wrong with the metadata extraction:")
            print(e)

        return str(str_mdata)
        #return "lmao get rekt"

    




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
        
    
    
            


    def write_file(self):
        pass


    def decode(self):

        self.extract_frames()

        if not os.path.exists("frames"):
            os.mkdir("frames")
        
        no_of_frames = len(os.listdir(self.extraction_folder))
        bits = ""
        binary_bytes=[]
        #pix_size = int(math.sqrt(self.pixel_size)))
        pix_size = 2
        
        #everything below this should be shifted to the get_pixel_values() function later on
        for frame in range(1,no_of_frames):
            #x,y = 0,0 # lmao tf this??
            image = Image.open(os.path.join(self.extraction_folder,f"frame_{frame}.png"))
            width, height = image.size
            pixels = image.load()
            print(f"decoding frame:{frame}")
            output_path = os.path.join(self.fileout)
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
                    #'if pix == 108: #after downloading from youtube pixel color changes
                    if pix == 108 and frame == no_of_frames-1: #after downloading from youtube pixel color changes
                    #if pix == red_color: # geh ass dumb method 

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
    
    #for this function pass frame by frame and then append all the resultant bytes
    def get_pixel_values(self,im:Image,single_frame:False)->str:
        
        """
        this function takes a frames, extracts the bits from it and returns it
        takes 3 variables:
        self
        im:Image(pillow.Image object )
        single_frame: to determine if its a single frame being decoded or a continous stream

        """
        
        width,height =im.size
        pixels = im.load()
        data_bits=[] # empty list for appending bit by bit
        binary_bytes=[] # ignore this
        check=1 # this for getting yeeted out of loop
        #pixel_size = self.pixel_size # this geh shit causing the recursion problem
        pixel_size=4 # for now keep this fixed to 4 pixels
        pixel_size = int(math.sqrt(pixel_size))
        
        for x in range(0,width,2):
            if not check:
                break
            for y in range(0,height,2):
                if not check:
                    break
                
                r_list =[]
                g_list=[]
                b_list=[]

                for i in range(pixel_size):
                    for j in range(pixel_size):
                        r,g,b = pixels[(x+j,y+i)]
                        r_list.append(r)
                        g_list.append(g)
                        b_list.append(b)

                r_avg=sum(r_list)/len(r_list)
                g_avg=sum(g_list)/len(g_list)
                b_avg=sum(b_list)/len(b_list)
                
                pix =(r_avg,g_avg,b_avg)
                #pix/=4
                #pix = int(pix)
                
                #pix = pixels[(x,y)]
                
                #print(pix,end = ", ")
                #if pix == Colors.red:# or int(sum(pix)/3) == 108:
                #if pix == 108:
                #if pix[0] > pix[1] and pix[0] > pix[2]:
                if single_frame and r_avg > 150 and g_avg < 100 and b_avg < 100:
                    print(f"found red pixel at x:{x} y:{y}")
                    try:
                        str_data = ''.join(data_bits)
                        #str_data = data_bits
                        #print(''.join(data_bits))
                        #return str_data
                        #exit()
                        for i in range(0,len(str_data),8):
                            byte = int(str_data[i:i+8],2) # type: ignore
                            binary_bytes.append(chr(byte)) # type: ignore
                        #binary_bytes = bytes(binary_bytes)# dont remove this else it wont do the chr conversion thingy
                        #binary_bytes = binary_bytes # why dis idek forgor
                        #return str_data
                        return str(''.join(binary_bytes))
                    except Exception as e:
                        print("something wrong with reading bytes")
                        print(e)
                    
                    
                    
                else:
                    curr_bit =None
                    #curr_bit = "1" if pix == Colors.one else "0" # this is the line thats supposed to work
                    #curr_bit = "0" if pix == Colors.one else "1" # why is this even working it should be 1 for colors.one but lmao no fuk you no reason
                    if pix <= (80,80,80): # this is just my own approximation need to verify the exact value at which black cannot be distinguised
                        curr_bit = "1"
                    else:
                        curr_bit = "0"
                    try:
                        data_bits.append(curr_bit)
                    except e:
                        print(e)
        # will return the bits in case its not just one frame like in case of metadata frame
        return data_bits
    
    # alternate decoder for frames
    def alt_pix_decoder(self,image:Image,single_frame:bool=True):

        width,height =im.size
        pixels = im.load()
        data_bits=[] # empty list for appending bit by bit
        binary_bytes=[] # ignore this
        check=1 # this for getting yeeted out of loop
        pixel_size = self.pixel_size
        #pixel_size=4
        pixel_size = int(math.sqrt(pixel_size))

        pix_limit = len(self.metadata)

        count =0

        #check = 1

        for x in range(0,width,2):
            if count >= pix_limit:
                break
            for y in range(0,height,2):
                if count >= pix_limit:
                    break
                
                r_list =[]
                g_list=[]
                b_list=[]

                for i in range():
                    for j in range(2):
                        r,g,b = pixels[(x+j,y+i)]
                        r_list.append(r)
                        g_list.append(g)
                        b_list.append(b)

                r_avg=sum(r_list)/len(r_list)
                g_avg=sum(g_list)/len(g_list)
                b_avg=sum(b_list)/len(b_list)
                
                pix =(r_avg,g_avg,b_avg)
                
                if single_frame and r_avg > 150 and g_avg < 100 and b_avg < 100:
                    print(f"found red pixel at x:{x} y:{y}")
                    try:
                        str_data = ''.join(data_bits)
                        #str_data = data_bits
                        #print(''.join(data_bits))
                        #return str_data
                        #exit()
                        for i in range(0,len(str_data),8):
                            byte = int(str_data[i:i+8],2) # type: ignore
                            binary_bytes.append(chr(byte)) # type: ignore
                        #binary_bytes = bytes(binary_bytes)# dont remove this else it wont do the chr conversion thingy
                        #binary_bytes = binary_bytes # why dis idek forgor
                        #return str_data
                        return str(''.join(binary_bytes))
                    except Exception as e:
                        print("something wrong with reading bytes")
                        print(e)
                    
                    
                    
                else:
                    curr_bit =None
                    
                    if pix <= (80,80,80):
                        curr_bit = "1"
                    else:
                        curr_bit = "0"
                    try:
                        data_bits.append(curr_bit)
                    except e:
                        print(e)
        
        