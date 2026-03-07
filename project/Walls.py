from settings import TILE
class Wall:
    def __init__(self, canvas, x, y, destructible):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.destructible = destructible

        color = "gray" if not destructible else "brown"
        self.id = canvas.create_rectangle(
            x, y, x+TILE, y+TILE, fill=color
        )

    def destroy(self):
        self.canvas.delete(self.id)