import os
from PIL import Image



mdataFramePath = os.path.join(self.extraction_folder,"frame0.png")
if not os.path.exists(mdataFramePath):
    print("metadata frame not found i.e frame0.png not found")
    print(f"extracting frames from {self.filename}")
    self.extract_frames()
print(f"metadata frame found at: {self.extraction_folder}/")

im = Image.open(os.path.join(self.extraction_folder,"frame0.png"))
width,height =im.size
pixels = im.load()
mdata_bits=[]
binary_bytes=[]
check=1
for x in range(0,width,2):
    if not check:
        break
    for y in range(0,height,2):
        if not check:
            break
        r_avg=0
        g_avg=0
        b_avg=0
        
        
        pix=0
        for i in range(2):
            for j in range(2):
                r,g,b = pixels[(x+j,y+i)]
                r_avg +=r
                g_avg+=g
                b_avg+=b
                
                
                #curr_pix = pixels[(x+j,y+i)] # check the bit checker below if you want to change this
                #pix += sum(curr_pix)/3
        r_avg/=4
        g_avg/=4
        b_avg/=4
        
        #pix/=4
        #pix = int(pix)
        
        #pix = pixels[(x,y)]
        
        #print(pix,end = ", ")
        #if pix == Colors.red:# or int(sum(pix)/3) == 108:
        #if pix == 108:
        #if pix[0] > pix[1] and pix[0] > pix[2]:
        if r_avg > 150 and g_avg < 100 and b_avg < 100:
            print(f"found red pixel at x:{x} y:{y}")
            try:
                mdata = str(mdata_bits)
                for i in range(0,len(mdata_bits),8):
                    byte = int(mdata[i:i+8],2) # type: ignore
                    binary_bytes.append(byte) # type: ignore
                binary_bytes = bytes(binary_bytes)
                #return mdata
                print(str(binary_bytes))
            
            
            
            except Exception as e:
                print(mdata)
                raise(e)# ye ik this stupid af
                print("something wrong with the metadata extraction:")
                print(e)
        else:
            curr_bit = "1" if pix == Colors.one else "0"
            mdata_bits.append(curr_bit)
