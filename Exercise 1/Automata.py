from utils import readScenarioFromJSON, readScenarioFromJSONFilePath

from scipy.sparse import dok_matrix
from numpy import full
import numpy as np
from math import inf

from os.path import isdir, exists


class Automata:
    def __init__(self, config):
        
        if type(config) is dict:
            self.width, self.height, self.pedestrians, self.targets, self.obstacles = readScenarioFromJSON(config)
        elif isdir(config) and exists(config):
            self.width, self.height, self.pedestrians, self.targets, self.obstacles = readScenarioFromJSONFilePath(config)
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

    def getDimensions(self): # OK
        return self.width, self.height

    def getState(self): # OK
        grid = dok_matrix((self.height, self.width), dtype=int)

        # TODO: Here maybe instead of 1, we put the pedestrianId => Then we should avoid color for obstacles and targets
        for pedestrian in self.pedestrians:
            grid[self.height - pedestrian[2] - 1, pedestrian[1]] = 1

        for obstacle in self.obstacles:
            grid[self.height - obstacle[1] - 1, obstacle[0]] = 2

        for target in self.targets:
            grid[self.height - target[2] - 1, target[1]] = 3

        return grid.toarray()

    def getStateWithPaths(self): # OK
        grid = self.getState()
        for pedestrianId in self.paths:
            for x, y in self.paths[pedestrianId]:
                grid[self.height - y - 1][x] = pedestrianId
        return grid

    def getPaths(self): # OK
        return self.paths

    def neighbors(self, x, y): # OK

        neighbors = [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)]

        # Checker for a neighbor is not outside of the grid, only selects proper neighbors.
        def validate(coor):
            if coor[0] < 0 or coor[1] < 0:
                return False
            elif coor[0] >= self.height or coor[1] >= self.width:
                return False
            else:
                return True

        return [neighbor for neighbor in neighbors if validate(neighbor)]

    def euclidianDistance(self, neighbor, target): # OK
        neighbor = np.array(neighbor)
        target = np.array(target)

        return np.linalg.norm(neighbor - target)
    
    def isTargetInNeighborhood(self, neighbors, pedestrianId): # OK
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
 
    def getUnreachableCells(self, avoidPedestrians): # OK
        if (not avoidPedestrians):
            return self.obstacles
        else:
            unreachableCells = self.obstacles
            for pedestrian in self.pedestrians:
                unreachableCells.append((pedestrian[1], pedestrian[2]))
            return unreachableCells

    # Dijkstra's algorithm with a target cell in a grid
    def dijkstra(self, target, avoidObstacles, avoidPedestrians):
        # Initialize distances grid with large values
        distances = full((self.width, self.height), inf)

        # Set target cell to 0
        distances[target[1], target[0]] = 0

        # Visited cells
        visited = set()

        while True:
            currentCell = None
            currentMinDist = inf
            for x in range(self.width):
                for y in range(self.height):
                    if (x, y) not in visited and distances[x][y] < currentMinDist:
                        currentCell = (x, y)
                        currentMinDist = distances[x][y]
            
            if currentCell is None:
                break
            visited.add(currentCell)
            for neighbor in self.neighbors(currentCell[0], currentCell[1]):
                if neighbor not in self.getUnreachableCells(avoidPedestrians):
                    newDistance = distances[currentCell[0], currentCell[1]] + self.euclidianDistance(neighbor, currentCell) # 1?
                    if newDistance < distances[neighbor[0], neighbor[1]]:
                        distances[neighbor[0]][neighbor[1]] = newDistance

        return distances

    def operatorWithCostFunction(self, avoidObstacles, avoidPedestrians):
        for index, pedestrian in enumerate(self.pedestrians):
            pedestrianId = pedestrian[0]

            neighbors = self.neighbors(pedestrian[1], pedestrian[2])

            targetAchieved, targetToBeAchieved = self.isTargetInNeighborhood(neighbors, pedestrianId)

            if targetAchieved:
                # Target archieved, then the pedestrian remains in the same cell and set its achieved target status to True
                self.achievedTargets[pedestrianId] = True
            else:
                distanceGrid = self.dijkstra(targetToBeAchieved, avoidObstacles, avoidPedestrians)

                neighborWithMinDist = (0, 0)
                minDist = np.inf  # same as inf, need to be concise with np.float64.
                for neighbor in neighbors:
                    # TODO: Shouldn't we measure the distance from the midpoint of the box to the midpoint of the targets box ?
                    dist = distanceGrid[neighbor[1]][neighbor[0]]
                    if dist < minDist:
                        neighborWithMinDist = (neighbor[0], neighbor[1])
                        minDist = dist
                
                # Change the cell not occupied by the pedestrian
                self.pedestrians[index] = (pedestrianId, neighborWithMinDist[0], neighborWithMinDist[1])

                # Save the current cell in the path
                self.paths[pedestrianId].append((self.pedestrians[index][1], self.pedestrians[index][2]))

    def basicOperator(self, avoidObstacles, avoidPedestrians): # OK
        for index, pedestrian in enumerate(self.pedestrians):
            pedestrianId = pedestrian[0]

            neighbors = self.neighbors(pedestrian[1], pedestrian[2])

            targetAchieved, targetToBeAchieved = self.isTargetInNeighborhood(neighbors, pedestrianId)

            if targetAchieved:
                # Target archieved, then the pedestrian remains in the same cell and set its achieved target status to True
                self.achievedTargets[pedestrianId] = True
            else:
                # Compute the distance from all neighbors in the neighborhood to the target, save the minimum distance
                if neighbors == self.getUnreachableCells(avoidPedestrians): # TODO: What is this?
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

    def simulate(self, operator, nSteps, avoidObstacles = True, avoidPedestrians = True): # OK
        for step in range(nSteps):
            operator(avoidObstacles, avoidPedestrians)

            if all(list(self.achievedTargets.values())):
                print("Simulation finished after {} steps. All pedestrians achieved their targets.".format(step + 1))
                break