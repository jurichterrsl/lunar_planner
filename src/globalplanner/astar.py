'''This file includes all functions to run the A* algorithm.'''

import heapq
import numpy as np

def astar(map_size, start, goal, setup, allow_diagonal):
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
    costcomponents = 4 # defined in setup function
    g_score = {start: [0]*(costcomponents+1)}
    f_score = {start: setup.h_func(start, goal)}  # Estimated total cost from start to goal
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current, setup.g_func, setup.h_func, goal)

        closed_set.add(current)

        for neighbor in get_neighbors(current, map_size, allow_diagonal):
            if neighbor in closed_set:
                continue

            new_g_score = [x + y for x, y in zip(g_score[current], setup.g_func(neighbor, current))]
            if setup.max_func(new_g_score):
                new_g_score[costcomponents] = np.inf

            if new_g_score[costcomponents] < np.inf and (neighbor not in g_score or new_g_score[costcomponents] < g_score[neighbor][costcomponents]):
                g_score[neighbor] = new_g_score
                f_score[neighbor] = new_g_score[costcomponents] + setup.h_func(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                came_from[neighbor] = current

    print('No path found. Check input parameters.')
    return -1, [-1]  # No path found


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
        cost.append(g_func(current, previous)+(h_func(previous, goal),))
        #cost.append((g_func(current, previous),(h_func(previous, goal))))
        current = previous
    tupellist = list(reversed(path))
    stats = list(reversed(cost))
    return np.array([list(t) for t in tupellist]), stats

