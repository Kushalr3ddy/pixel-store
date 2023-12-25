from PIL import Image
#import requests

im = Image.open("./color_bars.png")
pdf = open("./dummy.pdf","rb")
pixel_values = list(im.getdata())

#print(pixel_values[0:4])
#print(f"length of pixel array:{len(pixel_values)}")
print(bin(pdf.read()))