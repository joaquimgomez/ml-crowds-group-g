import json

from matplotlib import pyplot as plt
from matplotlib import colors
import numpy as np

typeToId = {
    "E": 0,
    "P": 1,
    "O": 2,
    "T": 3
}

idToType = {
    0: "E",
    1: "P",
    2: "O",
    3: "T" 
}

def readScenarioFromJSONFilePath(jsonFilePath):
    """
    Reads a scenario from a JSON file.
    """
    with open(jsonFilePath) as json_file:
        try:
            scenarioDescription = json.load(json_file)
        except ValueError as e:
            print("This is not a valid JSON file.")
            return None

    width = scenarioDescription["dimensions"]['width']
    height = scenarioDescription["dimensions"]['height']

    # Convert arrays of arrays to arrays of tuples for a better accessions of type "tuple IN list of tuples"
    pedestrians = []
    for pedestrian in scenarioDescription["pedestrians"]:
        if len(pedestrian) == 3:
            pedestrians.append((pedestrian[0], pedestrian[1], pedestrian[2]))
        elif len(pedestrian) == 4:
            pedestrians.append((pedestrian[0], pedestrian[1], pedestrian[2], pedestrian[3]))

    
    obstacles = []
    for obstacle in scenarioDescription["obstacles"]:
        obstacles.append((obstacle[0], obstacle[1]))

    targets = []
    for target in scenarioDescription["targets"]:
        targets.append((target[0], target[1], target[2]))

    return width, height, pedestrians, targets, obstacles


def readScenarioFromJSON(jsonFile):
    """
    Reads a scenario from a JSON file.
    """

    scenarioDescription = jsonFile

    width = scenarioDescription["dimensions"]['width']
    height = scenarioDescription["dimensions"]['height']

    # Convert arrays of arrays to arrays of tuples for a better accessions of type "tuple IN list of tuples"
    pedestrians = []
    for pedestrian in scenarioDescription["pedestrians"]:
        if len(pedestrian) == 3:
            pedestrians.append((pedestrian[0], pedestrian[1], pedestrian[2]))
        elif len(pedestrian) == 4:
            pedestrians.append((pedestrian[0], pedestrian[1], pedestrian[2], pedestrian[3]))

    obstacles = []
    for obstacle in scenarioDescription["obstacles"]:
        obstacles.append((obstacle[0], obstacle[1]))

    targets = []
    for target in scenarioDescription["targets"]:
        targets.append((target[0], target[1], target[2]))

    return width, height, pedestrians, targets, obstacles

def visualize(state, size = (12, 12)):
    cmap = colors.ListedColormap(['white', 'purple', 'black', 'blue'])
    plt.figure(figsize=size)
    plt.pcolor(state[::-1], cmap=cmap, edgecolors='k', linewidths=1)
    plt.show()
