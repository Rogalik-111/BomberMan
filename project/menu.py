import tkinter as tk
from settings import WIDTH, HEIGHT, BG

def show_menu(root):
    frame = tk.Frame(root, width=WIDTH, height=HEIGHT, bg=BG)
    frame.pack()

    title = tk.Label(frame, text="Bomberman", font=("Arial", 40), fg="white", bg=BG)
    title.place(relx=0.5, rely=0.3, anchor="center")

    start = tk.Button(frame, text="Start", font=("Arial", 20),
                      command=lambda: frame.destroy())
    start.place(relx=0.5, rely=0.5, anchor="center")

    root.wait_window(frame)