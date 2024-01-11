"""
temp metadata ignore

bits_len before padding:106112
bits_len after padding:106128
no of bits padded:16
"""

from PIL import Image

image = Image.open("optimised.png")

pixels =image.load()
width,height =image.size
count =0
file_bits = 106112
padding = 16


curr_pixel = pixels[(width-1,height-1)]
for i in range(3):
    curr_pixel = pixels[(0,0)][i]
    curr_pixel=bin(curr_pixel)[2:]
    print(curr_pixel.zfill(8))
    #bin(pixels[(0,0)][i])[2:].zfill(8) # one liner check once might throw error

#exit(0)
print("decoding section")
raw_bytes =[]
binary_bytes=[]
for x in range(width):
    if count ==106128:
        break
    for y in range(height):

        #if count == 106127:
        #    curr_pixel = pixels
        if count ==106128:
            break
        curr_pixel = pixels[(x,y)] # get the r,g,b tuple
        #str(bin(curr_pixel[i])[2:].zfill(8))
        r = int(bin(curr_pixel[0])[2:].zfill(8),2)
        g = int(bin(curr_pixel[1])[2:].zfill(8),2)
        b = int(bin(curr_pixel[2])[2:].zfill(8),2)
        #curr_byte = r+g+b
        
        raw_bytes.append(r)
        raw_bytes.append(g)
        raw_bytes.append(b)


        count+=24

print(len(raw_bytes))
print(len(raw_bytes[:-16]))
binary_bytes = bytes(raw_bytes[:-16])
with open("optimised_out.pdf", "wb") as file:
    file.write(binary_bytes)
