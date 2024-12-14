from pixelstore.resolutions import Resolutions
from pixelstore.color import Colors

from PIL import Image
import os
import json
import math
import cv2
from functools import lru_cache

OUTPUT_FOLDER = "decoded_files"
EXTRACTION_FOLDER = "extracted_frames"
PIXEL_SIZE = 4 # keep this as 4 itself

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
        cv2.destroyAllWindows() # type: ignore
    
    # function for extracting data from the frame
    def extract_data_from_frame(self,frame:Image,end_x = None,end_y = None, final_frame:bool=False)->str:
        
        pixels = frame.load() # this will return a list of tuples with rgb values
        width, height = frame.size
        # since each pixel is 2x2 pixels wide i.e 4 pixels take sqrt of 4
        #KEEP THIS CONST FOR ALL INSTANCES OF DECODER CLASS ELSE PAIN
        pix_len = int(math.sqrt(PIXEL_SIZE))
        
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
            
        binary_bytes = []
        metadata = json.loads(metadata)
        filename = metadata["filename"]
        for i in range(0,len(raw_bits),8):
            byte = int(raw_bits[i:i+8],2) # type: ignore
            binary_bytes.append(byte)
        binary_bytes = bytes(binary_bytes)
        filename = os.path.join(OUTPUT_FOLDER,filename)
        with open(filename, "wb") as file:
            file.write(binary_bytes)
            print("done writing file")
            
        
        
    # function to decode data extracted from all the frames
    
    def decode_data(self):
        m_data_bits =""
        file_bits = ""
        metadata_frame_path = os.path.join(self.extraction_folder,"frame0.png")
        if not os.path.exists(metadata_frame_path):
            print("metadata frame not found.exiting....")
            exit()
        
        no_of_frames = len(os.listdir(self.extraction_folder))
        
        if no_of_frames < 2:
            print("only one frame found.\nexiting...")
        
        #extract the metadata frame i.e frame0.png
        m_data_bits = self.extract_data_from_frame(Image.open(metadata_frame_path))
        print(self.conv_metadata(m_data_bits))
        # extract the rest of the frame
        for frame in range(1,no_of_frames-1):
            
            current_image = Image.open(os.path.join(self.extraction_folder,f"frame{frame}.png"))
            file_bits += self.extract_data_from_frame(current_image)
        
        mdata =self.conv_metadata(m_data_bits)
        
        # final frame data extraction
        metadata = json.loads(mdata)
        
        end_x = metadata['end_x']
        end_y = metadata['end_y']
        file_bits += self.extract_data_from_frame(frame=no_of_frames-1,
                                                  end_x= end_x
                                                  ,end_y= end_y)
        
        self.generate_file(file_bits, mdata)
