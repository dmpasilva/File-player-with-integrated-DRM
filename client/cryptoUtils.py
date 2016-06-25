import hashlib
import struct

import PyKCS11
from Crypto.Cipher import AES
from config import *
import requests
import json
import base64
import pteid

# Encrypt message with key
def encrypt(key, message):
    cipher = AES.new(key)

    c = cipher.encrypt(message)

    return c

# Decrypt message with key
def decrypt(key, message):
    cipher = AES.new(key)
    return cipher.decrypt(message)

# Decrypt a file and return the result
# based on solution from: http://stackoverflow.com/questions/16761458/how-to-aes-encrypt-decrypt-files-using-python-pycrypto-in-an-openssl-compatible
def decrypt_file(key, file_in):
    chunksize=24*1024
    out = ""

    with open(file_in, 'rb') as f:
        original_size = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]
        iv = f.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        while True:
            chunk = f.read(chunksize)
            if len(chunk) == 0:
                break
            out += decryptor.decrypt(chunk)

    return out[:original_size]

def gen_file_key(file_id):
    device_key = get_dev_key()
    player_key = get_player_key()

    # get file iv
    file_iv = get_file_iv(file_id)
    file_iv = base64.b64decode(file_iv)

    dev_enc = encrypt(device_key, file_iv)
    dev_enc = base64.b64encode(dev_enc)

    # encrypt with user key
    uenc_url = server_url +'/encrypt/'
    alias = get_client_alias()

    message = os.urandom(1024)
    nonce = base64.b64encode(message)
    signature = sign_message(message)
    signature = base64.b64encode(signature)

    data = {'clientid': alias, 'message': dev_enc, 'signature': signature, 'nonce': nonce}

    # request the server to encrypt message with user key
    user_enc = requests.post(uenc_url, data=json.dumps(data), auth=keyauth, headers=headers, verify=crt).content

    file_key = encrypt(player_key, user_enc)
    return file_key


def get_file_iv(filename):
    url = server_url + '/file-iv/'
    alias = get_client_alias()
    data = {'clientid': alias, 'filename': filename}
    return requests.get(url, data=json.dumps(data), auth=keyauth, headers=headers, verify=crt).content


def sign_message(message):

    lib = pteid.get_pkcs11_lib()
    pkcs11 = PyKCS11.PyKCS11Lib()
    pkcs11.load(lib)
    slot = pkcs11.getSlotList()[0]
    session = pkcs11.openSession(slot, PyKCS11.CKS_RO_PUBLIC_SESSION)
    certificate = pteid.get_certificate(session)

    public_key = certificate.public_key()
    m = hashlib.sha1()
    m.update(message)
    hash = m.digest()

    signature = pteid.sign(session, hash)
    return signature




