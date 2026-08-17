from pixelstore.resolutions import Resolutions
from pixelstore.color import Colors

from PIL import Image
import os
import json
import math
import hashlib
import cv2
from functools import lru_cache

OUTPUT_FOLDER = "decoded_files"
EXTRACTION_FOLDER = "extracted_frames"
PIXEL_SIZE = 4 # only a fallback now for old videos that dont have pix_size in their metadata, real cell size comes from the metadata frame
METADATA_CELL = 8 # HAS to be the same as Encoder.METADATA_CELL or the metadata frame reads as garbage

# instantiate Decoder with video filename
# extract all frames +done
# get the resolution and fps
# decode the first frame and the metadata
# get the end_x end_y pixel
# decode till last frame,last pixel and store all the raw bits
# dump the raw bits into a file
# save the file into output/filename from metadata
# (optional) compare the file hashes to check file integrity
class Decoder:
    # the reason why im not using the variables OUTPUT_FOLDER directly like
    # self.output_folder = OUTPUT_FOLDER is cause it will get rewritten to the same OUTPUT_FOLDER thing for every object created even if custom value is spcified
    def __init__(self,video_file:str,output_folder:str = OUTPUT_FOLDER,extraction_folder:str = EXTRACTION_FOLDER):
        self.video_file = video_file
        self.output_folder = output_folder
        self.extraction_folder = extraction_folder
        self.extract_frames(self.video_file)

    
    # function for extracting the frames from the video and saving it to self.extraction_folder
    def extract_frames(self,video_file:str):

        if not os.path.exists(self.video_file):
            print(f"video file {self.video_file} not found. exiting....")
            exit()
            
        if not os.path.exists(self.extraction_folder):
            os.mkdir(self.extraction_folder)
        
        video_file_reader = cv2.VideoCapture(self.video_file)
        
        # frame counter
        # remove this later ig?
        frame_no_count = 0
        
        while(True):
            ret,frame = video_file_reader.read()
            if ret:
                # if video is still left continue creating images
                
                print(f"extracting frame:{frame_no_count}",end="\r")

                cv2.imwrite(os.path.join(self.extraction_folder,f"frame{frame_no_count}.png"), frame) # type: ignore
                frame_no_count += 1
            else:
                print(f"done extracting {frame_no_count} frames")
                break
        video_file_reader.release()

    # function for extracting data from the frame
    # cell_px = how many pixels wide one bit is, gotta be the exact same value the encoder used or every bit lands in the wrong place
    def extract_data_from_frame(self,frame:Image,cell_px:int=None,end_x = None,end_y = None, final_frame:bool=False)->str:

        pixels = frame.load() # this will return a list of tuples with rgb values
        width, height = frame.size
        # pix_len = the cell side in pixels. data frames hand this in from the metadata, if nobody passes it fall back to the old hardcoded value
        pix_len = cell_px if cell_px is not None else int(math.sqrt(PIXEL_SIZE))

        frame_bits =""
        
        for x in range(0,width,pix_len):
                #if (y == end_y or x == end_x) and final_frame:
                #    break
                for y in range(0,height,pix_len):
                    if (y == end_y or x == end_x) and final_frame:
                        break
                    r_list =[]
                    g_list=[]
                    b_list=[]
                    
                    
                    for i in range(pix_len):
                        for j in range(pix_len):
                            # will return r,g,b as a list
                            curr_pix = pixels[(x+j,y+i)] # check the bit checker below if you want to change this
                            r_list.append(curr_pix[0])
                            g_list.append(curr_pix[1])
                            b_list.append(curr_pix[2])
                    
                    r_avg=sum(r_list)/len(r_list)
                    g_avg=sum(g_list)/len(g_list)
                    b_avg=sum(b_list)/len(b_list)

                    pix = ( r_avg,g_avg,b_avg)
                    if sum(pix)/3 > 128:
                        frame_bits += "0" 
                    else:
                        frame_bits += "1"
                    
                
        return frame_bits      
                    
    #@lru_cache # test this caching function later on
    def conv_metadata(self,str_mdata:str) -> str: 
        m_data_bits =[] # inefficient but helps to check the bytes that are decoded
        if len(str_mdata) % 8 !=0:
            print("not enough bits in raw metadata")
            exit()
            
        for i in range(0,len(str_mdata),8):
            curr_byte = int(str_mdata[i:i+8],2)
            m_data_bits.append(curr_byte)
        
        #metadata_ = ''.join(map(chr,m_data_bits))    
        metadata_ = ""
        for i in m_data_bits:
            try:
                
                if chr(i) == '}':
                    metadata_ += chr(i)
                    break
                else:
                    metadata_ += chr(i)
            except Exception as e:
                print(e)
                
        return metadata_
            
        
    # function to generate the file from the data extracted
    def generate_file(self,raw_bits:str,metadata:str):
        
        if not os.path.exists(OUTPUT_FOLDER):
            os.mkdir(OUTPUT_FOLDER)
            
        binary_bytes = [] # the raw bytes we rebuild from the bit string
        metadata = json.loads(metadata) # metadata comes in as a json string, load it back into a dict
        filename = metadata["filename"] # what to name the output file, taken from the metadata
        # walk the bits 8 at a time and turn each chunk back into one byte
        for i in range(0,len(raw_bits),8):
            byte = int(raw_bits[i:i+8],2) # type: ignore
            binary_bytes.append(byte)
        binary_bytes = bytes(binary_bytes) # list of ints -> actual bytes object so we can dump it to disk
        filename = os.path.join(OUTPUT_FOLDER,filename)
        with open(filename, "wb") as file:
            file.write(binary_bytes)
            print("done writing file")

        # expected = the md5 the encoder stored in the metadata frame. compare it against what we actually rebuilt to know if the decode came out clean
        expected = metadata.get("checksum")
        if expected is not None:
            actual = hashlib.md5(binary_bytes).hexdigest() # md5 of the file we just wrote
            if actual == expected:
                print(f"checksum OK ({actual})")
            else:
                # if these dont match some bits flipped somewhere (usually lossy compression eating the cells)
                print(f"checksum MISMATCH expected {expected} got {actual}")
            
        
        
    # function to decode data extracted from all the frames

    def decode_data(self):
        file_bits = "" # all the data bits from every frame get piled up here
        metadata_frame_path = os.path.join(self.extraction_folder,"frame0.png") # frame0 is always the metadata frame
        if not os.path.exists(metadata_frame_path):
            print("metadata frame not found.exiting....")
            exit()

        no_of_frames = len(os.listdir(self.extraction_folder)) # how many frames got extracted, counts frame0 too

        if no_of_frames < 2:
            print("only one frame found.\nexiting...")

        # read frame0 at the fat METADATA_CELL size, has to be the fixed size cause we dont know the data pix_size yet
        m_data_bits = self.extract_data_from_frame(Image.open(metadata_frame_path), cell_px=METADATA_CELL)
        mdata = self.conv_metadata(m_data_bits) # turn those bits into the metadata string
        metadata = json.loads(mdata) # and load it into a dict
        print(f"metadata: {metadata}")

        # data_cell = pixels per side for the DATA frames, pulled from metadata. sqrt cause pix_size is the pixel count (16 -> 4x4). old videos with no pix_size fall back to PIXEL_SIZE
        data_cell = int(math.sqrt(metadata.get("pix_size", PIXEL_SIZE)))

        # now read every actual data frame (frame1 to the last one) at the data cell size and glue the bits together
        for frame in range(1, no_of_frames):
            current_image = Image.open(os.path.join(self.extraction_folder,f"frame{frame}.png"))
            file_bits += self.extract_data_from_frame(current_image, cell_px=data_cell)

        # nbits = the real bit count from metadata. the last frame is padded with white so chop the bitstream back down to this or youll get extra junk bytes at the end
        nbits = metadata.get("nbits")
        if nbits is not None:
            file_bits = file_bits[:nbits]

        self.generate_file(file_bits, mdata)
