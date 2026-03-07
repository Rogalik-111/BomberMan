from settings import ROWS, COLS

def generate_level():
    level = []

    for y in range(ROWS):
        row = []
        for x in range(COLS):

            if y == 0 or x == 0 or y == ROWS-1 or x == COLS-1:
                row.append(1)
            elif x % 2 == 1 and y % 2 == 1:
                row.append(1)
            else:
                from random import random
                row.append(2 if random() < 0.4 else 0)

        level.append(row)

    level[1][1] = 0
    level[1][2] = 0
    level[2][1] = 0
    return level