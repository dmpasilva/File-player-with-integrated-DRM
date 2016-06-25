from Crypto.Cipher import AES
from Crypto import Random
import base64
import os
import random
import string

# Block size definition
BLOCK_SIZE = AES.block_size

encode = lambda k: pad(k)
decode = lambda k: unpad(k)

pad = lambda s: s + ((BLOCK_SIZE-len(s) % BLOCK_SIZE) * '{')

def unpad(message):
    l = message.count('{')
    decoded = message[:len(message)-l]
    return decoded

def encEDEFileKey(userKey, deviceKey, playerKey, message):
    user_enc = userKey.encrypt(encode(message))
    dev_enc = deviceKey.decrypt(user_enc)
    return playerKey.encrypt(dev_enc)

def decEDEFileKey(userKey, deviceKey, playerKey, mess_enc):
    player_dec = playerKey.decrypt(mess_enc)
    device_dec = deviceKey.encrypt(player_dec)
    user_dec = userKey.decrypt(device_dec)
    return decode(user_dec)
    #return user_dec

def encrypt_file(userKey, deviceKey, playerKey, file_in): #, file_out=None):
    bs = AES.block_size
    finished = False

    while not finished:
        chunk = file_in.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)
            finished = True
    return encEDEFileKey(userKey, deviceKey, playerKey, chunk)


def decrypt_file(userKey, deviceKey, playerKey, file_in): #, file_out=None):
    bs = AES.block_size
    finished = False

    while not finished:
        chunk = file_in.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)
            finished = True
    return decEDEFileKey(userKey, deviceKey, playerKey, chunk)




device_plain = 'deviceid'
deviceKey = AES.new(encode(device_plain)) #, AES.MODE_CBC, iv)

user_plain = 'username'
rnd = Random.new()
userKey = AES.new(encode(user_plain)) #, AES.MODE_CBC, rnd.read(BLOCK_SIZE))

player_plain = 'playerid'
rnd = Random.new()
playerKey = AES.new(encode(player_plain)) #, AES.MODE_CBC, rnd.read(BLOCK_SIZE))

temp = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
temp2 = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
f2 = open(temp, 'w+b')
f3 = open(temp2, 'w+b')

f = open('test.txt', 'rb')
fe = open(temp2, 'rb')
f2.write(encrypt_file(userKey, deviceKey, playerKey, f))
f3.write(decrypt_file(userKey, deviceKey, playerKey, fe))


f.close()
f2.close()

enc = encEDEFileKey(userKey, deviceKey, playerKey, player_plain)