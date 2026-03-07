from settings import TILE, WIDTH, HEIGHT

def draw_grid(canvas):
    for x in range(0, WIDTH, TILE):
        canvas.create_line(x, 0, x, HEIGHT, fill="#333")
    for y in range(0, HEIGHT, TILE):
        canvas.create_line(0, y, WIDTH, y, fill="#333")