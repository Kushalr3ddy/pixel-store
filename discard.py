from PIL import Image


image = Image.open("test.png")

pixels = image.load()

for x in range(640):
    for y in range(480):
        print(pixels[x,y])


