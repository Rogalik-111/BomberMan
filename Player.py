from settings import TILE, PLAYER_LIVES, EXIT_TILE
from sprites import get_sprite


class Player:
    def __init__(self, canvas, x=1, y=1, lives=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        if lives is None:
            self.lives = PLAYER_LIVES
        else:
            self.lives = lives

        self.image = get_sprite("Player")

        if self.image is not None:
            self.id = canvas.create_image(
                self.x * TILE + TILE // 2,
                self.y * TILE + TILE // 2,
                image=self.image,
                anchor="center",
            )
        else:
            self.id = canvas.create_rectangle(
                self.x * TILE,
                self.y * TILE,
                self.x * TILE + TILE - 10,
                self.y * TILE + TILE - 10,
                fill="blue",
            )

    def _move_draw(self):
        if self.image is not None:
            self.canvas.coords(
                self.id,
                self.x * TILE + TILE // 2,
                self.y * TILE + TILE // 2,
            )
        else:
            self.canvas.coords(
                self.id,
                self.x * TILE,
                self.y * TILE,
                self.x * TILE + TILE - 10,
                self.y * TILE + TILE - 10,
            )

    def move(self, dx, dy, level):
        new_x = self.x + dx
        new_y = self.y + dy

        if level[new_y][new_x] in (0, EXIT_TILE):
            self.x = new_x
            self.y = new_y
            self._move_draw()

    def hit(self):
        self.lives -= 1

    def reset_position(self):
        self.x = 1
        self.y = 1
        self._move_draw()
