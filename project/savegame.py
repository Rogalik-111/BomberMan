import json
from pathlib import Path

SAVE_FILE = Path(__file__).with_name("game_save.json")


def has_save():
    if not SAVE_FILE.exists():
        return False
    return load_save() is not None


def clear_save():
    if SAVE_FILE.exists():
        SAVE_FILE.unlink()


def load_save():
    try:
        with SAVE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    for key in (
        "level_number",
        "score",
        "lives",
        "max_bombs",
        "radius",
        "time_left",
        "level",
    ):
        if key not in data:
            return None
    return data


def save_from_game(g):
    payload = {
        "level_number": g.level_num,
        "score": g.score,
        "lives": g.player.lives,
        "max_bombs": g.max_bombs,
        "radius": g.blast_radius,
        "time_left": g.time_left,
        "level": g.grid,
        "player_x": g.player.x,
        "player_y": g.player.y,
        "exit_pos": list(g.exit_cell) if g.exit_cell else None,
        "enemies": [[e.x, e.y] for e in g.enemies],
        "bonuses": [{"x": x, "y": y, "kind": b.kind} for (x, y), b in g.bonuses.items()],
    }
    with SAVE_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
