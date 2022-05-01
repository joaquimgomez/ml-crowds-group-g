from utils import readScenarioFromJSON

from scipy.sparse import dok_matrix
from numpy import uint8

from math import inf, sqrt


class Automata:
    def __init__(self, config):
        self.width, self.height, self.pedestrians, self.targets, self.obstacles = readScenarioFromJSON(config)

        # Initialize arrays of paths for each pedestrian
        self.paths = {}     # {pedestrianId: [(x,y), ...]}
        for pedestrian in self.pedestrians:
            self.paths[pedestrian[0]] = [(pedestrian[1], pedestrian[2])]

        # Initialize dictionary of achieved target status for each pedestrian
        self.achievedTargets = {}
        for pedestrian in self.pedestrians:
            self.achievedTargets[pedestrian[0]] = False

        self.unreachableCells = []
        for obstacle in self.obstacles:
            self.unreachableCells.append(obstacle)

    def getUnreachableCells(self):
        unreachableCells = self.unreachableCells
        for pedestrian in self.pedestrians:
            unreachableCells.append((pedestrian[1], pedestrian[2]))
        return unreachableCells

    def getDimensions(self):
        return self.width, self.height
            
    def getState(self):
        grid = dok_matrix((self.height, self.width), dtype=int)

        # TODO: Here maybe istead of 1, we put the pedestrianId
        for pedestrian in self.pedestrians:
            grid[pedestrian[1], pedestrian[2]] = 1

        for obstacle in self.obstacles:
            grid[obstacle[0], obstacle[1]] = 2

        for target in self.targets:
            grid[target[1], target[2]] = 3

        return grid.toarray()

    def getStateWithPaths(self):
        grid = self.getState();
        for pedestrianId in self.paths:
            for x,y in self.paths[pedestrianId]:
                grid[x][y] = pedestrianId
        return grid


    def getPaths(self):
        return self.paths

    def getPathsOnAGrid(self):
        grid = dok_matrix((self.height, self.width), dtype=int)
        
        for obstacle in self.obstacles:
            grid[obstacle[0], obstacle[1]] = 2

        for target in self.targets:
            grid[target[1], target[2]] = 3
        
        for pedestrian in self.paths:
            for i, j in self.paths[pedestrian]:
                grid[i, j] = pedestrian

        return grid.toarray()

    def getStatus(self):
        return self.achievedTargets

    @staticmethod
    def neighbors(x, y):
        # TODO: what if a neighbor is outside of the grid ? Do we need to make sure that all the neighbors are inside the grid ?
        return [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)]

    def basicOperator(self):
        for index, pedestrian in enumerate(self.pedestrians):
            pedestrianId = pedestrian[0]

            neighbors = self.neighbors(pedestrian[1], pedestrian[2])

            # Check if the target is in the neighborhood
            targetAchieved = False
            targetToBeAchieved = (None, None)
            for target in self.targets:
                if pedestrianId in target[0] and ((target[1], target[2]) in neighbors):
                    targetAchieved = True
                    break
                elif pedestrianId in target[0] and not ((target[1], target[2]) in neighbors):
                    targetToBeAchieved = (target[1], target[2])

            if targetAchieved:
                # Target archieved, then the pedestrian remains in the same cell and set its achieved target status to True
                self.achievedTargets[pedestrianId] = True
            else:
                # Compute the distance from all neighbors in the neighborhood to the target, save the minimum distance
                # TODO: What if there is nowhere to go ? Then it goes to (0,0) directly
                neighborWithMinDist = (0, 0)
                minDist = inf
                for neighbor in neighbors:
                    # TODO: Shouldn't we measure the distance from the midpoint of the box to the midpoint of the targets box ?
                    dist = sqrt((neighbor[0] - targetToBeAchieved[0]) ** 2 + (neighbor[1] - targetToBeAchieved[1]) ** 2)

                    if dist < minDist and not neighbor in self.obstacles:
                        neighborWithMinDist = (neighbor[0], neighbor[1])
                        minDist = dist

                # Change the cell not occupied by the pedestrian
                self.pedestrians[index] = (pedestrianId, neighborWithMinDist[0], neighborWithMinDist[1])

                # Save the current cell in the path
                self.paths[pedestrianId].append((self.pedestrians[index][1], self.pedestrians[index][2]))

    def simulate(self, operator, nSteps):
        for step in range(nSteps):
            operator()

            if all(list(self.getStatus().values())):
                print("Simulation finished after {} steps. All pedestrians achieved their targets.".format(step))
                break