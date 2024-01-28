from PIL import Image


image = Image.open("data/encoded303.png")

pixels = image.load()

red = pixels[(60,175)]

print(red)