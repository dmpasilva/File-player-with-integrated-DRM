import PyKCS11
import cryptography
from Crypto.Hash import SHA256
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
import hashlib
from OpenSSL import crypto
import glob

def get_trusted_certs():
    files = glob.glob("certificates/*.pem")
    certificates = []

    for certificate in files:
        certificates.append(crypto.load_certificate(crypto.FILETYPE_PEM, open(certificate, "r").read()))

    return certificates

def check_signature(public_key, signature, hash):
    # Based on code from http://ludovicrousseau.blogspot.pt/2011/04/pykcs11-provided-samples-dumpitpy.html
    sx = eval('0x%s' % signature)

    exponent = public_key.public_numbers().e
    modulus = public_key.public_numbers().n

    decrypted = pow(sx, exponent, modulus)  # RSA
    d = hexx(decrypted).decode('hex')

    return hash == d[-20:]

# we must use OpenSSL here because cryptography does not provide methods for certificate verification
def check_certificate_data(certificate):
    try:
        certificate = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
        store = crypto.X509Store()

        trusted_certs = get_trusted_certs()

        for cert in trusted_certs:
            store.add_cert(cert)

        store_ctx = crypto.X509StoreContext(store, certificate)
        store_ctx.verify_certificate()
        return True
    except Exception:
        return False

# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/142812
# Title: Hex dumper
# Submitter: Sebastien Keim (other recipes)
# Last Updated: 2002/08/05
# Version no: 1.0

def hexx(intval):
    x = hex(intval)[2:]
    if (x[-1:].upper() == 'L'):
        x = x[:-1]
    if len(x) % 2 != 0:
        return "0%s" % x
    return x