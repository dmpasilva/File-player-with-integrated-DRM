# server.py
# Handles every server request
import hashlib

from config import *
from cryptoUtils import *
import string
import random
import json
from cryptography import x509
from cryptography.hazmat.backends import default_backend


# Routes

@app.route('/file-iv/', methods=['GET'])
@valid_header
@key_auth
def get_file_iv():
    data = json.loads(request.data)

    clientid = data['clientid']
    filename = data['filename']

    fileiv = get_file_iv_db(filename, clientid)
    if fileiv == -1:
        return Response('Unauthorized request', 401)
    fileiv = base64.b64encode(fileiv)
    return fileiv

# list of existing files to Web Store
@app.route('/hello', methods=['POST'])
@basic_auth
@valid_header
def greet():
    # secret passphrase
    if request.data == 'w7_4A#?B/!Lepv<;':
        return 'OK'
    else:
        return Response('Unauthorized request', 401)

# basic challenge
@app.route('/titles_list/', methods=['GET'])
@valid_header
@basic_auth
def get_titles_list():

    return dump_files_to_json()

@app.route('/hello2', methods=['POST'])
@key_auth
@valid_header
def newDevice():

    try:
        data = json.loads(request.data)

        # payload = {'username': username, 'alias': alias, 'key': k, 'certificate': c}
        username = data['username']
        alias = data['alias']
        cert = data['certificate']
        sign = data['signature']
        nonce = data['nonce']

    except Exception:

        return Response('Unauthorized request', 401)

    # check if nonce is valid
    if not check_nonce(nonce):
        return Response('Unauthorized request', 401)

    player_key = get_player_key()

    # get the original device key
    device_key = data['key']
    device_key = base64.b64decode(device_key)
    certificate = base64.b64decode(cert)
    signature = base64.b64decode(sign)
    nonce = base64.b64decode(nonce)

    device_key = decrypt(player_key, device_key)

    if new_device(username, certificate, alias, device_key, signature, nonce):
        return 'OK'

    return Response('Unauthorized request', 401)

# encrypt message with user key
@app.route('/encrypt/', methods=['GET', 'POST'])
@key_auth
@valid_header
def enc_ukey():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)

            # payload = {'username': username, 'alias': alias, 'key': c}
            alias = data['clientid']
            message = data['message']
            sign = data['signature']
            nonce = data['nonce']

            # check if nonce is valid
            if not check_nonce(nonce):
                return Response('Unauthorized request', 401)

            message = base64.b64decode(message)
            signature = base64.b64decode(sign)
            nonce = base64.b64decode(nonce)

        except Exception:
            return Response('Unauthorized request', 401)

        user_data = get_user_data(alias)
        user_id = user_data[0][0]
        user_id = str(user_id)

        # check if signature is valid for the user
        certificate = get_user_certificate(user_id)

        certificate = x509.load_pem_x509_certificate(certificate, default_backend())

        c_public_key = certificate.public_key()

        m = hashlib.sha1()
        m.update(nonce)
        hash = m.digest()

        if not pteid.check_signature(c_public_key, signature, hash):
            return None

        # get user key
        user_key = get_user_key(user_id)

        return encrypt(user_key, message)


# Method for purchasing a file
@app.route('/purchase_file/', methods=['GET'])
@file_auth
@valid_header
def purchase_f():

    data = json.loads(request.data)

    alias = data['clientid']
    filename = data['filename']
    sign = data['signature']
    nonce = data['nonce']

    # check if nonce is valid
    if not check_nonce(nonce):
        return Response('Unauthorized request', 401)

    # Check if signature is valid
    signature = base64.b64decode(sign)
    nonce = base64.b64decode(nonce)

    user_data = get_user_data(alias)
    user_id = user_data[0][0]
    user_id = str(user_id)

    # check if signature is valid for the user
    certificate = get_user_certificate(user_id)

    certificate = x509.load_pem_x509_certificate(certificate, default_backend())

    c_public_key = certificate.public_key()

    m = hashlib.sha1()
    m.update(nonce)
    hash = m.digest()

    if not pteid.check_signature(c_public_key, signature, hash):
        return "FAILED"

    if not process_purchase(alias, filename):
        return "FAILED"

    return 'OK'

# Method for downloading a purchased file
@app.route('/download_file/', methods=['GET'])
@file_auth
@valid_header
def download_stage1():
    try:
        data = json.loads(request.data)

        alias = data['clientid']
        filename = data['filename']
    except Exception:
        return Response('Unauthorized request', 401)

    iv = get_file_iv_db(filename, alias)
    if iv == -1:
        return Response('Unauthorized request', 401)


    fileKey = get_file_key(filename, alias)

    temp = app.config['TEMP'] + ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
    temp = temp + '.enc'

    file_path = get_file_path(filename)

    filename = app.config['FILES']+ str(file_path)

    encrypt_file(fileKey, filename, temp)

    toreturn = send_file(temp, as_attachment=True)

    os.unlink(temp)

    return toreturn


# Disconnect user from Player
@app.route('/disconnect/', methods=['GET', 'POST'])
@key_auth
@valid_header
def disconnect():
    try:
        data = json.loads(request.data)

        alias = data['clientid']
        sign = data['signature']
        nonce = data['nonce']

        # check if nonce is valid
        if not check_nonce(nonce):
            return Response('Unauthorized request', 401)

        # Check if signature is valid
        signature = base64.b64decode(sign)
        nonce = base64.b64decode(nonce)

        user_data = get_user_data(alias)
        user_id = user_data[0][0]
        device_id = user_data[0][1]
        user_id = str(user_id)
        device_id = str(device_id)

        # check if signature is valid for the user
        certificate = get_user_certificate(user_id)

        certificate = x509.load_pem_x509_certificate(certificate, default_backend())

        c_public_key = certificate.public_key()

        m = hashlib.sha1()
        m.update(nonce)
        hash = m.digest()

        if not pteid.check_signature(c_public_key, signature, hash):
            return "FAILED"

        if disconnect_user(user_id, device_id):
            return 'OK'
        else:
            return "FAILED"

    except Exception:
        return Response('Unauthorized request', 401)


def init():
    global master_key
    global public_key

    set_master_key()
    set_public_key()


    player_key = SHA256.new('ID_PL_18272010').digest()

    player_key = master_encrypt(player_key)[0]
    player_key = base64.b64encode(player_key)
    insertRows('crypto.db', 'players', (None, player_key, 0), 1)

if __name__ == '__main__':
    init()
    app.run(host='localhost', port=8000, ssl_context=app.config['CONTEXT'])
