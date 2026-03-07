from settings import TILE

class Explosion:
    def __init__(self, canvas, tiles):
        self.canvas = canvas
        self.ids = []

        for x, y in tiles:
            self.ids.append(
                canvas.create_rectangle(
                    x*TILE, y*TILE,
                    x*TILE+TILE, y*TILE+TILE,
                    fill="orange"
                )
            )

    def destroy(self):
        for i in self.ids:
            self.canvas.delete(i)