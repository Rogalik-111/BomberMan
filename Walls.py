from settings import TILE
from sprites import get_sprite


class Wall:
    def __init__(self, canvas, pixel_x, pixel_y, destructible):
        self.canvas = canvas
        self.destructible = destructible

        name = "BreakableWall" if destructible else "Wall"
        img = get_sprite(name)
        self.image = img

        if img is not None:
            self.id = canvas.create_image(
                pixel_x + TILE // 2,
                pixel_y + TILE // 2,
                image=img,
                anchor="center",
            )
        else:
            color = "brown" if destructible else "gray"
            self.id = canvas.create_rectangle(
                pixel_x,
                pixel_y,
                pixel_x + TILE,
                pixel_y + TILE,
                fill=color,
            )

    def destroy(self):
        self.canvas.delete(self.id)
