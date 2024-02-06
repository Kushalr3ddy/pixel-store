from PIL import Image
import os


out = "out"


#image = Image.open("data/encoded302.png")
image = Image.open(os.path.join(out,"frame_24.png"))
#x,y=60,176
x,y=590,174


pixels = image.load()
avg=0
for i in range(2):

    for j in range(2):
        red = pixels[(x+j,y+i)]
        avg+=sum(red)/3
        print(avg)

avg/=4
print(avg)
avg=int(avg)
print(avg)