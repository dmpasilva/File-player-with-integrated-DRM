# IEDCS - Identity Enabled Distribution Control System #

This project consists in a generic file player with an integrated DRM system, which was developed on the Security course of the Integrated Masters in Computers and Telematics Engineering (University of Aveiro). 
Both client and server sides are implemented. With the client module, one can create a user account (which has an associated User Key on the server and a Device Key on the user's computer). Along with a pre-shared secret (Player Key), without ever transmitting all keys between the two sides, a File Key is computed for each file purchased by the user. Whenever a user purchases an item, the file is encrypted with the File Key and it is transferred to the user's computer. Only the user who bought the file can access its content, as it is never stored after decryption.
In this assignment, we used ePUB files as purchasable and downloadable content. In order to display its content without ever storing the decrypted file, we wrote a simple extension to the EbookLib Python library which parses a binary stream of data. Client has a simple GUI implemented with Tkinter.
Finally, all messages are signed in an HTTPS connection with the Portuguese Citizen card and the server included a deployable encrypted filesystem via EncFS.

## Main keywords ##

* Python
* Flask
* PyCrypto
* SQLAlchemy
* PySqlite
* EbookLib
* TKinter
* PyKCS11
* PTEID
* EncFS
* Bash

## Deployment instructions ##

* There are two virtual environments in order to handle which each side's dependencies independently. All dependencies are in requirements_client.txt and requirements_server.txt. 
* Client: Edit runme.sh in order to include the path to the virtualenv's Python interpreter and run the script.
* Edit runme_xxxxx.sh (where xxxxxx is the platform's OS; e.g., runme_osx.sh or runme_linux.sh) in order to include the path to the virtualenv's Python interpreter and run the script. 
* Passwords: both required passwords are "iedcs_2k15".

## Owners ##

The entire solution was developped by me and David Silva ([dmpasilva](https://bitbucket.org/dmpasilva)).