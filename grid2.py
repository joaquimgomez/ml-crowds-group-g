import numpy as np
import pygame
import sys
import random
from numpy.random import choice

# Colors for cells

BLACK = (0, 0, 0)
WHITE = (255, 255, 255) # Empty Cell
RED = (255, 0, 0) # Pedestrian
BLUE = (0, 0, 255) # Obstacle
YELLOW = (255, 255, 0) # Target

# Screensize, can be changed
size = (width, height) = (600, 600)

# Pygame initialization
pygame.init()

# Setting screensize and clock
win = pygame.display.set_mode(size)
clock = pygame.time.Clock()

# Scale the grids with some constant value for clear interpretation
scale = 20
rows, cols = int(win.get_height() / scale), int(win.get_width() / scale)

grid = []

# Randomly assign every cell one of 4 values : 0: empty, 1: ped, 2:obstacle, 3:target
# TODO : We must not to do it on a probabilistic way.
l = [0] * 95 + [1] * 1 + [2] * 1 + [3] * 1

for i in range(rows):
    arr = []
    for j in range(cols):
        arr.append(random.choice(l))
    grid.append(arr)

# Finding the neighbors for each cell both counts and neighbors itself.
def count(grid, x, y):
    c = 0
    neighbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            col = (y + j + cols) % cols
            row = (x + i + rows) % rows
            c += grid[row][col]
            neighbors.append(grid[row][col])
    c -= grid[x][y]

    return c, neighbors


# Screen Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    win.fill(WHITE)

    # Fill with colors.
    for i in range(rows):
        for j in range(cols):
            x = i * scale
            y = j * scale
            if grid[i][j] == 0:
                pygame.draw.rect(win, WHITE, (x, y, scale, scale))
            elif grid[i][j] == 1:
                pygame.draw.rect(win, RED, (x, y, scale, scale))
            elif grid[i][j] == 2:
                pygame.draw.rect(win, BLUE, (x, y, scale, scale))
            else:
                pygame.draw.rect(win, YELLOW, (x, y, scale, scale))

            pygame.draw.line(win, BLACK, (x, y), (x, height))
            pygame.draw.line(win, BLACK, (x, y), (width, y))

    new_grid = []
    for i in range(rows):
        arr = []
        for j in range(cols):
            arr.append(0)
        new_grid.append(arr)

    for i in range(cols):
        for j in range(rows):
            if grid[i][j] == 1: # If cell has a pedestrian
                number, neighbors = count(grid, j, i) # Compute its neighbors
                state = grid[i][j] # save the grid's state

            #  TODO : If any of the neighbors is in T state return it unchanged,
            #  otherwise compute its distance from all its neighbors.

            """
            Game of Life Ruleset, may be similar to ours
            if state == 0 and neighbors == 3:
                new_grid[i][j] = 1
            elif state == 1 and (neighbors < 2 or neighbors > 3):
                new_grid[i][j] = 0
            else:
                new_grid[i][j] = state"""
    grid = new_grid

    pygame.display.update()
    clock.tick(10)
    pygame.display.flip()
