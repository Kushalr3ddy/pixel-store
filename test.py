no_of_frames = 1
width, height = 640,480 # test with 480p for now later add other resolutions
total_pixels = width * height
x,y = 0,0
count = 0
last_frame =0

# this is for storing all the images (frames) that are created as a result of converting bits to pixels
png_folder ="frames"

# create the folder if it doesnt exist
if not os.path.exists(png_folder):
    os.mkdir(png_folder)

content=''.join(self.ripped_bytes)#.replace('\n','')
image = Image.new('RGB', (width, height), color='white')

#determine the no of frames 
if len(content) > total_pixels:
    no_of_frames = int((len(content)/total_pixels)+1)

#print(f"no of frames required:{no_of_frames}")
for frame in range(no_of_frames):
    last_frame=frame
    #create a blank white image and overwrite the pixel values
    image = Image.new('RGB', (width, height), color='white')
    
    # this works and prints only 75 frames cause the frame value starts from 0 ;so 0 to 75 total 76 frames
    if count == len(content):
            print("reached end of data bits")
            break
        
    print(f"encoding frame :{frame}" )
    for x in range(width):
        if count == len(content):
                print("reached end of data bits")
                break
            
        for y in range(height):
            if count == len(content):
                print("reached end of data bits")
                break
            

            curr_bit = content[count]
            if curr_bit == '0':
                image.putpixel((x, y), zero)
            if curr_bit == '1':
            
                image.putpixel((x, y), one)
            self.end_x=x
            self.end_y=y
            count+=1

    #image.save(f'data/encoded{frame}.png')
    image.save(os.path.join(png_folder,f"frame{frame}.png"))