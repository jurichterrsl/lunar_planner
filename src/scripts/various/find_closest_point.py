import numpy as np
import pyproj


def find_two_closest_points():
    '''
    Find the two closest points in the trajectory to the current position.

    Returns:
        tuple: A tuple containing the index of the two closest points as tuples
    '''
    idx_closest_points = [None, None]
    smallest_distances = [float('inf'), float('inf')]

    for idx, point in enumerate(wp_x_y_z):
        distance = np.linalg.norm(point[0:2] - current_position[0:2])

        # Check if the current point is closer than the current closest points
        if distance < smallest_distances[0]:
            smallest_distances[1] = smallest_distances[0]
            idx_closest_points[1] = idx_closest_points[0]

            smallest_distances[0] = distance
            idx_closest_points[0] = idx
        elif distance < smallest_distances[1]:
            smallest_distances[1] = distance
            idx_closest_points[1] = idx

    # If points are not consecutive, take closest point and its consecutive point
    if abs(idx_closest_points[0]-idx_closest_points[1]) != 1:
        idx_closest_points[1] = idx_closest_points[0] + 1
    if idx_closest_points[1] == wp_x_y_z.shape[0]:
        idx_closest_points[1] = idx_closest_points[1] - 2

    return idx_closest_points


def check_path_accuracy():
    '''Checks if the robot deviates too far from the path. If that's the case, it re-transforms the
    global coordinates with the latest umeyama-transform (cmp. gps_alignment.cpp), deletes the old
    coordinates and posts the updated coordiantes'''
    # Measure current deviation from path
    idx1, idx2 = find_two_closest_points()
    print(idx1, idx2)
    a = current_position[:2] - wp_x_y_z[idx1,:2]
    b = wp_x_y_z[idx1,:2] - wp_x_y_z[idx2,:2]
    deviation = np.linalg.norm(np.cross(a,b)) / np.linalg.norm(b)
    print(deviation)

    # Check GPS flag


wp_x_y_z = np.array([[40,20,1], [42,22,2], [43,21,1]])
current_position = (42,20,1)

#print (x, y, z)
# check_path_accuracy()
# print(wp_x_y_z[1:,:])

# wp_x_y_z = np.array([[5.980014801025391, 46.16244888305664, 351.42376708984375],
#                         [5.9800004959106445, 46.16249465942383, 351.5030822753906],
#                         [5.979992866516113, 46.162540435791016, 351.4803466796875],
#                         [5.979965686798096, 46.16258239746094, 351.5308532714844],
#                         [5.9799580574035645, 46.162628173828125, 351.6053466796875], 
#                         [5.979898452758789, 46.16267395019531, 351.68994140625],
#                         [5.979839324951172, 46.16271209716797, 351.67266845703125]])

# print(np.reshape(wp_x_y_z[1,:2],(1,2)))
# print(wp_x_y_z)

list = []
points = [[0,1],[2,3],[4,6]]
for i in range(len(points)):
    list.append([points[i][0], points[i][1]])
wps_next = np.array(list)
print(wps_next)