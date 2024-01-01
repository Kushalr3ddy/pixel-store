from PIL import Image

# Define image resolution
width, height = 640, 480


# create a new image with a white background
image = Image.new('RGB', (width, height), color='white')

width, height = image.size
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
print(len(content))
end_x=0
end_y=0
for x in range(width):

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
    


image.putpixel((end_x+1, end_y+1), red_color)
print()
#a red pixel is put to indicate the end of data
print(f"last pixels are x:{end_x},y:{end_y}")
print(f"no of pixels written:{count}")
        

        

#image.putpixel((x+1, y), blue_color)

#create the image
image.save('encoded.png')