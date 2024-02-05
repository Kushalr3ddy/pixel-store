from PIL import Image


image = Image.open("data/encoded302.png")

pixels = image.load()

red = pixels[(62,178)]

print(red)