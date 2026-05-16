from settings import TILE
from sprites import get_sprite


class Explosion:
    def __init__(self, canvas, tiles):
        self.canvas = canvas
        self.ids = []
        img = get_sprite("Explosion")

        for x, y in tiles:
            if img is not None:
                self.ids.append(
                    canvas.create_image(
                        x * TILE + TILE // 2,
                        y * TILE + TILE // 2,
                        image=img,
                        anchor="center",
                    )
                )
            else:
                self.ids.append(
                    canvas.create_rectangle(
                        x * TILE,
                        y * TILE,
                        x * TILE + TILE,
                        y * TILE + TILE,
                        fill="orange",
                    )
                )

    def destroy(self):
        for i in self.ids:
            self.canvas.delete(i)
