import random
from settings import TILE

class Enemy:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y

        self.id = canvas.create_rectangle(
            x*TILE, y*TILE,
            x*TILE+TILE-10, y*TILE+TILE-10,
            fill="red"
        )

    def move(self, level):
        dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

        if level[self.y+dy][self.x+dx] == 0:
            self.x += dx
            self.y += dy
            self.canvas.coords(
                self.id,
                self.x*TILE, self.y*TILE,
                self.x*TILE+TILE-10,
                self.y*TILE+TILE-10
            )

    def destroy(self):
        self.canvas.delete(self.id)