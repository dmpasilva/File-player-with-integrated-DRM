import sqlite3

# CREATE two DATABASES:
#   - crypto.db, contains cryptographic information
#   - iedcs.db, contains store elements (to be implemented)
 
crypt = sqlite3.connect('crypto.db')

# File TABLE
c = crypt.cursor()
 
query = "create table players(" \
        "id integer primary key autoincrement, " \
        "key text, " \
        "revoked integer)"
 
c.execute(query)
 
query = "create table files(" \
        "id integer primary key autoincrement, " \
        "filename text unique, " \
        "path text unique)"
 
c.execute(query)
 
query = "create table users(" \
        "id integer primary key autoincrement, " \
        "username text unique, "\
        "certificate text unique, "\
        "key text unique," \
        "revoked integer)"
 
c.execute(query)
 
query = "create table devices(" \
        "id integer primary key autoincrement, " \
        "key text unique, "\
        "revoked integer) "
 
c.execute(query)

query = "create table user_devices(" \
        "id integer primary key autoincrement, " \
        "userid integer references users(id), "\
        "deviceid integer references devices(id), "\
        "alias text unique)"

c.execute(query)

query = "create table filekeys(" \
        "id integer primary key autoincrement, " \
        "key text, " \
        "revoked integer)"

c.execute(query)

 
query = "create table purchases(" \
        "id integer primary key autoincrement, " \
        "clientid integer references user_devices(id), "\
        "playerid integer references players(id), "\
        "fileid integer references files(id), "\
        "filekeyid integer references filekeys(id), "\
        "iv text )"

c.execute(query)

query = "create table nonces(" \
        "id integer primary key autoincrement, " \
        "nonce text)"

c.execute(query)