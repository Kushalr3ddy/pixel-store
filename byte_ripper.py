import os


with open("bigc.pdf","rb") as source:
    byte_ptr = source.read(1)
    while(byte_ptr):
        print(int(byte_ptr,2))

        byte_ptr = source.read(1)
        