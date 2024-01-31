from PIL import Image


image = Image.open("data/encoded265.png")

pixels = image.load()

red = pixels[(212,274)]

print(red)