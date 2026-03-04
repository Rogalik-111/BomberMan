import tkinter as tk
from tkinter import *
from tkinter import ttk

import Player
#Создание окна
root = tk.Tk()
root.title("BomberMan")
root.geometry("800x600")


def click_button():
    root.destroy()

btn = ttk.Button(text = "Выход", command = click_button)
btn.pack(anchor="w", expand=True)


#Игровой цикл
root.mainloop()
