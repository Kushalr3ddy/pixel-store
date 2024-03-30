import cv2


video = cv2.VideoCapture('bigc.avi')

#print(video.get(cv2.CAP_PROP_FPS))
x = video.get(2)
print(x)


