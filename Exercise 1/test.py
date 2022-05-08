from Automata import Automata
from utils import visualize
import math



import sys
import numpy as np

np.set_printoptions(threshold=sys.maxsize)

pedestrians = []
id = 0
for i in range(1, 10):
    for j in range(2, 19):
        pedestrians.append([id, i, j])
        id = id + 1
        if id == 150:
            break

configTask41 = {
    "name": "Task1Scenario",
    "dimensions": {
        "width": 71,
        "height": 22
    },
    "pedestrians": pedestrians,
    "targets": [
        [[i for i in range(0, 150)], 65, 10],
    ],
    "obstacles": [[20, i] for i in range(0, 22) if not i == 10 and not i == 11] + \
                 [[i, 9] for i in range(21, 30)] + \
                 [[i, 12] for i in range(21, 30)] + \
                 [[30, i] for i in range(0, 22) if not i == 10 and not i == 11] + \
                 [[51, i] for i in range(0, 22) if not i == 10 and not i == 11]

}
print(configTask41)
task41Automata = Automata(configTask41)
visualize(task41Automata.getState())
print(np.around(task41Automata.dijkstra((65, 10), avoidObstacles = True, avoidPedestrians = True), decimals=2))