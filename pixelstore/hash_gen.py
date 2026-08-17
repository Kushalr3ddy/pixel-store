import hashlib


def get_md5(filename:str):
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)

    return(file_hash.hexdigest())

def get_sha1(filename:str):
    with open(filename, "rb") as f:
        file_hash = hashlib.sha1()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)

    return(file_hash.hexdigest())
