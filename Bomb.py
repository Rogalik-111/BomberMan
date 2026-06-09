from settings import TILE
from sprites import get_sprite


class Bomb:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y

        img = get_sprite("Bomb")
        self.image = img

        if img is not None:
            self.id = canvas.create_image(
                x * TILE + TILE // 2,
                y * TILE + TILE // 2,
                image=img,
                anchor="center",
            )
        else:
            size = TILE * 0.6
            offset = (TILE - size) / 2
            self.id = canvas.create_oval(
                x * TILE + offset,
                y * TILE + offset,
                x * TILE + offset + size,
                y * TILE + offset + size,
                fill="black",
            )

    def destroy(self):
        self.canvas.delete(self.id)
