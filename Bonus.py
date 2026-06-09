from settings import TILE
from sprites import get_sprite


class Bonus:
    COLORS = {
        "bomb": "yellow",
        "radius": "orange",
        "life": "pink",
    }

    SPRITE_NAMES = {
        "bomb": "BonusBomb",
        "radius": "BonusRadius",
        "life": "BonusLife",
    }

    def __init__(self, canvas, x, y, kind):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.kind = kind

        name = self.SPRITE_NAMES.get(kind)
        self.image = get_sprite(name) if name else None
        if self.image is None:
            self.image = get_sprite("Bonus")

        if self.image is not None:
            self.id = canvas.create_image(
                x * TILE + TILE // 2,
                y * TILE + TILE // 2,
                image=self.image,
                anchor="center",
            )
        else:
            color = self.COLORS.get(kind, "white")
            size = TILE * 0.6
            offset = (TILE - size) / 2
            self.id = canvas.create_oval(
                x * TILE + offset,
                y * TILE + offset,
                x * TILE + offset + size,
                y * TILE + offset + size,
                fill=color,
            )

    def destroy(self):
        self.canvas.delete(self.id)
