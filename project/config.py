import json

from paths import get_data_dir

SETTINGS_FILE = get_data_dir() / "settings.json"

DEFAULT_SETTINGS = {
    "volume": 50,
    "resolution": "1920x1080",
    "difficulty": "Нормальный",
}


def load_settings():
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()

    out = DEFAULT_SETTINGS.copy()
    for key, value in data.items():
        if key in DEFAULT_SETTINGS:
            out[key] = value
    if out.get("difficulty") == "Лёгкий":
        out["difficulty"] = "Новичок"
    return out


def save_settings(settings):
    safe = {}
    for key, default in DEFAULT_SETTINGS.items():
        safe[key] = settings.get(key, default)
    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(safe, f, ensure_ascii=False, indent=4)
