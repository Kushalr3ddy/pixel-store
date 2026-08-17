from pixelstore.encoder import Encoder
#from pixelstore.decoder import Decoder
from pixelstore.decodr import Decoder

import os
import json

filename = "bigc.pdf"
def encode(filename:str) ->None:
    enc1 = Encoder(filename)
    enc1.encode()

#encode(filename)
    
def decode(video_file):
    dec1 = Decoder(video_file)
    dec1.decode_data()
    
#encode("./bigc.pdf")
decode("output/bigc.avi")