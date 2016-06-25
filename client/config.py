# coding=utf-8
import os
import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy import create_engine, MetaData, Table, select, delete
import sqlite3


# Player Key, Device Key and client alias
player_key = None
device_key = None
client_alias = None

serialnumber = None     # Cartão de cidadão

# Variables definition
server_url = 'https://localhost:8000'
security_folder = os.path.dirname(os.path.realpath(__file__)) + '/security/'
library_path = os.path.dirname(os.path.realpath(__file__)) + '/library/'

database = security_folder + 'iedcs.db'


engine = create_engine('sqlite:///' + database)

metadata = MetaData(bind=engine)

con = engine.connect()

# Auth types

basicauth = HTTPBasicAuth('iedcsp^kYQF!', 'a3tGR4ULq_p=w@Sd')
keyauth = HTTPBasicAuth('iedcskKRKm', '5ujCjm8TwGBG*G$b')
fileauth = HTTPBasicAuth('iedcsf$NhpS^', '8PAxd$_?UuXKJYJk')

# Headers
headers = {'user-agent': 'iedcs-player/0.1'}

crt = security_folder + 'iedcs.crt'

device_key_path = security_folder + 'device.key'

def set_player_key(value):
    global player_key
    player_key = value

def set_dev_key(value):
    global device_key
    device_key = value

def get_player_key():
    return player_key

def get_dev_key():
    return device_key

def get_user_name():
    return username

def set_user_name(value):
    global username
    username = value

def get_client_alias():
    return client_alias

def set_client_alias(value):
    global client_alias
    client_alias = value

def get_titles_from_library():
    books = get_books_table()
    query = select([books.c.title], books.c.owner == get_serialNumber())
    try:
        return query.execute().fetchall()
    except IndexError:
        return -1

def get_file(title):
    cursor = sqlite3.connect(database).cursor()
    rows = cursor.execute("select local_filename from books where title = ? and owner = ?", (title, get_serialNumber())).fetchall()
    cursor.close()
    try:
        return rows[0][0]
    except IndexError:
        return -1

def get_titles_from_server():
    url = server_url + '/titles_list'
    return requests.get(url, data=None, auth=basicauth, headers=headers, verify=crt).content


def already_downloaded(title):
    cursor = sqlite3.connect(database).cursor()
    rows = cursor.execute("select id from books where title = ? and owner = ?", (title, get_serialNumber())).fetchall()
    cursor.close()
    try:
        return rows != []
    except IndexError:
        return -1

def get_books_table():
    return Table('books', metadata, autoload=True)


def get_serialNumber():
    global serialnumber
    return serialnumber

def set_serialNumber(sn):
    global serialnumber
    serialnumber = sn