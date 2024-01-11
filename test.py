from PIL import Image

width, height = 640, 480


# Create a new image with a white background
image = Image.new('RGB', (width, height), color='white')
x,y=0,0

blue_color =(0,0,255)
red_color =(255,0,0)

image.putpixel((x, y), blue_color)
image.putpixel((1, 0), red_color)
image.save('test.png')