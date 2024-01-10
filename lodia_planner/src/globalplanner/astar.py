'''This file includes all functions to run the A* algorithm.'''

import heapq
import numpy as np


def astar(map_size, start, goal, h_func, g_func, allow_diagonal):
    '''
    Core A* function that calculates the best path and returns it as a list of tuples

    Parameters:
        start ((int, int)): start pixel
        goal ((int, int)): goal pixel
        h_func((int: x_current, int: y_current), (int: x_goal, int: y_goal)) -> float: calculates the heuristic for pixels x,y
        g_func((int: x_current, int: y_current),(int: x_previous, int: y_previous)) -> float:\
            calculates the cost for pixels x,y
        allow_diagonal (Boolean): true checks all 8 neighboring pixels while false only checks 4
    
    Returns:
        path ((int, int)[]): List of tupels 
    '''
    open_set = []
    heapq.heappush(open_set, (0, start))  # Priority queue ordered by cost
    came_from = {}
    g_score = {start: 0}
    f_score = {start: h_func(start, goal)}  # Estimated total cost from start to goal
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            # path = reconstruct_path(came_from, current, g_func, h_func, goal)
            # _, rows = map_size
            # path[0][:,1] = rows - path[0][:,1]
            return reconstruct_path(came_from, current, g_func, h_func, goal)

        closed_set.add(current)

        for neighbor in get_neighbors(current, map_size, allow_diagonal):
            if neighbor in closed_set:
                continue

            new_g_score = g_score[current] + g_func(neighbor, current)
            if neighbor not in g_score or new_g_score < g_score[neighbor]:
                g_score[neighbor] = new_g_score
                f_score[neighbor] = new_g_score + h_func(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                came_from[neighbor] = current

    print('No path found. Check input parameters.')
    return -1, -1  # No path found


def get_neighbors(node, map_size, allow_diagonal=False):
    '''
    Gets all neighbors of a node
        Parameters:
            node ((int, int)): x,y pixels of node
            map_size ((int, int)): row,colums size of map
            allow_diagonal (Boolean): true checks all 8 neighboring pixels while false only checks 4
        Returns:
            (int,int)[]: Tupellist of all neighbors
    '''
    x, y = node
    cols, rows = map_size
    neighbors = []

    # Add adjacent cells as neighbors
    if x > 0:
        neighbors.append((x - 1, y))
    if x < cols - 1:
        neighbors.append((x + 1, y))
    if y > 0:
        neighbors.append((x, y - 1))
    if y < rows - 1:
        neighbors.append((x, y + 1))

    if allow_diagonal:
        # Add diagonal cells as neighbors
        if x > 0 and y > 0:
            neighbors.append((x - 1, y - 1))
        if x > 0 and y < rows - 1:
            neighbors.append((x - 1, y + 1))
        if x < cols - 1 and y > 0:
            neighbors.append((x + 1, y - 1))
        if x < cols - 1 and y < rows - 1:
            neighbors.append((x + 1, y + 1))

    return neighbors


def reconstruct_path(came_from, current, g_func, h_func, goal):
    '''Reconstruct path once it's calculated'''
    path = [current]
    cost = []
    while current in came_from:
        previous = came_from[current]
        path.append(previous)
        cost.append(g_func(current, previous, True)+(h_func(previous, goal),))
        #cost.append((g_func(current, previous),(h_func(previous, goal))))
        current = previous
    tupellist = list(reversed(path))
    stats = list(reversed(cost))
    return np.array([list(t) for t in tupellist]), stats


def example(): 
    '''One arbitrary example how to run the algorithm'''
    # Define the map, start and goal positions
    map = np.random.random((10, 10))
    map_size = (map.shape[0], map.shape[1])
    start = (0, 0)
    goal = (9, 9)

    # Define the heuristic function h(x, y)
    def h_func(node, goal):
        x, y = node
        return abs(goal[0] - x) + abs(goal[1] - y)

    # Define the cost function g(x, y)
    def g_func(node, current):
        x, y = node
        return map[x][y]  # Cost based on the map value

    # Run A* algorithm
    path = astar(map_size, start, goal, h_func, g_func, False)
    print(path) 

if __name__ == "__main__":
    example()
