import cv2
import os

images = os.listdir("data/")


#for i in len(images):
#    pass

no_of_frames = len(images)

fps =1


first_image = cv2.imread("data/encoded0.png")
height, width, channels = first_image.shape # ignore the channels for now; will become use full when using RGBA mode (four channels)
#exit(0)


image_folder = 'data'
video_name = 'video.avi'
frames =[]

for i in range(no_of_frames+1):
    frames.append(f"encoded{i}.png")

frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

#video = cv2.VideoWriter(video_name, 0, 1, (width,height))

fourcc = cv2.VideoWriter_fourcc(*'FFV1')
#fourcc = cv2.VideoWriter_fourcc(*'X264')
video = cv2.VideoWriter(video_name, fourcc, 1, (width, height))

for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

cv2.destroyAllWindows()
video.release()
