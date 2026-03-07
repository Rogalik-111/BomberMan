from settings import TILE, PLAYER_LIVES

class Player:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = 1
        self.y = 1
        self.lives = PLAYER_LIVES

        self.id = canvas.create_rectangle(
            self.x*TILE, self.y*TILE,
            self.x*TILE+TILE-10, self.y*TILE+TILE-10,
            fill="blue"
        )

    def move(self, dx, dy, level):
        new_x = self.x + dx
        new_y = self.y + dy

        if level[new_y][new_x] == 0:
            self.x = new_x
            self.y = new_y
            self.canvas.coords(
                self.id,
                self.x*TILE, self.y*TILE,
                self.x*TILE+TILE-10,
                self.y*TILE+TILE-10
            )

    def hit(self):
        self.lives -= 1