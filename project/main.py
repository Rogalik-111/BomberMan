import tkinter as tk

from settings import WIDTH, HEIGHT, BG, ROWS, COLS, TILE
from menu import show_menu
from Game import Game
from config import load_settings
from sound import sound_manager


def main():
    root = tk.Tk()
    root.title("Бомбермен")
    root.resizable(True, True)

    settings = load_settings()
    resolution = settings.get("resolution", f"{WIDTH}x{HEIGHT}")
    root.geometry(resolution)

    volume = settings.get("volume", 50) / 100
    sound_manager.set_volume(volume)
    sound_manager.set_music(None)
    sound_manager.play_music(loop=True)

    info_frame = tk.Frame(root, bg=BG, height=40)
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG)

    game_started = False

    while True:
        try:
            if not root.winfo_exists():
                break
        except tk.TclError:
            break

        if game_started:
            canvas.pack_forget()
            info_frame.pack_forget()

        action = show_menu(root)

        try:
            if not root.winfo_exists():
                break
        except tk.TclError:
            break

        if action == "quit":
            root.destroy()
            break

        info_frame.pack(fill="x")
        canvas.pack(fill="both", expand=True)
        if not game_started:
            canvas.config(scrollregion=(0, 0, COLS * TILE, ROWS * TILE))
            game_started = True

        canvas.delete("all")
        for w in list(info_frame.winfo_children()):
            w.destroy()

        game = Game(
            root,
            canvas,
            info_frame,
            continue_game=(action == "continue"),
        )
        try:
            root.wait_variable(game.session_var)
        except tk.TclError:
            break
        try:
            game.cleanup()
        except tk.TclError:
            pass
        if game.quit_app:
            try:
                root.destroy()
            except tk.TclError:
                pass
            break

    try:
        if root.winfo_exists():
            root.destroy()
    except tk.TclError:
        pass


if __name__ == "__main__":
    main()
