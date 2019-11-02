# Sept 2018
# UI minimaliste pour les élèves

from tkinter import *
# Tk, Canvas, Frame, BOTH, Button, LEFT, CENTER, RIGHT, BOTTOM, TOP, ALL, Label, DISABLED, NORMAL, RAISED,mainloop
from enum import Enum # Not used ici
from random import randint, choice
from warnings import showwarning, warn  # No nedd ?
from tkinter.messagebox import showinfo


def onClick(i):
    deux_figs = ['X', 'O']
    print("Clic sur le bouton : " + str(i))

    # On mets un rond ou une croix au piffff
    hasard = randint(0, 1)
    new_text = deux_figs[hasard]
    liste_buttons[i-1]["text"] = new_text # -1 car les indices commencent à 0

def redo():
    print("On va rejouer ")

def start():
    global liste_buttons
    win = Tk()
    win.geometry("600x400+300+0")
    groupe_frame = Frame(win,borderwidth=2,relief=RAISED).pack(side=TOP)

    buttonframe1 = Frame(groupe_frame)
    buttonframe1.pack(side=TOP, pady=5)
    for i in range(1,4):
        b = Button(buttonframe1, fg = "green", text=chr(ord(str(i))), height=5, width=5, command=lambda i=i: onClick(i))
        b.pack(side=LEFT, padx=5)
        liste_buttons.append(b)

    buttonframe2 = Frame(groupe_frame)
    buttonframe2.pack(side=TOP, pady=5)
    for i in range(4,7):
        b = Button(buttonframe2, fg = "blue", text=chr(ord(str(i))),height=5, width=5, command=lambda i=i: onClick(i))
        b.pack(side=LEFT, padx=5)
        liste_buttons.append(b)
    #buttonframe2.pack(side=BOTTOM)
    buttonframe3 = Frame(groupe_frame)
    buttonframe3.pack(side=TOP, pady=5)
    for i in range(7,10):
        b = Button(buttonframe3, fg="magenta", text=chr(ord(str(i))), height=5, width=5, command=lambda i=i: onClick(i))
        b.pack(side=LEFT, padx=5)
        liste_buttons.append(b)

    frame11 = Frame(win)
    frame11.pack(side=BOTTOM)
    Button(frame11, text='Quit', command=win.destroy).pack(pady=5)
    Button(frame11, text='Redo', command=redo).pack(pady=5)
    return


if __name__ == "__main__" :
    liste_buttons = []
    start()
    mainloop() # Essentiel pour conserver la fenetre. Sinon, on affiche et on ferme
