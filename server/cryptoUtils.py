# cryptography.py
# This file contains all functions that handle file encryption and decryption

from Crypto.Cipher import AES
import os, struct
from Crypto import Random

# Functions to apply padding and unpadding
pad = lambda s: s + ((AES.block_size-len(s) % AES.block_size) * '{')

def encrypt(key, message):
    cipher = AES.new(key)
    return cipher.encrypt(message)

def decrypt(key, message):
    cipher = AES.new(key)
    return cipher.decrypt(message)

def genFileKey(player_key, device_key, user_key, iv):
    # generate file key
    dev_enc = encrypt(device_key, iv)
    user_enc = encrypt(user_key, dev_enc)
    file_key = encrypt(player_key, user_enc)

    return file_key

# encrypts a file and writes the result to file_out
# based on code from http://stackoverflow.com/questions/16761458/how-to-aes-encrypt-decrypt-files-using-python-pycrypto-in-an-openssl-compatible
def encrypt_file(key, file_in, file_out):
    # create cipher
    iv = Random.new().read(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # encrypt file
    chunksize=64*1024
    filesize = os.path.getsize(file_in)

    with open(file_in, 'rb') as infile:
        with open(file_out, 'wb') as outfile:

            # <Q = unsigned long long little endian
            # source: https://docs.python.org/3.0/library/struct.html
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(cipher.encrypt(chunk))
