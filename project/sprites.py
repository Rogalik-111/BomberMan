import tkinter as tk
from pathlib import Path
import sys
ASSETS_DIR = Path(__file__).with_name("Images")

# Имя спрайта → файл в папке Images/
SPRITE_FILES = {
    "Player": "Player.png",
    "Enemy": "Enemy.png",
    "Bomb": "Bomb.png",
    "Bonus": "Bonus.png",
    "BonusBomb": "BonusBomb.png",
    "BonusRadius": "BonusRadius.png",
    "BonusLife": "BonusLife.png",
    "Wall": "Wall.png",
    "BreakableWall": "BreakableWall.png",
    "MenuBack": "MenuBack.png",
    "Door": "Door.png",
    "Explosion": "Explosion.png",
}

_cache = {}
_enemy_faces = {}


def resource_path(relative_path):
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path

def get_sprite(name):
    if name in _cache:
        return _cache[name]

    filename = SPRITE_FILES.get(name)
    if not filename:
        return None

    path = resource_path(f"Images/{filename}")
    if not path.exists():
        return None

    try:
        img = tk.PhotoImage(file=str(path))
    except tk.TclError:
        return None

    _cache[name] = img
    return img

def get_enemy_face_images(master):
    key = id(master)
    if key in _enemy_faces:
        return _enemy_faces[key]

    path = resource_path(f"Images/{SPRITE_FILES['Enemy']}")
    if not path.exists():
        _enemy_faces[key] = (None, None)
        return _enemy_faces[key]

    try:
        from PIL import Image, ImageTk

        im = Image.open(path).convert("RGBA")
        left = ImageTk.PhotoImage(im, master=master)
        right = ImageTk.PhotoImage(
            im.transpose(Image.FLIP_LEFT_RIGHT), master=master
        )
        _enemy_faces[key] = (left, right)
    except Exception:
        _enemy_faces[key] = (None, None)

    return _enemy_faces[key]
