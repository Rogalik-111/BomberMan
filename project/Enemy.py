import random

from settings import TILE
from sprites import get_sprite, get_enemy_face_images


class Enemy:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.facing_right = False

        master = canvas.winfo_toplevel()
        self.face_left, self.face_right = get_enemy_face_images(master)
        self.fallback = get_sprite("Enemy")
        if self.face_left is not None:
            self.image = self.face_left
        else:
            self.image = self.fallback

        if self.image is not None:
            self.id = canvas.create_image(
                x * TILE + TILE // 2,
                y * TILE + TILE // 2,
                image=self.image,
                anchor="center",
            )
        else:
            self.image = None
            self.id = canvas.create_rectangle(
                x * TILE,
                y * TILE,
                x * TILE + TILE - 10,
                y * TILE + TILE - 10,
                fill="red",
            )

    def current_sprite(self):
        if self.face_left is not None and self.face_right is not None:
            return self.face_right if self.facing_right else self.face_left
        return self.fallback

    def update_sprite(self):
        if self.image is None:
            return
        img = self.current_sprite()
        if img is not None:
            self.image = img
            self.canvas.itemconfig(self.id, image=self.image)

    def move_draw(self):
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

    def move(self, level):
        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        if level[self.y + dy][self.x + dx] == 0:
            self.x += dx
            self.y += dy
            if dx < 0:
                self.facing_right = False
            elif dx > 0:
                self.facing_right = True
            self.update_sprite()
            self.move_draw()

    def destroy(self):
        self.canvas.delete(self.id)
