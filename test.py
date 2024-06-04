from pixelstore.encoder import Encoder
from pixelstore.decoder import Decoder

import os
enc1 = Encoder(filename="bigc.pdf")
#enc1= Encoder(filename="payload.png")
print(enc1.metadata)
enc1.encode()
filename = os.path.join("output","bigc.avi")
#dec1=Decoder(filename=filename)
#dec1.extract_frames()
#print(dec1.metadata)


