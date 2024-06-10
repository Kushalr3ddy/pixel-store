from pixelstore.encoder import Encoder
from pixelstore.decoder import Decoder

import os
#enc1 = Encoder(filename="bigc.pdf")
#enc1= Encoder(filename="bigc.pdf",frame_folder="data")
#print(f"og_metadata:{len(enc1.metadata)}")
#print(enc1.metadata)
#enc1.create_video()
#enc1.encode()
#exit()
filename = os.path.join("output","bigc.avi")
filename = os.path.join("output","compressed_out.mp4")
filename = os.path.join("output","50_compressed.mp4")
dec1=Decoder(filename=filename)

#dec1.extract_frames()
ext_metadata =dec1.metadata
print(f"length decoded_metadata:{len(ext_metadata)}") # type: ignore
print(type(ext_metadata))
print(ext_metadata)




