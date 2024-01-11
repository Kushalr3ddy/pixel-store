from PIL import Image

# Define image resolution
width, height = 640, 480


# create a new image with a white background
image = Image.new('RGB', (width, height), color='white')

#width, height = image.size
#x,y coordinates
#x, y = 100, 200



#defining the pixels to represent colors 
red_color =(255,0,0)
blue_color = (0, 0, 255)  
one=(0,0,0)
zero = (255,255,255)

file = open("padded_bytes.txt","r")



#starting pixels
x,y = 0,0
count =0
total_pixels = 640*480
#total_bits = len(content)

# 640x480 width x height


#read the file containing raw bit data as strings and remove the newline characters
content=file.read().replace('\n','')
bits_length = len(content)
print(bits_length/24)



#image.putpixel((end_x+1, end_y+1), red_color)
print()
#a red pixel is put to indicate the end of data
#print(f"last pixels are x:{end_x},y:{end_y}")
print(f"no of pixels written:{count}")

no_of_padding=0
if bits_length%24 !=0:
    quotient = bits_length // 24
    while (quotient*24) < bits_length:
        quotient +=1
        no_of_padding = (quotient*24)-bits_length


print(f"no of bits padded:{no_of_padding}")
print(f"bits_len before padding:{bits_length}")

padded_content = content+('0' * no_of_padding)

print(f"bits_len after padding:{len(padded_content)}")

print(f"padded content condition :{len(padded_content)%24}")
byte_array = []

for i in range(0, len(padded_content), 24):
    curr_chunk=padded_content[i:i+24]
    byte_array.append(curr_chunk)

print(len(byte_array))
print(byte_array[0])
#exit(0)
count =0

for x in range(width):#width
    if count ==len(byte_array):
        break
    for y in range(height):#height (cause it goes from top to bottom column wise)
        if count ==len(byte_array):
            break
        chunk = byte_array[count]
        #print(f"getting value x:{x} y:{y}")
        r = int(chunk[:8],2)
        g = int(chunk[8:16],2)
        b = int(chunk[16:24],2)
        
        image.putpixel((x, y), (r,g,b))
        count+=1

#image.putpixel((x+1, y), blue_color)

#create the image
image.save('optimised.png')
