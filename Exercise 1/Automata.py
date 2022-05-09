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

        if type(config) is dict:
            self.width, self.height, self.pedestrians, self.targets, self.obstacles, self.step = readScenarioFromJSON(config)
        elif isdir(config) and exists(config):
            self.width, self.height, self.pedestrians, self.targets, self.obstacles, self.step = readScenarioFromJSONFilePath(
                config)
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
        # self.pedestriansWaitingSteps = {}
        if len(self.pedestrians[0]) == 4:
            for pedestrian in self.pedestrians:
                self.availableSteps[pedestrian[0]] = 0.0
                self.pedestriansSpeed[pedestrian[0]] = pedestrian[3]

        self.end = False

    def getDimensions(self):  # OK
        return self.width, self.height

    def getState(self):  # OK
        grid = dok_matrix((self.height, self.width), dtype=int)

        # TODO: Here maybe instead of 1, we put the pedestrianId => Then we should avoid color for obstacles and targets
        for pedestrian in self.pedestrians:
            grid[self.height - pedestrian[2] - 1, pedestrian[1]] = 1

        for obstacle in self.obstacles:
            grid[self.height - obstacle[1] - 1, obstacle[0]] = 2

        for target in self.targets:
            grid[self.height - target[2] - 1, target[1]] = 3

        return grid.toarray()

    def getStateWithPaths(self):  # OK
        grid = self.getState()
        for pedestrianId in self.paths:
            for x, y in self.paths[pedestrianId]:
                grid[self.height - y - 1][x] = 1
        return grid

    def getPaths(self):  # OK
        return self.paths

    def neighbors(self, x, y):  # OK

        neighbors = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x - 1, y), (x + 1, y), (x - 1, y + 1), (x, y + 1),
                     (x + 1, y + 1)]

        # Checker for a neighbor is not outside of the grid, only selects proper neighbors.
        def validate(coor):
            if coor[0] < 0 or coor[1] < 0:
                return False
            elif coor[1] >= self.height or coor[0] >= self.width:
                return False
            else:
                return True

        return [neighbor for neighbor in neighbors if validate(neighbor)]

    def euclidianDistance(self, neighbor, target):  # OK
        neighbor = np.array(neighbor)
        target = np.array(target)

        return np.linalg.norm(neighbor - target)

    def isTargetInNeighborhood(self, neighbors, pedestrianId):  # OK
        # Check if the target is in the neighborhood
        targetAchieved = False
        targetToBeAchieved = (None, None)
        for target in self.targets:
            if pedestrianId in target[0] and ((target[1], target[2]) in neighbors):
                targetAchieved = True
                break
            elif pedestrianId in target[0] and not ((target[1], target[2]) in neighbors):
                targetToBeAchieved = (target[1], target[2])

        return targetAchieved, targetToBeAchieved

    def getUnreachableCells(self, avoidPedestrians):  # OK
        if (not avoidPedestrians):
            return self.obstacles
        else:
            unreachableCells = [obstacle for obstacle in self.obstacles]
            for pedestrian in self.pedestrians:
                if (not self.achievedTargets[pedestrian[0]]):
                    unreachableCells.append((pedestrian[1], pedestrian[2]))
            return unreachableCells

    # Dijkstra's algorithm with a target cell in a grid
    def dijkstra(self, target, avoidObstacles, avoidPedestrians):
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
                    newDistance = distances[currentCell[1], currentCell[0]] + self.euclidianDistance(neighbor,
                                                                                                     currentCell)  # 1?
                    if newDistance < distances[neighbor[1], neighbor[0]]:
                        distances[neighbor[1]][neighbor[0]] = newDistance

        return distances

    def canGoToTheNextCell(self, pedestrianId):
        if len(self.pedestriansSpeed) > 0 and len(self.pedestriansWaitingSteps) > 0:
            if self.pedestriansWaitingSteps[pedestrianId] >= self.pedestriansSpeed[pedestrianId]:
                self.pedestriansWaitingSteps[pedestrianId] = 0
                
                # Update speed ?

                return True
            return False
        return True

    def operatorWithCostFunction(self, avoidObstacles, avoidPedestrians):
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
                if self.canGoToTheNextCell(pedestrianId):
                    if len(self.targets) > 1:
                        distanceGrid = self.dijkstra(targetToBeAchieved, avoidObstacles, avoidPedestrians)

                    neighborWithMinDist = (0, 0)
                    minDist = np.inf  # same as inf, need to be concise with np.float64.
                    for neighbor in neighbors:
                        dist = distanceGrid[neighbor[1]][neighbor[0]]
                        if dist < minDist and neighbor not in self.getUnreachableCells(avoidPedestrians):
                            neighborWithMinDist = (neighbor[0], neighbor[1])
                            minDist = dist
                    
                    # Change the cell not occupied by the pedestrian
                    self.pedestrians[index] = (pedestrianId, neighborWithMinDist[0], neighborWithMinDist[1])

                    # Save the current cell in the path
                    self.paths[pedestrianId].append((self.pedestrians[index][1], self.pedestrians[index][2]))
                else:
                    self.pedestriansWaitingSteps[pedestrianId] += 1




    def hasStepsAvailable(self, pedestrianId):
        if (self.availableSteps[pedestrianId] >= self.step):
            self.availableSteps[pedestrianId] = self.availableSteps[pedestrianId] - self.step
            return True
        return False

    def operatorWithCostFunction_Angelos(self, avoidObstacles, avoidPedestrians):

        if len(self.targets) == 1:
            distanceGrid = self.dijkstra((self.targets[0][1], self.targets[0][2]), avoidObstacles, avoidPedestrians)

        for index, pedestrian in enumerate(self.pedestrians):

            if (not self.hasStepsAvailable(pedestrian[0]) or self.achievedTargets[pedestrian[0]]):
                continue

            pedestrianId = pedestrian[0]

            neighbors = self.neighbors(pedestrian[1], pedestrian[2])

            targetAchieved, targetToBeAchieved = self.isTargetInNeighborhood(neighbors, pedestrianId)

            if targetAchieved:
                # Target archieved, then the pedestrian remains in the same cell and set its achieved target status to True
                self.achievedTargets[pedestrianId] = True
                for target in self.targets:
                    if pedestrianId in target[0]:
                        self.pedestrians[index] = (pedestrianId, target[1], target[2])

            else:
                if len(self.targets) > 1:
                    distanceGrid = self.dijkstra(targetToBeAchieved, avoidObstacles, avoidPedestrians)

                neighborWithMinDist = None
                minDist = np.inf  # same as inf, need to be concise with np.float64.
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


    def basicOperator(self, avoidObstacles, avoidPedestrians):  # OK
        for index, pedestrian in enumerate(self.pedestrians):
            pedestrianId = pedestrian[0]

            neighbors = self.neighbors(pedestrian[1], pedestrian[2])

            targetAchieved, targetToBeAchieved = self.isTargetInNeighborhood(neighbors, pedestrianId)

            if targetAchieved:
                # Target archieved, then the pedestrian remains in the same cell and set its achieved target status to True
                self.achievedTargets[pedestrianId] = True
            else:
                # Compute the distance from all neighbors in the neighborhood to the target, save the minimum distance
                if neighbors == self.getUnreachableCells(avoidPedestrians):  # TODO: What is this?
                    self.achievedTargets[pedestrianId] = False
                    break

                neighborWithMinDist = (0, 0)
                minDist = np.inf
                for neighbor in neighbors:
                    dist = self.euclidianDistance(neighbor, targetToBeAchieved)
                    if dist < minDist and not neighbor in self.getUnreachableCells(avoidPedestrians):
                        neighborWithMinDist = (neighbor[0], neighbor[1])
                        minDist = dist

                # Change the cell not occupied by the pedestrian
                self.pedestrians[index] = (pedestrianId, neighborWithMinDist[0], neighborWithMinDist[1])

                # Save the current cell in the path
                self.paths[pedestrianId].append((self.pedestrians[index][1], self.pedestrians[index][2]))

    def simulate(self, operator, nSteps, avoidObstacles=True, avoidPedestrians=True):  # OK
        for step in range(nSteps):
            operator(avoidObstacles, avoidPedestrians)

            if all(list(self.achievedTargets.values())):
                print("Simulation finished after {} steps. All pedestrians achieved their targets.".format(step + 1))
                break


    def simulate2(self, operator, seconds, avoidObstacles=True, avoidPedestrians=True):  # OK

        for i in range(seconds):

            if all(list(self.achievedTargets.values())):
                print("Simulation finished after {} seconds. All pedestrians achieved their targets.".format(seconds + 1))
                break

            print("DOING STEP NO: ", i)
            # update available steps because 1 second has passed
            self.update_available_steps()

            while (self.someone_can_move()): # available_steps_for_somebody = E at least 1 pedestrian that can perform at least one step
                operator(avoidObstacles, avoidPedestrians)

    def someone_can_move(self):
        for i, step in enumerate(self.availableSteps):
            if (self.availableSteps[i+1] >= self.step):
                return True
        return False

    def update_available_steps(self):
        for i, steps in enumerate(self.availableSteps):
            self.availableSteps[i+1] = self.availableSteps[i+1] + self.pedestriansSpeed[i+1]


    
    def simulateAndVisualize(self, operator, nSteps, avoidObstacles=True, avoidPedestrians=True, size = (12, 12)):
        for step in range(nSteps):
            operator(avoidObstacles, avoidPedestrians)

            clear_output(wait=True)
            visualize(self.getState(), size)
            sleep(0.2)

            if all(list(self.achievedTargets.values())):
                print("Simulation finished after {} steps. All pedestrians achieved their targets.".format(step + 1))
                break

    def simulateAndVisualize2(self, operator, seconds, avoidObstacles=True, avoidPedestrians=True, size = (12, 12)):
        for i in range(seconds):

            if all(list(self.achievedTargets.values())):
                print(
                    "Simulation finished after {} seconds. All pedestrians achieved their targets.".format(seconds + 1))
                return

            # update available steps because 1 second has passed
            self.update_available_steps()

            while (self.someone_can_move()):  # available_steps_for_somebody = E at least 1 pedestrian that can perform at least one step
                operator(avoidObstacles, avoidPedestrians)
                clear_output(wait=True)
                visualize(self.getState(), size)
                sleep(0.1)

        print("Simulation finished after {} seconds.".format(seconds))
