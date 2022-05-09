from Automata import Automata
from utils import visualize
import math

ob = []
for i in range(0, 20):
    ob.append([i, 4])

for i in range(4, 24):
    ob.append([19, i])

ped = []
id = 1
for i in range(0, 10, 2):
    ped.append([id, i, 0, 0.5])
    id += 1

for i in range(0, 10, 2):
    ped.append([id, i, 2, 0.5])
    id += 1

for i in range(1, 10, 2):
    ped.append([id, i, 1, 0.5])
    id += 1

for i in range(1, 11, 2):
    ped.append([id, i, 3, 0.5])
    id += 1
    if (id == 21):
        break

print(len(ped))

rimea1 = {
    "name": "Task1Scenario",
    "dimensions": {
        "width": 24,
        "height": 24  # 1 cell = 0.4 meter ===> 2 m wide = (0.4m/cell)/2m =
    },
    "pedestrians": ped,
    "targets": [
        [[1], 21, 23]
    ],
    "obstacles": ob,

    "step": 0.5
}
rimea1Automata = Automata(rimea1)

# visualize(rimea1Automata.getState(), size = (15,15))
rimea1Automata.simulateAndVisualize2(rimea1Automata.operatorWithCostFunction_Angelos, 60, size=(15, 15))