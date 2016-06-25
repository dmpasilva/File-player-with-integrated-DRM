#!/bin/bash

# Set python interpreter location (if virtualenv). Leave as python if system.
PYTHON_INTERPRETER=../../../virtualenv/server/bin/python

realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

ABS_PATH_ENC=$(realpath enc_files)
ABS_PATH_DEC=$(realpath files)

echo "----------------------------"
echo "Now mounting directory with encfs"
echo "----------------------------"
encfs $ABS_PATH_ENC $ABS_PATH_DEC
wait
echo "----------------------------"
echo "Initializing sql database..."
echo "----------------------------"
$PYTHON_INTERPRETER sql_init.py
wait
$PYTHON_INTERPRETER sqlfill.py
wait
echo "----------------------------"
echo "Running web server."
echo "----------------------------"
$PYTHON_INTERPRETER server.py
wait
echo "----------------------------"
echo "Removing leftovers..."
echo "----------------------------"
# remove db
rm -r crypto.db
wait
echo "----------------------------"
echo "Unmounting encrypted directory."
echo "----------------------------"
# add sudo if using Linux
umount $ABS_PATH_DEC