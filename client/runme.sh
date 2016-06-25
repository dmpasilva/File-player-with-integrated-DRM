#!/bin/bash

# Set python interpreter location (if virtualenv). Leave as python if system.
PYTHON_INTERPRETER=../../../virtualenv/client/bin/python

echo "----------------------------"
echo "Starting IEDCS Client..."
echo "----------------------------"
$PYTHON_INTERPRETER client.py
wait
echo "----------------------------"
echo "Removing leftovers..."
echo "----------------------------"
rm security/*.cfg
rm security/*.db
rm security/*.key
rm library/*