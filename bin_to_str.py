binstr_og= "0111101100100111011100000110100101111000011001010110110001011111011100110110100101111010011001010010011100111010001000000011010000101100001000000010011101100101011011100110010001011111011110000010011100111010001000000011000000101100001000000010011101100101011011100110010001011111011110010010011100111010001000000011000000101100001000000010011101100110011010010110110001100101011011100110000101101101011001010010011100111010001000000010011101100010011010010110011101100011001011100111000001100100011001100010011100101100001000000010011101100011011010000110010101100011011010110111001101110101011011010010011100111010001000000010011100110101001101010011011001100101001101100110001001100101011001010011010100110110001100010110001000110111001101110011011001100011001110010011010101100011001101100011100000110111001100100110001100110100001101000011000101100010011000010110000101100100001100010010011101111101"


binstr_extracted = "0111101100100111011100000110100101111000011001010110110001011111011100110110100101111010011001010010011100111010001000000011010000101100001000000010011101100101011011100110010001011111011110000010011100111010001000000011000000101100001000000010011101100101011011100110010001011111011110010010011100111010001000000011000000101100001000000010011101100110011010010110110001100101011011100110000101101101011001010010011100111010001000000010011101100010011010010110011101100011001011100111000001100100011001100010011101111101"

binstr = binstr_og

for i in range(0,len(binstr),8):
    curr_bit = binstr[i:i+8]
    bin_bit = int(curr_bit,2)
    print(chr(bin_bit),end="")