from PIL import Image


image = Image.open("encoded.png")

white =(0,0,0)
black =(255,255,255)
red_color =(255,0,0)

#define custom exception for reaching end of file
class endoffile(Exception):    
    pass


pixels = image.load()
#pixels = image.getdata() 
width, height = image.size
#print(image.size)

all_pixels = []
bits_to_decode =[]
bits = ""

x,y = 0,0

def get_file(pixels):
    bits=""
    for x in range(width):
        for y in range(height):
            pix = pixels[(x,y)]
            if tuple(pix) == red_color:
                #print(f"reached end of file at:x:{x},y:{y}")
                #print(pix,end="")
                binary_bytes=[int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
                binary_bytes = bytes(binary_bytes)
                with open("reconstructed_file.pdf", "wb") as file:
                    file.write(binary_bytes)
                return bits
                
            else:
                if pix == white:
                    bits+='1'
                elif pix==black:
                    bits+='0'
                #print(pix,end="")



if __name__ =='__main__':
    get_file(pixels)