from pixelstore.encoder import Encoder


#enc1 = Encoder(filename="bigc.pdf")
enc1= Encoder(filename="payload.png")
print(enc1.metadata)
enc1.encode()

#dec1=Decoder(filename="bigc.avi")
#dec1.extract_frames()
#print(dec1.metadata)



