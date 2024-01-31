from PIL import Image
import os

# Define image resolution
width, height = 640, 480


# create a new image with a white background
image = Image.new('RGB', (width, height), color='white')

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
    no_of_frames = int((len(content)*4/total_pixels))

print(f"no of frames required:{no_of_frames}")
#exit(0)
pix_count=0
frame=0
for bit in bit_sequence:
    if pix_count == total_pixels:
        image.save(os.path.join("data",f"encoded{frame}.png"))
        frame+=1
        
    for curr_bit in bit:
        if y>=height:
            x+=1
            y=0
        pixel_color = one if curr_bit == 1 else zero
    
        for i in range(2):
            for j in range(2):
                image.putpixel((x+j, y+i), pixel_color)

        pix_count+=4
        y+=1
    end_x=x
    end_y=y


print(f"frame:{frame},x:{x},y:{y}")
    
if end_y < height:
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