# config.py
# This file contains every aspect necessary for the correct server configuration
import getpass
import hashlib

from flask import *
from functools import wraps
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import os
import sqlite3
from cryptoUtils import encrypt, decrypt, genFileKey
import base64
from sqlalchemy import create_engine, MetaData, Table, select
import pteid
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from sqlalchemy import delete

# App configuration
app = Flask(__name__)
app.config['FILES'] = os.path.dirname(os.path.realpath(__file__)) + '/files/'
app.config['SECURITY'] = os.path.dirname(os.path.realpath(__file__)) + '/security/'
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.realpath(__file__)) + '/uploads/'
app.config['TEMP'] = os.path.dirname(os.path.realpath(__file__)) + '/tmp/'

# Connection context configuration
key = app.config['SECURITY'] + 'iedcs.key'
crt = app.config['SECURITY'] + 'iedcs.crt'
app.config['CONTEXT'] = (crt, key)

# Master key
master_key = None
public_key = None

# Database configuration
crypto_db = os.path.dirname(os.path.realpath(__file__)) +'/crypto.db'
iedcs_db = os.path.dirname(os.path.realpath(__file__)) +'/iedcs.db' #unused for now

engine = create_engine('sqlite:///' + crypto_db)

metadata = MetaData(bind=engine)

files = Table('files', metadata, autoload=True)
players = Table('players', metadata, autoload=True)
devices = Table('devices', metadata, autoload=True)
users = Table('users', metadata, autoload=True)
user_devices = Table('user_devices', metadata, autoload=True)
filekeys = Table('filekeys', metadata, autoload=True)
purchases = Table('purchases', metadata, autoload=True)
nonces = Table('nonces', metadata, autoload=True)

con = engine.connect()

# Authentication functions
# Different passwords for different services

# Basic operations authentication
def auth_basic(username, password):
    return username == 'iedcsp^kYQF!' and password == 'a3tGR4ULq_p=w@Sd'

def set_master_key():
    global master_key

    pwd = getpass.getpass(prompt="Private key access password: \n")
    with open('private.pem', 'rb') as private_rsa_file:
        master_key = RSA.importKey(private_rsa_file.read(), pwd)

def master_encrypt(message):
    global public_key

    return public_key.encrypt(message, 32)

def set_public_key():
    global public_key

    with open('public.pem', 'rb') as public_rsa_file:
        public_key = RSA.importKey(public_rsa_file.read())

# Keys-related operations authentication
def auth_keys(username, password):
    # let's leave this as it is for now
    return username == 'iedcskKRKm' and password == '5ujCjm8TwGBG*G$b'

# File-related operations authentication
def auth_file(username, password):
    # let's leave this as it is for now
    return username == 'iedcsf$NhpS^' and password == '8PAxd$_?UuXKJYJk'


# Request authentication
def authenticate():
    return Response(
        'Unauthorized request', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth_basic(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def key_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth_keys(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def file_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth_file(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Check if HTTP Headers are valid
def valid_header(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user_agent.__str__() != 'iedcs-player/0.1':
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# Database-related functions

def new_device(username, certificate_data, alias, device_key, signature, nonce):

    # let's check if certificate is valid before doing anything
    if not pteid.check_certificate_data(certificate_data):
        return False

    certificate = x509.load_pem_x509_certificate(certificate_data, default_backend())

    c_public_key = certificate.public_key()

    m = hashlib.sha1()
    m.update(nonce)
    hash = m.digest()

    # check if signature is valid
    if not pteid.check_signature(c_public_key, signature, hash):
        return False

    userid = get_user_id(username)

    # if the user is registered
    if userid > 0:
        # let's assign a new device to this user
        print 'assigning new device to id '+ str(userid)
        if not assign_device(userid, device_key, alias):
            return False

    else:
        # let's create a new user
        if not new_user(username, certificate_data, alias, device_key):
            return False

    return True

def get_device_key(devkey_id):
    return get_key(devices, devkey_id)

def get_player_key(id = 1):
    return get_key(players, id)

def get_user_key(id):
    return get_key(users, id)

# gets the user id associated with username
def get_id(table, param, value):
    #requires that param needs to by default an attribute from a table (e.g. users.c.id)
    query = select([table.c.id], param == value)

    try:
        id = query.execute().fetchall()[0][0]
        return id
    except IndexError:
        return -1

def get_key(table, id):
    query = select([table.c.key], table.c.id == id)
    try:
        global master_key
        key = query.execute().fetchall()[0][0]
        key = base64.b64decode(key)
        key = master_key.decrypt(key)
        return key
    except IndexError:
        return -1

def is_revoked(table, key):
    query = select([table.c.revoked], table.c.key == key)
    try:
        value = query.execute().fetchall()[0][0]
        return value != 0
    except Exception:
        return True

# get user id
def get_user_id(username):
    return get_id(users, users.c.username, username)

def get_user_id_from_certificate(certificate):
    return get_id(users, users.c.certificate, certificate)


# get user certificate
def get_user_certificate(id):
    query = select([users.c.certificate], users.c.id == id)

    try:
        value = query.execute().fetchall()[0][0]
        return base64.b64decode(value)
    except Exception:
        return None

# gets parameters from the table devices
def get_device_id(device_key):
    return get_id(devices, devices.c.key, device_key)

# gets parameters from the table files
def get_file_id(filename):
    return get_id(files, files.c.filename, filename)

def get_file_path(filename):
    query = select([files.c.path], files.c.filename == filename)
    res = query.execute().fetchall()
    try:
        return res[0][0]
    except IndexError:
        return -1

def get_client_id(alias):
    return get_id(user_devices, user_devices.c.alias, alias)

def get_file_key_id(clientid, fileid):
    cursor = sqlite3.connect(crypto_db).cursor()
    rows = cursor.execute("select filekeyid from purchases where clientid = ? and fileid = ?", (clientid, fileid)).fetchall()
    cursor.close()
    try:
        return rows[0][0]
    except IndexError:
        return -1

def get_file_key(filename, client_alias):
    clientid = get_client_id(client_alias)
    fileid = get_file_id(filename)

    fkeyid = get_file_key_id(clientid, fileid)

    return get_key(filekeys, fkeyid)

def get_file_iv_db(filename, client_alias):

    clientid = get_client_id(client_alias)

    if clientid < 1:
        return -1

    fileid = get_file_id(filename)

    if fileid < 1:
        return -1

    userid = get_user_data(client_alias)[0][0]

    num_devices = count_devices(userid)

    if num_devices == 0 or num_devices > 2:
        return -1

    rows = select([user_devices.c.id], user_devices.c.userid == userid).execute().fetchall()
    cursor = sqlite3.connect(crypto_db).cursor()

    clientid = str(clientid)
    fileid = str(fileid)
    rows = cursor.execute("select iv from purchases where clientid = ? and fileid = ?", (clientid, fileid)).fetchall()
    cursor.close()

    try:
        global master_key
        iv = rows[0][0]
        iv = base64.b64decode(iv)
        iv = master_key.decrypt(iv)
        return iv
    except Exception:
        return -1




def already_purchased(clientid, fileid):
    cursor = sqlite3.connect(crypto_db).cursor()
    rows = cursor.execute("select * from purchases where clientid = ? and fileid = ?", (clientid, fileid)).fetchall()
    try:
        return rows[0][0] > 0
    except IndexError:
        return False

# returns the userid and deviceids associated with alias
def get_user_data(alias):
    query = select([user_devices.c.userid, user_devices.c.deviceid], user_devices.c.alias == alias)

    try:
        return query.execute().fetchall()
    except IndexError:
        return -1

def count_instance(table, param, value):
     #requires that param needs to by default an attribute from a table (e.g. users.c.id)
    query = select([table.c.id], param == value)

    try:
        count = len(query.execute().fetchall())
        print "Device number: ", count
        return count
    except IndexError:
        return -1


def count_devices(user_id):
    return count_instance(user_devices, user_devices.c.userid, user_id)

def assign_device(userid, device_key, alias):
    # prepare device_key
    global public_key
    device_key = public_key.encrypt(device_key, 32)[0]
    device_key = base64.b64encode(device_key)

    # check if this device key was already assigned to another user
    device_key_id = get_device_id(device_key)
    if device_key_id > 0:
        # TODO: Apply restrictions?
        insertRows(crypto_db, 'user_devices', (None, userid, device_key_id, alias), 1)
        return True

    # otherwise, let's add a new device

    # check if the key is already assigned to another device
    num_devices = count_devices(userid)

    if num_devices >= 2:
        return False

    insertRows(crypto_db, 'devices', (None, device_key, 0), 1)
    device_key_id = get_device_id(device_key)

    # check if the operation was successful
    if device_key_id < 1:
        return False

    insertRows(crypto_db, 'user_devices', (None, userid, device_key_id, alias), 1)
    return True

def new_user(username, certificate, alias, device_key):
    # generate a new user key
    global public_key
    user_key = SHA256.new(os.urandom(16)).digest()
    user_key = public_key.encrypt(user_key, 32)[0]
    user_key = base64.b64encode(user_key)

    certificate = base64.b64encode(certificate)

    insertRows(crypto_db, 'users', (None, username, certificate, user_key, 0), 1)

    # find the user ID we've just inserted
    userid = get_user_id(username)
    if userid < 1:
        return False

    # Assign device key to user
    return assign_device(userid, device_key, alias)

def new_file(filename, path):
    # generate a new user key
    insertRows(crypto_db, 'files', (None, filename, path), 1)

def get_client_by_user(userid):
    query = select([user_devices.c.id], user_devices.c.userid == userid)

    try:
        rows = query.execute().fetchall()
        return rows
    except IndexError:
        return -1

def check_nonce(nonce):
    # checks if a given nonce is valid
    # nonces are already base64 encoded

    query = select([nonces.c.id], nonces.c.nonce == str(nonce))

    try:
        rows = query.execute().fetchall()
        if rows == []:
            insertRows(crypto_db, 'nonces', (None, nonce), 1)
            return True
        return False
    except IndexError:
        insertRows(crypto_db, 'nonces', (None, nonce), 1)
        return True



def process_purchase(alias, filename):

    client_id = get_client_id(alias)

    user_data = get_user_data(alias)
    user_id = user_data[0][0]
    device_id = user_data[0][1]

    # We just have one version of the player
    player_id = 1

    file_id = get_file_id(filename)
    player_key = get_player_key()
    user_key = get_user_key(user_id)


    if(already_purchased(client_id, file_id)):
        return False

    device_key = get_device_key(device_id)

    num_devices = count_devices(user_id)

    if num_devices == 0 or num_devices > 2:
        return False

    file_iv = None


    # checking multiple user_device instances

    client_id_list = get_client_by_user(user_id)
    fk_exists = False
    file_key_id = -1
    file_key = -1

    for client in client_id_list:
        file_key_id = get_file_key_id(client[0], file_id)

        if file_key_id != -1 and client[0] != client_id:
            fk_exists = True
            file_key = get_key(filekeys, file_key_id)
            first_dec = decrypt(player_key, file_key)
            second_dec = decrypt(user_key, first_dec)
            file_iv = decrypt(device_key, second_dec)

            break
        else:
            file_iv = SHA256.new(os.urandom(16)).digest()

    global public_key

    file_iv_db = public_key.encrypt(file_iv, 32)[0]
    file_iv_db = base64.b64encode(file_iv_db)

    if fk_exists == False:
        file_key = genFileKey(player_key, device_key, user_key, file_iv)

        file_key_db = public_key.encrypt(file_key, 32)[0]
        file_key_db = base64.b64encode(file_key_db)

        # process purchase
        insertRows(crypto_db, 'filekeys', (None, file_key_db, 0), 1)

        # get file key id
        file_key_id = get_id(filekeys, filekeys.c.key, file_key_db)

    # store purchase
    insertRows(crypto_db, 'purchases', (None, client_id, player_id, file_id, file_key_id, file_iv_db), 1)

    return True

def get_all_files():
    query = select([files.c.id, files.c.filename])
    try:
        return query.execute().fetchall()
    except IndexError:
        return -1

def dump_files_to_json():

    files = get_all_files()
    dict = { "id" : [ x[0] for x in files],
             "titles" : [ x[1] for x in files] }
    return json.dumps(dict)


def insertRows(db, table, values, nrows):
    c = sqlite3.connect(db)
    cursor = c.cursor()
    query = "pragma table_info(" + table + ")"
    cursor.execute(query)
    cols = len(cursor.fetchall())

    query = "insert into " + table + " values("
    for i in range(cols):
        if i != cols-1:
            query += "?,"
        else:
            query +="?)"

    if nrows == 1:
        cursor.execute(query, values)
    else:
        cursor.executemany(query, values)

    c.commit()
    cursor.close()


def disconnect_user(userid, deviceid):
    # deletes this alias from the database
    try:
        c = sqlite3.connect(crypto_db)
        cursor = c.cursor()
        rows = cursor.execute("delete from user_devices where userid = ? and deviceid = ?", (userid, deviceid))
        c.commit()
        cursor.close()
        return True
    except Exception:
        return False
