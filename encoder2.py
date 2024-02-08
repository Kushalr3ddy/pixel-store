from PIL import Image
import os

import ffmpeg
# Define image resolution
width, height = 640, 480


# create a new image with a white background
#image = Image.new('RGB', (width, height), color='white')
image = Image.new('RGB', (width, height), color='black')

width, height = image.size
#x,y coordinates
#x, y = 100, 200

# initially no of frames is 1 if the no of bits < no of pixels
no_of_frames=1

#defining the pixels to represent colors 
red_color =(255,0,0)
blue_color = (0, 0, 255)  
one=(0,0,0)
zero = (255,255,255)

#file = open("padded_bytes.txt","r")
#read the file containing raw bit data as strings and remove the newline characters
file = open("bigc.pdf","rb")

if not os.path.exists("data"):
    os.mkdir("data")    

png_folder ="data"


#starting pixels
x,y = 0,0
count =0
total_pixels = 640*480
#total_bits = len(content)

# 640x480 width x height



        
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
    

content=''.join(bit_sequence)#.replace('\n','')
print(len(content))
#exit(0)

# to determine the end pixel
end_x=0
end_y=0
#exit(0)
if len(content) > total_pixels:
    no_of_frames = int((len(content)*4/total_pixels))+1

print(f"no of frames required:{no_of_frames}")
#exit(0)

count=0
end_x=0
end_y=0
for frame in range(no_of_frames):
    if count == len(content):
        break
    print(f"encoding frame:{frame}")
    #image = Image.new("RGB",(width,height),color="white")
    image = Image.new("RGB",(width,height),color="black")
    for x in range(0,width,2):
        if count == len(content):
            break
        for y in range(0,height,2):
            if count == len(content):
                break
            
            curr_bit = content[count]
            pix_color = one if curr_bit =='1' else zero
            """
            for i in range(2):
                for j in range(2):
                    image.putpixel((x+j,y+i),pix_color)
            """
            image.putpixel((x,y),pix_color)
            image.putpixel((x+1,y),pix_color)
            image.putpixel((x,y+1),pix_color)
            image.putpixel((x+1,y+1),pix_color)

            count+=1
            end_x=x
            end_y=y


    image.save(os.path.join(png_folder,f"encoded{frame}.png"))
#print(f"x:{x} y:{y}")
#exit(0)
#end_x=x
#end_y=y

#print(f"end frame:{frame}\nend pixels are x:{end_x}y:{end_y}")
#exit(0)
print(f"frame:{frame},x:{x},y:{y}")
    
if end_y+2 < height:
    end_y+=2
else:
    end_x+=1
    end_y=0


image.putpixel((end_x, end_y), red_color)
image.putpixel((end_x+1, end_y), red_color)
image.putpixel((end_x, end_y+1), red_color)
image.putpixel((end_x+1, end_y+1), red_color)

image.save(os.path.join("data",f"encoded{frame}.png"))
print()
#a red pixel is put to indicate the end of data
print(f"last pixels are x:{end_x},y:{end_y}")
print(f"no of pixels written:{count}")
        

        

#image.putpixel((x+1, y), blue_color)

#create the image
#image.save('encoded.png')
input_pattern = os.path.join(png_folder ,'encoded%d.png')

# Output video file name
output_video = 'output_video.avi'

# Create a video using ffmpeg with Lagarith codec
(
    ffmpeg
    .input(input_pattern, framerate=6)  # Set frame rate
    .output(output_video, vcodec='huffyuv', pix_fmt='rgb24',bitrate ="3000k")  # Lagarith codec with RGB24 pixel format
    .run(cmd=ffmpeg_path)
)

