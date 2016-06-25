# coding=utf-8
# Open IEDCS client
import random

from init import init
from sql import *
from cryptoUtils import *
import string
from gui_aux import *
import tkMessageBox
import time
from sqlalchemy import create_engine, MetaData, Table, select

from config import get_serialNumber

from requests import ConnectionError, RequestException, HTTPError


# Database configuration
iedcs_db = os.path.dirname(os.path.realpath(__file__)) +'/security/iedcs.db'


engine = create_engine('sqlite:///' + iedcs_db)

metadata = MetaData(bind=engine)

#books = Table('books', metadata, autoload=True)

# source: http://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


class Client():
    """
    Class attributes
    > root
    > buttons
    > last_purchase_success : indica se a ultima compra foi bem sucedida
    > sample_file_name e sample_file
    > self.frame que contem os botoes principais
    """

    def __init__(self):
        self.root = Tk()
        self.root.wm_title('IEDCS Player')
        self.root.minsize(width=200, height=200)

        # create frame
        self.frame = Frame(self.root, width=200, height=200)
        self.frame.pack()

        self.library_button = Button(self.frame, text = "IEDCS Library", command= lambda: self.launch_library())
        self.library_button.pack()

        self.store_button = Button(self.frame, text="IEDCS Store", command=lambda: self.launch_store())
        self.store_button.pack()

        self.logout_button = Button(self.frame, text="Disconnect", command=lambda: self.disconnect())
        self.logout_button.pack()

        center(self.root)

        try:
            if not init():
                tkMessageBox.showinfo("IEDCS Player", "Unable to validate this player.")
                os._exit(1)
        except PyKCS11.PyKCS11Error:
            tkMessageBox.showinfo("Aborted", "Operation aborted.")
            os._exit(1)
        except IndexError:
            tkMessageBox.showinfo("Cartão de Cidadão", "Please insert your Citzen Card and try again.")
            os._exit(1)

        self.run()

    def launch_library(self):
        player = Player()

    def launch_store(self):
        try:
            store = Store()
        except:
            tkMessageBox.showinfo("IEDCS Error", "Unable to connect to the store. Please try again later.")
            os._exit(1)

    def disconnect(self):

        alias = get_client_alias()

        url = server_url + '/disconnect/'

        message = os.urandom(1024)
        nonce = base64.b64encode(message)

        signature = sign_message(message)
        signature = base64.b64encode(signature)

        data = {'clientid': alias, 'signature': signature, 'nonce': nonce}

        response = requests.get(url, data=json.dumps(data), auth=keyauth, headers=headers, verify=crt).content

        if response == 'OK':
            os._exit(0)
        else:
            tkMessageBox.showinfo("IEDCS Error", "Unable to remove device assignment.")

    def run(self):
        self.root.mainloop()

    def close_window(self, window):
        window.destroy()

class Player():

    def __init__(self):
        self.root = Tk()
        self.root.wm_title('IEDCS Library')
        self.root.minsize(width=350, height=500)

        # create frame
        self.frame = Frame(self.root, width=350, height=500)
        self.frame.grid()

        self.library_entries = []

        library_titles = get_titles_from_library()

        for title in library_titles:
            title = title[0]
            label = Label(self.frame, text=title)
            r = len(self.library_entries) + 1
            label.grid(row=r, column=1)
            file = get_file(title)
            if file == -1:
                tkMessageBox.showinfo("System info: ", "There is an error in the files library")
                return file

            button = Button(self.frame, text="Open ebook", command=lambda file1=file, title1=title: self.open_file(file1,title1))
            r = len(self.library_entries) + 1
            button.grid(row=r, column=2)

            entry = (title, file, button)
            self.library_entries.append(entry)

        center(self.root)


        self.run()

    #####################################
    ##          Player API              ##
    ######################################

    def open_file(self, file_in, title):

        #if file_in not in self.available_files:
         #   return None

        try:
            fileKey = gen_file_key(title)
            ebook = decrypt_file(fileKey, file_in)

        except Exception:
            tkMessageBox.showinfo("System Info", 'This ebook was not purchased for this user.')
            return None

        read_epub(ebook)


    def run(self):
        self.root.mainloop()

    def close_window(self, window):
        window.destroy()

class Store():

    def __init__(self):

        try:
            if not init():
                tkMessageBox.showinfo("IEDCS Player", "Unable to validate this player.")
                os._exit(1)
        except IndexError:
            tkMessageBox.showinfo("Cartão de Cidadão", "Please insert your Citzen Card and try again.")
            os._exit(1)
        except PyKCS11.PyKCS11Error:
            tkMessageBox.showinfo("Aborted", "Operation aborted.")
            os._exit(1)
        except:
            tkMessageBox.showinfo("IEDCS Player", "Unable to connect to IEDCS Server.")
            os._exit(1)

        self.root = Tk()
        self.root.wm_title('IEDCS Store')
        self.root.minsize(width=350, height=500)

          # create frame
        self.frame = Frame(self.root, width=350, height=500)
        self.frame.grid()

        self.title_entries = []

        books = json.loads(get_titles_from_server())

        for book in books['titles']:

            filename = book

            label = Label(self.frame, text=filename)
            r = len(self.title_entries) + 1
            label.grid(row=r, column=1)

            button = Button(self.frame)

            if already_downloaded(filename):
                button = Button(self.frame, text="Already downloaded")
                entry = (label, button)
                r = len(self.title_entries) + 1
                self.title_entries.append(entry)
                self.title_entries[self.title_entries.index(entry)][1].grid(row=r, column=2)

            else:
                button = Button(self.frame, text="Purchase ebook", command=lambda button1=button, filename1=filename: self.purchase_file(button1, filename1))
                entry = (label, button)
                r = len(self.title_entries) + 1
                self.title_entries.append(entry)
                self.title_entries[self.title_entries.index(entry)][1].grid(row=r, column=2)

        center(self.root)
        self.run()

    def purchase_file(self, button, filename):

        alias = get_client_alias()

        url = server_url + '/purchase_file/'

        message = os.urandom(1024)
        nonce = base64.b64encode(message)

        signature = sign_message(message)
        signature = base64.b64encode(signature)

        data = {'clientid': alias, 'filename': filename, 'signature': signature, 'nonce': nonce}

        response = requests.get(url, data=json.dumps(data), auth=fileauth, headers=headers, verify=crt).content

        purchase_success = None
        if response == 'OK':
            purchase_success = True
        else:
            purchase_success = False

        self.checkout(button, purchase_success, filename)

    def checkout(self, button, purchase_success, filename):

        if purchase_success:
            tkMessageBox.showinfo("System Info", 'Purchase succeeded!')
            self.proceed_to_download_file(button, filename)
        else:
            tkMessageBox.showinfo("Purchase failed", 'Either you already have purchased this title or the requested file is no longer available.')
            return None

        #for entry in self.title_entries:
        #    if str(entry[0].config('text')[-1]) == filename:
        #        button = entry[1]
        #        button.configure(text="Download ebook", command=lambda: self.proceed_to_download_file(button, filename))

    def proceed_to_download_file(self, button, filename):
        file = self.download_file(filename)

        if file != None:

            #books = get_books_table()
            insertRows('books', (None, file, filename, get_serialNumber()), 1)
            button.configure(text="Already owned", command=None)
        else:
            tkMessageBox("Error", "Error downloading file!")

    # download_file: retrieves file from server

    def download_file(self, fileid):
        temp = library_path
        temp += ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
        temp += '.edcs'

        alias = get_client_alias()

        data = {'clientid': alias, 'filename': fileid}
        url = server_url + '/download_file/'

        time.sleep(1.5)
        f = requests.get(url, data=json.dumps(data), auth=fileauth, headers=headers, verify=crt)
        if str(f) == '<Response [401]>':
            return None

        # Open our local file for writing
        with open(temp, "wb") as local_file:
            for chunk in f.iter_content(chunk_size=1024):
                if chunk:
                    local_file.write(chunk)

        return temp

    def run(self):
        self.root.mainloop()

    def close_window(self, window):
        window.destroy()


client = Client()
