from PIL import Image
#import requests

#im = Image.open("./color_bars.png")
pdf = open("./bigc.pdf","rb")
#pixel_values = list(im.getdata())

#print(pixel_values[0:4])
#print(f"length of pixel array:{len(pixel_values)}")
raw_bytes =pdf.read(1)
bit_sequence = []
padded_bytes=[]
count =0
while raw_bytes:
    curr_byte = bin(int.from_bytes(raw_bytes,byteorder="big"))
    curr_byte = curr_byte[2:]
    if len(curr_byte) < 8:
        # fill up the lsb so if a byte is 1010 it will become 00001010
        # this is done so it becomes 8 bits ie one whole byte for easy parsing later on
        curr_byte = curr_byte.zfill(8)
        padded_bytes.append(count)
    print((curr_byte))#,end=" ")
    raw_bytes = pdf.read(1)
    bit_sequence.append(curr_byte)
    count+=1


#print(f"\n{'-'*10}{count}:{len(bit_sequence)}{'-'*10}")
#print("\npadded bytes indexes:")

