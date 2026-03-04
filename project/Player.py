
import tkinter as tk
from tkinter import *
class Player:
    def __init__(self):
        self.bomberman = PhotoImage(file='bomberman.png')

    def on_key_press(self, event):
        if event.key == "W":
            self.canvas.move(self.rect_id, 0, 1)


