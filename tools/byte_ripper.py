import os


with open("bigc.pdf","rb") as source:
    byte_ptr = source.read(1)
    while(byte_ptr):
        print(format(ord(byte_ptr),"08b"))

        byte_ptr = source.read(1)
        