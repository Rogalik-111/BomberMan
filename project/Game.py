from settings import *
from Level import generate_level
from Walls import Wall
from Player import Player
from Enemy import Enemy
from Bomb import Bomb
from Explosion import Explosion
import random

class Game:
    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas
        self.level = generate_level()

        self.walls = {}
        self.create_map()

        self.player = Player(canvas)
        self.enemies = [Enemy(canvas, COLS-2, ROWS-2)]
        self.bombs = []

        root.bind("<Key>", self.key_press)

        self.loop()

    def create_map(self):
        for y in range(ROWS):
            for x in range(COLS):
                if self.level[y][x] == 1:
                    self.walls[(x,y)] = Wall(self.canvas, x*TILE, y*TILE, False)
                elif self.level[y][x] == 2:
                    self.walls[(x,y)] = Wall(self.canvas, x*TILE, y*TILE, True)

    def key_press(self, e):
        if e.keysym == "Left":
            self.player.move(-1,0,self.level)
        if e.keysym == "Right":
            self.player.move(1,0,self.level)
        if e.keysym == "Up":
            self.player.move(0,-1,self.level)
        if e.keysym == "Down":
            self.player.move(0,1,self.level)
        if e.keysym == "space":
            self.place_bomb()

    def place_bomb(self):
        if len(self.bombs) >= MAX_BOMBS:
            return
        bomb = Bomb(self.player.x, self.player.y)
        self.bombs.append(bomb)
        self.root.after(BOMB_DELAY, lambda: self.explode(bomb))

    def explode(self, bomb):
        tiles = [(bomb.x, bomb.y)]

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            for i in range(1, RADIUS+1):
                nx = bomb.x + dx*i
                ny = bomb.y + dy*i

                if self.level[ny][nx] == 1:
                    break

                tiles.append((nx,ny))

                if self.level[ny][nx] == 2:
                    break

        explosion = Explosion(self.canvas, tiles)

        for x,y in tiles:
            if self.level[y][x] == 2:
                self.level[y][x] = 0
                self.walls[(x,y)].destroy()

            if self.player.x == x and self.player.y == y:
                self.player.hit()

            for enemy in self.enemies[:]:
                if enemy.x == x and enemy.y == y:
                    enemy.destroy()
                    self.enemies.remove(enemy)

        self.root.after(EXPLOSION_TIME, explosion.destroy)
        self.bombs.remove(bomb)

    def loop(self):
        for enemy in self.enemies:
            enemy.move(self.level)

            if enemy.x == self.player.x and enemy.y == self.player.y:
                self.player.hit()

        self.root.after(500, self.loop)