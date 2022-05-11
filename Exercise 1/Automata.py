from utils import readScenarioFromJSON, readScenarioFromJSONFilePath, visualize

from scipy.sparse import dok_matrix
from numpy import full
import numpy as np
from math import inf

from os.path import isdir, exists

from time import sleep
from IPython.display import clear_output


class Automata:
    def __init__(self, config):
        """Initialize the Automata using as input a path to a JSON file or a dictionary. It creates/saves the following required data structures:
        
        Data structures:
            pedestrians (list): list of pedestrians containing tuples describing pedestrians as (pedestrian id, coordiante x, coordinate y)
            targets (list): list of targets containing tuples describing targets as ([id of pedestrian having this target], coordinate x, coordinate y)
            obstacles (list): list of obstacles containing tuples describing obstacles as (coordinate x, coordinate y)
            paths (dict): dictionary that saves for every pedestrian (pedestrian id as key) the paths as a list of tuples [(x_1 , y_1), (x_2, y_2),  ...]
            achievedTargets (dict): dictionary that saves for every pedestrian (pedestrian id as key) if it has achieved its target
            pedestriansSpeed (dict): dictionary that saves the speed of every pedestrian (pedestrian id as key)
            availableSteps (dict): dictionary that saves the number of available steps (steps (meters) to move forward) for every pedestrian (pedestrian id as key)
            times (dict): dictionary that saves the number of seconds running for every pedestrian (pedestrian id as key)

        Args:
            config (str or dictionary): Path to a JSON file or a dictionary
        """
        if type(config) is dict:
            self.width, self.height, self.pedestrians, self.targets, self.obstacles, self.step = readScenarioFromJSON(config)
        elif isdir(config) and exists(config):
            self.width, self.height, self.pedestrians, self.targets, self.obstacles, self.step = readScenarioFromJSONFilePath(config)
        else:
            raise "The input config is not a valid path nor a JSON/dictionary."

        # Initialize arrays of paths for each pedestrian {pedestrianId: [(x_1 , y_1), (x_2, y_2),  ...]}
        self.paths = {}
        for pedestrian in self.pedestrians:
            self.paths[pedestrian[0]] = [(pedestrian[1], pedestrian[2])]

        # Initialize dictionary of achieved target status for each pedestrian {pedestrianId: True/False}
        self.achievedTargets = {}
        for pedestrian in self.pedestrians:
            self.achievedTargets[pedestrian[0]] = False

        self.pedestriansSpeed = {}
        self.availableSteps = {}
        self.times = {}
        # We only create these structures if we are working with velocity, that is, we have specified for every pedestrian a velocity
        if len(self.pedestrians[0]) == 4:
            for pedestrian in self.pedestrians:
                self.availableSteps[pedestrian[0]] = 0.0
                self.pedestriansSpeed[pedestrian[0]] = pedestrian[3]
                self.times[pedestrian[0]] = 0

    def getDimensions(self):
        """Returns the dimensions of the grid

        Returns:
            integer, integer: Dimensions of the grid
        """
        return self.height, self.width

    def getState(self): 
        """Returns a 2D NumPy ndarray (matrix) with the current state of the grid. The cells with 0 are empty cell, 
        with 1 are pedestrians, with 2 are obstacles and with 3 are targets

        Returns:
            ndarray: NumPy ndarray with the current state of the grid
        """
        grid = dok_matrix((self.height, self.width), dtype=int)

        for pedestrian in self.pedestrians:
            grid[self.height - pedestrian[2] - 1, pedestrian[1]] = 1

        for obstacle in self.obstacles:
            grid[self.height - obstacle[1] - 1, obstacle[0]] = 2

        for target in self.targets:
            grid[self.height - target[2] - 1, target[1]] = 3

        return grid.toarray()

    def getStateWithPaths(self):
        """Returns a 2D NumPy ndarray (matrix) with the current state of the grid as self.getState() method
        but containing also the pedestrians paths (traversed cell positions) until now as 1s in the grid

        Returns:
            ndarray: NumPy ndarray with the current state of the grid and paths
        """
        grid = self.getState()
        for pedestrianId in self.paths:
            for x, y in self.paths[pedestrianId]:
                grid[self.height - y - 1][x] = 1
        return grid

    def getPaths(self): 
        """Returns a dictionary with the paths (traversed cell positions) until now for every pedestrian

        Returns:
            dict: Dictionary with pedestrian ids as key and arrays of cell positions tuples as values
        """
        return self.paths

    def neighbors(self, x, y): 
        """Returns a list of valid neighbors coordinates for the input coordinates (x, y)

        Args:
            x (integer): x coordinate
            y (integer): y coordinate

        Returns:
            list: List of valid 2D integer tuples of coordinates
        """
        neighbors = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x - 1, y), (x + 1, y), (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]

        def validate(coor):
            """For a given coordinate, it checks if it is not outside of the grid

            Args:
                coor ((integer, integer)): Coordinates tuple

            Returns:
                boolean: True if the coordinate it is inside the grid and False otherwise
            """
            if coor[0] < 0 or coor[1] < 0:
                return False
            elif coor[1] >= self.height or coor[0] >= self.width:
                return False
            else:
                return True

        return [neighbor for neighbor in neighbors if validate(neighbor)]

    def euclideanDistance(self, origin, target): 
        """Returns the euclidean distance between an origian and a target cell

        Args:
            origin ((integer, integer)): Coordinates tuple of the origin
            target ((integer, integer)): Coordinates tuple of the target

        Returns:
            float: Euclidean distance
        """
        origin = np.array(origin)
        target = np.array(target)

        return np.linalg.norm(origin - target)

    def isTargetInNeighborhood(self, neighbors, pedestrianId): 
        """Checks for a given pedestrian if its target is in its current neighbors

        Args:
            neighbors (list): List of tuples with the coordinates of the neighbors of the given pedestrian
            pedestrianId (integer): ID of the pedestrian

        Returns:
            boolean, tuple: True boolean if the target is in the neighbors (False otherwise), and tuple with the coordinates of the pedestrian's target
        """
        targetAchieved = False
        targetToBeAchieved = (None, None)
        for target in self.targets:
            if pedestrianId in target[0] and ((target[1], target[2]) in neighbors):
                targetAchieved = True
                break
            elif pedestrianId in target[0] and not ((target[1], target[2]) in neighbors):
                targetToBeAchieved = (target[1], target[2])

        return targetAchieved, targetToBeAchieved

    def getUnreachableCells(self, avoidPedestrians): 
        """Returns a list with the coordinates of the unreachable cells, which can be pedestrians and/or obstacles

        Args:
            avoidPedestrians (boolean): Boolean to enable the pedestrians avoidance

        Returns:
            list: List of coordinates of the unreachable cells
        """
        if (not avoidPedestrians):
            return self.obstacles
        else:
            unreachableCells = [obstacle for obstacle in self.obstacles]
            for pedestrian in self.pedestrians:
                if (not self.achievedTargets[pedestrian[0]]):
                    unreachableCells.append((pedestrian[1], pedestrian[2]))
            return unreachableCells

    def dijkstra(self, target, avoidObstacles, avoidPedestrians): 
        """Dijkstra's algorithm for flooding the grid with the distances from all cells to the target cell.
        If avoidObstacles or avoidPedestrians are setted to True, then the algorithm takes into consideration the avoidance of obstacles and/or pedestrians

        Args:
            target (tuple): Coordiantes of the target cell
            avoidObstacles (boolean): Boolean to enable the obstacles avoidance
            avoidPedestrians (boolean): Boolean to enable the pedestrians avoidance

        Returns:
            ndarray: NumPy 2D ndarray with the distances from all grid cells to the target
        """
        # Initialize distances grid with large values
        distances = full((self.height, self.width), inf)

        # Set target cell to 0
        distances[target[1], target[0]] = 0

        # Visited cells
        visited = set()

        while True:
            currentCell = None
            currentMinDist = inf
            for x in range(self.width):
                for y in range(self.height):
                    if (x, y) not in visited and distances[y][x] < currentMinDist:
                        currentCell = (x, y)
                        currentMinDist = distances[y][x]

            if currentCell is None:
                break
            
            visited.add(currentCell)
            for neighbor in self.neighbors(currentCell[0], currentCell[1]):
                if neighbor not in self.getUnreachableCells(avoidPedestrians) or not avoidObstacles:
                    newDistance = distances[currentCell[1], currentCell[0]] + self.euclideanDistance(neighbor, currentCell)
                    if newDistance < distances[neighbor[1], neighbor[0]]:
                        distances[neighbor[1]][neighbor[0]] = newDistance

        return distances

    # -------------------------- BASIC (Euclidean Distance + steps) & COMPLEX (Cost Function + steps) AUTOMATAS --------------------------

    def basicOperator(self, _, avoidPedestrians): 
        """Applies the basic operator to the current automata state. This operator uses the euclidean distance to compute the next state of the automata (cells occupied by the 
        pedestrians in the next step) and allows for pedestrian avoidance

        Args:
            _ (_): Argument added for consistence with other operators and the simulate() method. Not used.
            avoidPedestrians (boolean): Boolean to enable the pedestrians avoidance
        """
        for index, pedestrian in enumerate(self.pedestrians):
            pedestrianId = pedestrian[0]

            neighbors = self.neighbors(pedestrian[1], pedestrian[2])

            targetAchieved, targetToBeAchieved = self.isTargetInNeighborhood(neighbors, pedestrianId)

            if targetAchieved:
                # Target archieved, then the pedestrian remains in the same cell and set its achieved target status to True
                self.achievedTargets[pedestrianId] = True
            else:
                # Compute the distance from all neighbors in the neighborhood to the target, save the minimum distance
                if neighbors == self.getUnreachableCells(avoidPedestrians):
                    self.achievedTargets[pedestrianId] = False
                    break

                neighborWithMinDist = (0, 0)
                minDist = np.inf
                for neighbor in neighbors:
                    dist = self.euclideanDistance(neighbor, targetToBeAchieved)
                    if dist < minDist and not neighbor in self.getUnreachableCells(avoidPedestrians):
                        neighborWithMinDist = (neighbor[0], neighbor[1])
                        minDist = dist

                # Change the cell not occupied by the pedestrian
                self.pedestrians[index] = (pedestrianId, neighborWithMinDist[0], neighborWithMinDist[1])

                # Save the current cell in the path
                self.paths[pedestrianId].append((self.pedestrians[index][1], self.pedestrians[index][2]))

    def operatorWithCostFunction(self, avoidObstacles, avoidPedestrians): 
        """Applies the complex operator to the current automata state. This operator uses a cost function (grid flooded with distances by dijkstra's algorithm) to compute the next state of the automata (cells occupied by the 
        pedestrians in the next step) and allows for pedestrians and/or obstacles avoidance 

        Args:
            avoidObstacles (boolean): Boolean to enable the obstacles avoidance
            avoidPedestrians (boolean): Boolean to enable the pedestrians avoidance
        """
        # If all the pedestrians have the same target we can compute just once the distance matrix
        if len(self.targets) == 1:
            distanceGrid = self.dijkstra((self.targets[0][1], self.targets[0][2]), avoidObstacles, avoidPedestrians)
        
        for index, pedestrian in enumerate(self.pedestrians):
            pedestrianId = pedestrian[0]

            neighbors = self.neighbors(pedestrian[1], pedestrian[2])

            targetAchieved, targetToBeAchieved = self.isTargetInNeighborhood(neighbors, pedestrianId)

            if targetAchieved:
                # Target archieved, then the pedestrian remains in the same cell and set its achieved target status to True
                self.achievedTargets[pedestrianId] = True
            else:
                # If the pedestrians have different targets we need to compute the distance matrix for every pedestrian
                if len(self.targets) > 1:
                    distanceGrid = self.dijkstra(targetToBeAchieved, avoidObstacles, avoidPedestrians)

                neighborWithMinDist = None
                minDist = np.inf
                for neighbor in neighbors:
                    dist = distanceGrid[neighbor[1]][neighbor[0]]
                    if dist < minDist and neighbor not in self.getUnreachableCells(avoidPedestrians):
                        neighborWithMinDist = (neighbor[0], neighbor[1])
                        minDist = dist

                if neighborWithMinDist is None:
                    continue

                # Change the cell not occupied by the pedestrian
                self.pedestrians[index] = (pedestrianId, neighborWithMinDist[0], neighborWithMinDist[1])

                # Save the current cell in the path
                self.paths[pedestrianId].append((self.pedestrians[index][1], self.pedestrians[index][2]))

    def simulate(self, operator, nSteps, avoidObstacles=True, avoidPedestrians=True): 
        """Simulates for nSteps number of steps using a given operator

        Args:
            operator (function): Operator method to be used
            nSteps (integer): Number of steps to perform
            avoidObstacles (bool, optional): Boolean to enable the obstacles avoidance. Defaults to True.
            avoidPedestrians (bool, optional): Boolean to enable the pedestrians avoidance. Defaults to True.
        """
        for step in range(nSteps):
            operator(avoidObstacles, avoidPedestrians)

            if all(list(self.achievedTargets.values())):
                print("Simulation finished after {} steps. All pedestrians achieved their targets.".format(step + 1))
                break

    def simulateAndVisualize(self, operator, nSteps, avoidObstacles=True, avoidPedestrians=True, size=(12,12)): 
        """Simulates for nSteps number of steps using a given operator and prints (and updates) a visualization for every step

        Args:
            operator (function): Operator method to be used
            nSteps (integer): Number of steps to perform
            avoidObstacles (bool, optional): Boolean to enable the obstacles avoidance. Defaults to True.
            avoidPedestrians (bool, optional): Boolean to enable the pedestrians avoidance. Defaults to True.
            size (tuple, optional): Size of the output. Defaults to (12, 12).
        """
        for step in range(nSteps):
            operator(avoidObstacles, avoidPedestrians)

            clear_output(wait=True)
            visualize(self.getState(), size)
            sleep(0.2)

            if all(list(self.achievedTargets.values())):
                print("Simulation finished after {} steps. All pedestrians achieved their targets.".format(step + 1))
                break

    # -------------------------- RiMEA AUTOMATA (Cost function + time) --------------------------

    def hasStepsAvailable(self, pedestrianId): 
        """Returns True if the given pedestrian has steps (meters) to move forward, False otherwise

        Args:
            pedestrianId (integer): ID of the pedestrian

        Returns:
            boolean: True if the pedestrian has steps, False otherwise
        """
        if (self.availableSteps[pedestrianId] >= self.step):
            self.availableSteps[pedestrianId] = self.availableSteps[pedestrianId] - self.step
            return True
        return False

    def someoneCanMove(self): 
        """Returns True if some pedestrian has steps (meters) to move forward, False otherwise

        Returns:
            boolean: True if some pedestrian has steps, False otherwise
        """
        for i, step in enumerate(self.availableSteps):
            if (self.availableSteps[i+1] >= self.step):
                return True
        return False

    def updateAvailableSteps(self): 
        """Update the available steps for every pedestrian
        """
        for i, steps in enumerate(self.availableSteps):
            self.availableSteps[i+1] = self.availableSteps[i+1] + self.pedestriansSpeed[i+1]

    def tikTak(self): 
        """Updates the running time of each pedestrian
        """
        for pedestrian in self.pedestrians:
            if (not self.achievedTargets[pedestrian[0]]):
                self.times[pedestrian[0]] += 1

    def operatorWithCostFunctionRiMEA(self, avoidObstacles, avoidPedestrians): 
        """Applies the complex operator to the current automata state. This operator uses a cost function (grid flooded with distances by dijkstra's algorithm) to compute the next state of the automata (cells occupied by the 
    pedestrians in the next step) and allows for pedestrians and/or obstacles avoidance. Works like operatorWithCostFunction, but instead of steps and cells, this operator considers velocities, times and meters

        Args:
            avoidObstacles (boolean): Boolean to enable the obstacles avoidance
            avoidPedestrians (boolean): Boolean to enable the pedestrians avoidance
        """
        # If all the pedestrians have the same target we can compute just once the distance matrix
        if len(self.targets) == 1:
            distanceGrid = self.dijkstra((self.targets[0][1], self.targets[0][2]), avoidObstacles, avoidPedestrians)

        for index, pedestrian in enumerate(self.pedestrians):
            # If the pedestrian has no step available or has achieved its target, then we have nothing to do
            if (not self.hasStepsAvailable(pedestrian[0]) or self.achievedTargets[pedestrian[0]]):
                continue

            pedestrianId = pedestrian[0]

            neighbors = self.neighbors(pedestrian[1], pedestrian[2])

            targetAchieved, targetToBeAchieved = self.isTargetInNeighborhood(neighbors, pedestrianId)

            if targetAchieved:
                # Target archieved, then the pedestrian is absorbed by the target and sets its achieved target status to True
                self.achievedTargets[pedestrianId] = True
                for target in self.targets:
                    if pedestrianId in target[0]:
                        self.pedestrians[index] = (pedestrianId, target[1], target[2])
            else:
                # If the pedestrians have different targets we need to compute the distance matrix for every pedestrian
                if len(self.targets) > 1:
                    distanceGrid = self.dijkstra(targetToBeAchieved, avoidObstacles, avoidPedestrians)

                neighborWithMinDist = None
                minDist = np.inf
                for neighbor in neighbors:
                    dist = distanceGrid[neighbor[1]][neighbor[0]]
                    if dist < minDist and neighbor not in self.getUnreachableCells(avoidPedestrians):
                        neighborWithMinDist = (neighbor[0], neighbor[1])
                        minDist = dist

                if neighborWithMinDist is None:
                    continue

                # Change the cell not occupied by the pedestrian
                self.pedestrians[index] = (pedestrianId, neighborWithMinDist[0], neighborWithMinDist[1])

                # Save the current cell in the path
                self.paths[pedestrianId].append((self.pedestrians[index][1], self.pedestrians[index][2]))

    def simulateWithTime(self, operator, seconds, avoidObstacles=True, avoidPedestrians=True): 
        """Simulates for the given number of seconds using a given operator

        Args:
            operator (function): Operator method to be used
            nSteps (integer): Number of steps to perform
            avoidObstacles (bool, optional): Boolean to enable the obstacles avoidance. Defaults to True.
            avoidPedestrians (bool, optional): Boolean to enable the pedestrians avoidance. Defaults to True.
        """
        for i in range(seconds):
            if all(list(self.achievedTargets.values())):
                print("Simulation finished after {} seconds. All pedestrians achieved their targets.".format(i + 1))
                break

            # Update available steps because 1 second has passed
            self.updateAvailableSteps()

            while (self.someoneCanMove()):
                operator(avoidObstacles, avoidPedestrians)

            self.tikTak()

        print("Simulation finished after {} seconds.".format(i + 1))

    def simulateAndVisualizeWithTime(self, operator, seconds, avoidObstacles=True, avoidPedestrians=True, size=(12,12)): 
        """Simulates for the given number of second using a given operator and prints (and updates) a visualization for every step

        Args:
            operator (function): Operator method to be used
            nSteps (integer): Number of steps to perform
            avoidObstacles (bool, optional): Boolean to enable the obstacles avoidance. Defaults to True.
            avoidPedestrians (bool, optional): Boolean to enable the pedestrians avoidance. Defaults to True.
            size (tuple, optional): Size of the output. Defaults to (12, 12).
        """
        for i in range(seconds):
            if all(list(self.achievedTargets.values())):
                print(
                    "Simulation finished after {} seconds. All pedestrians achieved their targets.".format(i + 1))
                return

            # Update available steps because 1 second has passed
            self.updateAvailableSteps()

            while (self.someoneCanMove()):
                operator(avoidObstacles, avoidPedestrians)

                clear_output(wait=True)
                visualize(self.getState(), size)
                sleep(0.1)

            self.tikTak()

        print("Simulation finished after {} seconds.".format(i + 1))
