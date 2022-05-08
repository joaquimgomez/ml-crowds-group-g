def dijkstraOld(self, target, avoidObstacles, avoidPedestrians):
        # Dijkstra's algoritm for flooding grid with distance values to a target cell assigning large values to unreachable cells  
        # Initialize distances grid with large values
        distances = full((self.width, self.height), inf)

        # Set target cell to 0
        distances[self.height - target[1] - 1, target[0]] = 0

        # Initialize queue with target cell
        queue = [(self.height - target[1] - 1, target[0])]

        # While remain unvisited cells (queue is not empty)
        while queue:
            # Get the cell with the smallest distance
            current = queue.pop(0)

            # For each neighbor of the current cell
            for neighbor in self.neighbors(current[0], current[1]):
                # If the neighbor is not an obstacle
                if avoidObstacles:
                    if neighbor not in self.getUnreachableCells(avoidPedestrians):
                        # If the distance to the neighbor is larger than the distance to the current cell plus 1
                        if distances[current[0], current[1]] + 1 < distances[neighbor[0], neighbor[1]]:
                            # Set the distance to the neighbor to the distance to the current cell plus 1
                            distances[neighbor[0], neighbor[1]] = distances[current[0], current[1]] + self.euclidianDistance(neighbor, current)
                            # Add the neighbor to the queue
                            queue.append(neighbor)
                else:
                    # If the distance to the neighbor is larger than the distance to the current cell plus 1
                    if distances[current[0], current[1]] + 1 < distances[neighbor[0], neighbor[1]]:
                        # Set the distance to the neighbor to the distance to the current cell plus 1
                        distances[neighbor[0], neighbor[1]] = distances[current[0], current[1]] + self.euclidianDistance(neighbor, current)
                        # Add the neighbor to the queue
                        queue.append(neighbor)

        # Return the distance to the target cell
        return distances

    def operatorWithCostFunctionOld(self, avoidObstacles, avoidPedestrians):
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
                    dist = distanceGrid[neighbor[0], neighbor[1]]
                    if dist < minDist and not neighbor in self.getUnreachableCells(avoidPedestrians):
                        neighborWithMinDist = (neighbor[0], neighbor[1])
                        minDist = dist
                
                # Change the cell not occupied by the pedestrian
                self.pedestrians[index] = (pedestrianId, neighborWithMinDist[0], neighborWithMinDist[1])

                # Save the current cell in the path
                self.paths[pedestrianId].append((self.pedestrians[index][1], self.pedestrians[index][2]))