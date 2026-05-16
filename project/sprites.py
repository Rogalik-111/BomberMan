import tkinter as tk
from pathlib import Path
from tkinter import *
import sys
ASSETS_DIR = Path(__file__).with_name("Images")

# Имя спрайта → файл в папке Images/
SPRITE_FILES = {
    "Player": "Player.png",
    "EnemyRight": "EnemyRight.png",
    "EnemyLeft": "EnemyLeft.png",
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

    pathr = resource_path(f"Images/{SPRITE_FILES['EnemyRight']}")
    pathl = resource_path(f"Images/{SPRITE_FILES['EnemyLeft']}")
    if not pathr.exists() and not pathl.exists():
        _enemy_faces[key] = (None, None)
        return _enemy_faces[key]

    try:

        left = PhotoImage(file = f"{pathr}", master=master)
        right = PhotoImage(
            file = f"{pathl}", master=master
        )
        _enemy_faces[key] = (left, right)
    except Exception:
        _enemy_faces[key] = (None, None)

    return _enemy_faces[key]
