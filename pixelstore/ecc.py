# reed-solomon error correction layer
# the whole point of this file: youtube compression flips some bits, the md5 checksum can only TELL you it broke, it cant fix anything
# reed-solomon lets us actually REPAIR the flipped bits instead of just crying about them
# we bolt this on BEFORE the file bytes get turned into pixels, and peel it back off AFTER we rebuild the bytes on decode

from reedsolo import RSCodec

# DEFAULT_PARITY = how many parity bytes to tack on per 255 byte block
# 32 parity means it can fully repair up to 16 wrong bytes in every 255 byte chunk, thats ~14% bigger file for that safety net
# set parity to 0 anywhere to turn ECC completely off (for lossless transports where you dont need it)
DEFAULT_PARITY = 32


# take the raw file bytes and pad them with parity bytes so the decoder can self heal later
def rs_encode(data: bytes, parity: int = DEFAULT_PARITY) -> bytes:
    if parity <= 0:            # parity 0 = ecc disabled, just hand the bytes straight back
        return data
    # RSCodec chops data into 255 byte blocks on its own and appends `parity` parity bytes to each
    return bytes(RSCodec(parity).encode(data))


# take the (possibly corrupted) bytes we rebuilt from the pixels and use the parity to fix errors + strip the parity back off
def rs_decode(data: bytes, parity: int = DEFAULT_PARITY) -> bytes:
    if parity <= 0:            # nothing to undo if ecc was off
        return data
    # decode() returns a tuple, [0] is the repaired original bytes. this raises if there are too many errors to fix
    return bytes(RSCodec(parity).decode(data)[0])
