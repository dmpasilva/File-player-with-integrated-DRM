#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Client initialization functions

from Crypto.Hash import SHA256
from install import gen_device_key, generate_alias
from cryptoUtils import *
from config import *
import json
import base64
import sql
import PyKCS11, pteid
from cryptography import x509
from cryptoUtils import sign_message

from config import set_serialNumber

# called every time a new Window is opened
# checks if the Cartão de Cidadão is still present
# allows user to register using another card
def init():

    # check if Cartão de Cidadão is inserted
    pkcs11 = PyKCS11.PyKCS11Lib()
    pkcs11.load(pteid.get_pkcs11_lib())
    slot = pkcs11.getSlotList()[0]

    session = pkcs11.openSession(slot, PyKCS11.CKS_RO_PUBLIC_SESSION)
    certificate = pteid.get_certificate(session)

    # get username from Cartão de Cidadão
    serialnumber = certificate.subject.get_attributes_for_oid(x509.OID_SERIAL_NUMBER)[0].value

    # If we can't connect to server, we can't validate this player
    try:
        if not test_conn():
            return False
    except Exception:
        return False

    # set player key
    set_player_key(SHA256.new('ID_PL_18272010').digest())

    # check if device key exists
    if os.path.exists(device_key_path):
        read_device_key()
    else:
        create_device_key()

    # check if database exists
    #if not os.path.exists(database):
    try:
        sql.init_sql()
    except Exception:
        pass            # table already exists, nothing to do here...

    # check if user alias exist on this machine
    if(os.path.exists(security_folder + serialnumber + ".cfg")):
        read_device_alias(serialnumber)
    else:
        create_device_alias(serialnumber)
        valid = send_device_key()

        if not valid:
            os.unlink(security_folder + serialnumber + ".cfg")
            os.unlink(device_key_path)
            os.unlink(database)

        return valid

    set_serialNumber(serialnumber)
    return True

def read_device_key():
    with open(device_key_path, 'rb') as config:
        device_key = config.read()
    config.close()

    set_dev_key(device_key)

def create_device_key():
    device_key = gen_device_key()

    with open(device_key_path, 'wb') as config:
        config.write(device_key)
    config.close()

    set_dev_key(device_key)


def read_device_alias(serialnumber):
    with open(security_folder + serialnumber + ".cfg", 'rb') as config:
        alias = config.read()
    config.close()

    set_client_alias(alias)

def create_device_alias(serialnumber):
    device_alias = generate_alias()
    device_alias = base64.b64encode(device_alias)

    with open(security_folder + serialnumber + ".cfg", 'wb') as config:
        config.write(device_alias)
    config.close()

    set_client_alias(device_alias)


# validate the installation
def test_conn():
    test_url = server_url + '/hello'
    return requests.post(test_url, data='w7_4A#?B/!Lepv<;', headers=headers, auth=basicauth, verify=crt).content == 'OK'

def send_device_key():
    lib = pteid.get_pkcs11_lib()
    pkcs11 = PyKCS11.PyKCS11Lib()
    pkcs11.load(lib)
    slot = pkcs11.getSlotList()[0]
    session = pkcs11.openSession(slot, PyKCS11.CKS_RO_PUBLIC_SESSION)
    certificate = pteid.get_certificate(session)

    player_key = get_player_key()
    device_key = get_dev_key()
    alias = get_client_alias()

    # get username from Cartão de Cidadão
    username = certificate.subject.get_attributes_for_oid(x509.OID_SERIAL_NUMBER)[0].value

    certificate_bytes = pteid.get_certificate_bytes(certificate)

    device_url = server_url + '/hello2'
    ciph_dev = encrypt(player_key, device_key)
    k = base64.b64encode(ciph_dev)
    c = base64.b64encode(certificate_bytes)

    message = os.urandom(1024)
    n = base64.b64encode(message)
    try:
        signature = sign_message(message)
        s = base64.b64encode(signature)
    except:
        return False

    payload = {'username': username, 'alias': alias, 'key': k, 'certificate': c, 'signature': s, 'nonce': n}

    return requests.post(device_url, data =json.dumps(payload), auth=keyauth, headers=headers, verify=crt).content == 'OK'





def library_checkup():

    library_path = os.path.dirname(os.path.realpath(__file__)) + '/library/'
    for root, dirs, files in os.walk(library_path):
        for file in files:
            if file.endswith(".edcs"):
                if file_exists(library_path + file) == -1:
                    os.unlink(library_path + file)

    books = get_books_table()

    query = select([books.c.local_filename]).execute().fetchall()
    for file in query:
        file = file[0]
        if os.path.isfile(file) == False:
            books = get_books_table()
            delete(books, books.c.local_filename == file)

def file_exists(filename):
    books = get_books_table()
    query = select([books.c.id], books.c.local_filename == filename)
    try:
        return query.execute().fetchall()[0][0]
    except IndexError:
        return -1