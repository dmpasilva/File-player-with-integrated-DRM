import PyKCS11
import cryptography
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
import platform, os

def get_pkcs11_lib():
    current_os = platform.system()

    if(current_os == 'Windows'):
        return "pteidpkcs11.dll"

    elif(current_os == 'Darwin'):
        return "libpteidpkcs11.dylib"

    elif(current_os == 'Linux'):
        return " /usr/local/lib/libpteidpkcs11.so"

    return None     # unsupported OS

def get_certificate(session):
    cert = session.findObjects(template=( (PyKCS11.CKA_LABEL, "CITIZEN AUTHENTICATION CERTIFICATE"),
                                          (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
                                          (PyKCS11.CKA_CERTIFICATE_TYPE, PyKCS11.CKC_X_509) ))[0]

    cert_data = ''.join(chr(c) for c in cert.to_dict()['CKA_VALUE'])

    certificate = cryptography.x509.load_der_x509_certificate(cert_data, default_backend())
    return certificate


def get_authentication_object(session):
    objects = session.findObjects(template=( (PyKCS11.CKA_LABEL, "CITIZEN AUTHENTICATION KEY"),
                                             (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                                             (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA) ))

    return objects[0]


def get_certificate_bytes(certificate):
    return certificate.public_bytes(Encoding.PEM)


def sign(session, hash, object=None):
    if object == None:
        object = get_authentication_object(session)

    signature = session.sign(object, hash)
    s = ''.join(chr(c) for c in signature).encode('hex')

    return s