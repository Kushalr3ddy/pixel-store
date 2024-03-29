from PIL import Image

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
file = open("big_bits.txt","r")



#starting pixels
x,y = 0,0
count =0
total_pixels = 640*480
#total_bits = len(content)

# 640x480 width x height


#read the file containing raw bit data as strings and remove the newline characters
content=file.read().replace('\n','')

print(len(content))

# to determine the end pixel
end_x=0
end_y=0
#exit(0)

if len(content) > total_pixels:
    no_of_frames = int((len(content)/total_pixels)+1)

print(f"no of frames required:{no_of_frames}")
#exit(0)

for frame in range(no_of_frames):
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
            end_x=x
            end_y=y
            count+=1

    image.save(f'data/encoded{frame}.png')

print(f"frame:{frame},x:{x},y:{y}")
    
if end_y < height:
    end_y+=1
else:
    end_x+=1
    end_y=0

image.putpixel((end_x, end_y), red_color)

image.save(f'data/encoded{frame}.png')
print()
#a red pixel is put to indicate the end of data
print(f"last pixels are x:{end_x},y:{end_y}")
print(f"no of pixels written:{count}")
        

        

#image.putpixel((x+1, y), blue_color)

#create the image
#image.save('encoded.png')