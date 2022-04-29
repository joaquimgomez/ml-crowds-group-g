"""
    new_grid = []
    for i in range(rows):
        arr = []
        for j in range(cols):
            arr.append(0)
        new_grid.append(arr)

    for i in range(cols):
        for j in range(rows):
            neighbors = count(grid, j, i)
            state = grid[j][i]
            if state == 0 and neighbors == 3:
                new_grid[j][i] = 1
            elif state == 1 and (neighbors < 2 or neighbors > 3):
                new_grid[j][i] = 0
            else:
                new_grid[j][i] = state
    grid = new_grid

    pygame.display.flip()
"""
