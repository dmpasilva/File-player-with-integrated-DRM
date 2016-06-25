import epub_parser
from Tkinter import *

# Read epub file
def read_epub(epub):

    title = 'IEDCS Player'

    text = epub_parser.Parser().extract(epub)

    window = Tk()
    window.wm_title(title)

    # create frame
    frame = Frame(window, width=600, height=700)
    frame.pack(fill="both", expand=True)
    frame.grid_propagate(False)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    #create text widget
    t = Text(frame)
    t.config(font=("helvetica", 12))
    t.pack(side=LEFT, fill=Y)
    t.insert(INSERT, text)

    scroll = Scrollbar(frame)
    scroll.pack(side=RIGHT, fill=Y)
    scroll.config(command=t.yview)
    t.config(yscrollcommand=scroll.set)

    window.mainloop()