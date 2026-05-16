from settings import TILE
from sprites import get_sprite


class Exit:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y

        img = get_sprite("Door")
        self.image = img

        if img is not None:
            self.id = canvas.create_image(
                x * TILE + TILE // 2,
                y * TILE + TILE // 2,
                image=img,
                anchor="center",
            )
        else:
            self.id = canvas.create_oval(
                x * TILE + TILE * 0.2,
                y * TILE + TILE * 0.2,
                x * TILE + TILE * 0.8,
                y * TILE + TILE * 0.8,
                fill="green",
            )

    def destroy(self):
        self.canvas.delete(self.id)
