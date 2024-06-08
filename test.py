from pixelstore.encoder import Encoder
from pixelstore.decoder import Decoder

import os
#enc1 = Encoder(filename="bigc.pdf")
enc1= Encoder(filename="bigc.pdf",frame_folder="data")
print(f"og_metadata:{len(enc1.metadata)}")
print(enc1.metadata)
#enc1.create_video()
#enc1.encode()
filename = os.path.join("output","bigc.avi")
dec1=Decoder(filename=filename)
#dec1.extract_frames()
print(f"decoded_metadata:{len(dec1.metadata)}")
print(dec1.metadata)




