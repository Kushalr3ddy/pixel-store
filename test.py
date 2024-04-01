from PIL import Image
import os

image = Image.open(os.path.join("data","frame0.png"))
pixels = image.load()
width, height = image.size

pixel_arry=[]
for x in range(0,width,2):
    for y in range(0,height,2):
        #print(pixels[(x,y)])
        if pixels[(x,y)] == (255,0,0):
            
            print(f"red found at :{x},{y}")