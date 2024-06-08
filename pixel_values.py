from PIL import Image
import os

from pixelstore import Colors

image =os.path.join("data","frame0.png")
print(os.path.exists(image))
frame =  Image.open(image)
width, height = frame.size
pixels = frame.load()



def avg(l:list)->float:
    return sum(l)/len(l)


for x in range(0,width,2):
    for y in range(0,height,2):
        
        r_list =[]
        g_list=[]
        b_list=[]
        
        for i in range(2):
            for j in range(2):
                r,g,b = pixels[(x+j,y+i)]
                
                r_list.append(r)
                g_list.append(g)
                b_list.append(b)

        print(avg(r_list),end=" ")
        print(avg(g_list),end=" ")
        print(avg(b_list))

        #print(pixels[(i,j)][0])