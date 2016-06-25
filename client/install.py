# First time install

from uuid import getnode as get_mac
import os
import platform
import random
from Crypto.Hash import SHA256

# Get system serial number
def get_serial_number():
    current_os = platform.system()

    if(current_os == 'Windows'):
        return os.popen("wmic diskdrive get serialnumber").read().split('\r\n')[1].rstrip(' ')

    elif(current_os == 'Darwin'):
        return os.popen('ioreg -l | grep IOPlatformSerialNumber').read().split('"')[3]

    elif(current_os == 'Linux'):
        doc = 'dmi.txt'
        os.system("gksudo dmidecode > " + doc)
        try:
            return read_dmi(doc)
        except Exception:
            print 'Root privileges is required for this operation to proceed. Please try again.'
            os._exit(1)

    else:
        print "IEDCS Error: Your platform is not supported!"
        os._exit(1)

# Read Linux's dmidecode output file
def read_dmi(f):
    i=0
    f_rd=open(f,'r')
    result = None
    for line in f_rd:
        if i:
            if line.__contains__("Serial"):
                split = line.split(" ")
                result = split[2]
                break;
        if line.__contains__("System Information"):
            i += 1

    # This file is no longer needed
    os.unlink(f)
    return result

# Generate device Key
def gen_device_key():
    mac = get_mac()
    serial_number = get_serial_number()

    concat = str(mac) + serial_number
    device = ''.join(random.sample(concat,len(concat)))

    return SHA256.new(device).digest()

def generate_alias():
    return SHA256.new(os.urandom(1024)).digest()