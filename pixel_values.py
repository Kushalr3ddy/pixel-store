from PIL import Image
import os


from pixelstore import Colors

image =os.path.join("frames","frame0.png")# this is after encoding (no compression)
#image =os.path.join("frames","frame0.png")# this is after frame extraction(after compression)
print(os.path.exists(image))
frame =  Image.open(image)
width, height = frame.size
pixels = frame.load()



def avg(l:list)->float:
    return sum(l)/len(l)

bit_string=''

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

        r_avg = avg(r_list)
        g_avg = avg(g_list)
        b_avg = avg(b_list)
        
        cur_pix = (r_avg,g_avg,b_avg)
        
        if r_avg > 150 and g_avg < 100 and b_avg < 100:
            print(f"found red pixel at x:{x} y:{y}")
            #exit()
        else:
            #bit_string+=("1" if cur_pix == Colors.one else "0")
            bit_string+=("0" if cur_pix == Colors.one else "1")
        #print(pixels[(i,j)][0])
        
#print(bit_string)

for i in range(0,len(bit_string),8):
    #char_ptr = bit_string[i:i+8]
    #print(char_ptr,end="")
    
    char_ptr = int(bit_string[i:i+8],2)
    print(chr(char_ptr),end=' ')
    