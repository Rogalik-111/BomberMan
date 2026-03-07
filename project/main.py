import tkinter as tk
from settings import WIDTH, HEIGHT, BG
from menu import show_menu
from Game import Game

root = tk.Tk()
root.title("Bomberman")
root.geometry(f"{WIDTH}x{HEIGHT}")
show_menu(root)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG)
canvas.pack()

Game(root, canvas)
root.mainloop()