import os
import sys
from pathlib import Path

_APP_NAME = "Bomberman"


def get_data_dir() -> Path:
    """Папка для настроек и сохранений (доступна на запись в exe и при запуске из исходников)."""
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / _APP_NAME
    else:
        base = Path(__file__).resolve().parent
    base.mkdir(parents=True, exist_ok=True)
    return base
