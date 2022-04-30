from utils import readScenarioFromJSON, typeToId

from scipy.sparse import dok_matrix
from numpy import uint8

from math import inf, sqrt


class Automata:
    def __init__(self, scenarioFilePath):
        self.width, self.height, self.pedestrians, self.targets, self.obstacles = readScenarioFromJSON(scenarioFilePath)

        # Initialize arrays of paths for each pedestrian
        self.paths = {}     # {pedestrianId: [(x,y), ...]}
        for pedestrian in self.pedestrians:
            self.path[pedestrian[0]] = [(pedestrian[1], pedestrian[2])]

        # Initialize dictionary of achieved target status for each pedestrian
        self.achievedTargets = {}
        for pedestrian in self.pedestrians:
            self.achievedTargets[pedestrian[0]] = False

    def getState(self):
        grid = dok_matrix((self.height, self.width), dtype=uint8)

        for pedestrian in self.pedestrians:
            grid[pedestrian[0], pedestrian[1]] = 1

        for obstacle in self.obstacles:
            grid[obstacle[0], obstacle[1]] = 2

        for target in self.targets:
            grid[target[0], target[1]] = 3

        return self.grid.toarray()

    def getPaths(self):
        return self.paths

    def getStatus(self):
        return self.achievedTargets

    @staticmethod
    def neighbors(x, y):
        return [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)]

    def basicOperator(self):
        for pedestrian in self.pedestrians:
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
                neighborWithMinDist =  (0, 0)
                minDist = inf
                for neighbor in neighbors:
                    if sqrt((neighbor[0] - targetToBeAchieved[0]) ** 2 + (neighbor[1] - targetToBeAchieved[1]) ** 2) < minDist \
                            and not neighbor in self.obstacles:
                        neighborWithMinDist = (neighbor[0], neighbor[1])

                # Change the cell not occupied by the pedestrian
                pedestrian[1] = neighborWithMinDist[0]
                pedestrian[2] = neighborWithMinDist[1]

                # TODO: What to do when two pedestrians want to be in the same cell?

                # Save the current cell in the path
                self.paths[pedestrianId].append((pedestrian[1], pedestrian[2]))

    def simulate(self, operator, nSteps):
        for step in range(nSteps):
            operator()

            if all(list(self.getStatus().values())):
                print("Simulation finished after {} steps. All pedestrians achieved their targets.".format(step))
                break