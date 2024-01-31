import numpy as np

def get_slope_from_height(heightmap):
    '''
    Returns the maximal slope between one pixel and its 8 neighboring pixel 
    numpy array
        Parameters:
            heightmap (ndarray): 2D array
        Return:
            slopemap (ndarray): 2D array with same size as input size
    '''
    # distance = np.sqrt((np.gradient(heightmap, axis=0)/25) ** 2 + (np.gradient(heightmap, axis=1)/25) ** 2)
    # slopemap = np.degrees(np.arctan(distance))
    slopemap = np.zeros(heightmap.shape)
    for i in range(heightmap.shape[0]):
        for j in range(heightmap.shape[1]):
            slopes = []
            for n, neighbor in enumerate(get_neighbors((i,j))):
                if n<4:
                    slope = np.degrees(np.arctan((heightmap[neighbor]-heightmap[i,j])/(3)))
                else:
                    slope = np.degrees(np.arctan((heightmap[neighbor]-heightmap[i,j])/(np.sqrt(2)*3)))
                slopes.append(slope)
            slopemap[i, j] = max(slopes, key=lambda x: abs(x))

    return slopemap


def get_neighbors(node):
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
    cols, rows = 3,3
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


arr = np.array([[1, 1, 1],
                [1, 1, 4],
                [1, 1, 1]])
slope_map = get_slope_from_height(arr)
print(slope_map)