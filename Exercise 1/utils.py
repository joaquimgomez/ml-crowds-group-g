import json

from matplotlib import pyplot as plt
from matplotlib import colors


def readScenarioFromJSONFilePath(jsonFilePath):
    """Reads a scenario from a JSON file and returns the its elements as expected by the Automata class

    Args:
        jsonFilePath (string): Path to the JSON scenario configuration file

    Returns:
        int, int, list, list, list, int: Returns width, height, pedestrians, targets, obstacles and step as expected by the Automata class
    """
    with open(jsonFilePath) as json_file:
        try:
            scenarioDescription = json.load(json_file)
        except ValueError as e:
            print("This is not a valid JSON file.")
            return None

    width = scenarioDescription["dimensions"]['width']
    height = scenarioDescription["dimensions"]['height']

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

    step = None
    if "step" in scenarioDescription:
        step = scenarioDescription["step"]

    return width, height, pedestrians, targets, obstacles, step

def readScenarioFromJSON(jsonFile):
    """Reads a scenario from a dictionary and returns the its elements as expected by the Automata class

    Args:
        jsonFile (dictionary): Dictionary containing the config of the scenario

    Returns:
        int, int, list, list, list, int: Returns width, height, pedestrians, targets, obstacles and step as expected by the Automata class
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

    step = None
    if "step" in scenarioDescription:
        step = scenarioDescription["step"]

    return width, height, pedestrians, targets, obstacles, step

def visualize(state, size = (12, 12)):
    """Shows the given matrix using matplotlib. Empty cells are white, pedestrians are purple, obstacles are black and targets are blue

    Args:
        state (ndarray): NumPy ndarray with the current state (with or without path) of the grid
        size (tuple, optional): Size for the matplotlib visualization. Defaults to (12, 12).
    """
    cmap = colors.ListedColormap(['white', 'purple', 'black', 'blue'])
    plt.figure(figsize=size)
    plt.pcolor(state[::-1], cmap=cmap, edgecolors='k', linewidths=1)
    plt.show()
