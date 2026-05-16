from random import random, choice

from settings import ROWS, COLS, EXIT_TILE


def generate_level():
    grid = []

    for y in range(ROWS):
        row = []
        for x in range(COLS):
            if y == 0 or x == 0 or y == ROWS - 1 or x == COLS - 1:
                row.append(1)
            elif x % 2 == 1 and y % 2 == 1:
                row.append(1)
            else:
                row.append(2 if random() < 0.4 else 0)
        grid.append(row)

    grid[1][1] = 0
    grid[1][2] = 0
    grid[2][1] = 0

    free = []
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == 0 and not (x <= 2 and y <= 2):
                free.append((x, y))

    if free:
        ex, ey = choice(free)
        grid[ey][ex] = EXIT_TILE

    return grid
