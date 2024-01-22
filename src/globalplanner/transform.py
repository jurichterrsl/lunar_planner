'''A file that includes several transformation functions'''

import numpy as np
import math
import pyproj


def from_pixel_to_globe(coordinates, setup):
    '''
    Transforms an array of coordinates or a list of tupels in pixel into the coordinates of a map
        Parameters:
            coordinates (ndarray): Must have size (n,2) or len n (if tupellist)
            setup (Setup): setup file containing the map data as well as the map_size_in_pixel
        Returns:
            transformed_coordinates (ndarray): 2D array with size (n,2)
    '''
    # Extract x and y coordinates from the input array or the tupel ist
    coordinates_sim = from_pixel_to_map(coordinates, setup)
    return from_map_to_globe(coordinates_sim, setup)


def from_globe_to_pixel(coordinates, setup):
    # Extract x and y coordinates from the input array or the tupel ist
    coordinates_sim = from_globe_to_map(coordinates, setup)
    return from_map_to_pixel(coordinates_sim, setup)


# def from_globe_to_map(coordinates, setup):
#     # Extract x and y coordinates from the input array or the tupel ist
#     coordinates_sim = from_globe_to_pixel(coordinates, setup)
#     return from_pixel_to_map(coordinates_sim, setup)


def from_pixel_to_map(coordinates, setup):
    '''
    Transforms an array of coordinates or a list of tupels in pixel into the coordinates of a map
        Parameters:
            coordinates (ndarray): Must have size (n,2) or len n (if tupellist)
            setup (Setup): setup file containing the map data as well as the map_size_in_pixel
        Returns:
            transformed_coordinates (ndarray): 2D array with size (n,2)
    '''
    # Extract x and y coordinates from the input array or the tupel ist
    if isinstance(coordinates, np.ndarray):
        # If coordinates is a NumPy array
        output_type = np.ndarray
    elif isinstance(coordinates, list):
        # If coordinates is a list of tuples
        coordinates = tupellist_to_array(coordinates)
        output_type = list
    else:
        raise TypeError("Invalid type for 'coordinates'. Must be a NumPy array or a list of tuples.")
    
    row = coordinates[:, 0]
    col = setup.maps.n_px_height-1 - coordinates[:, 1]
    
    transformed_y = abs(setup.maps.pixel_size) * (col + 0.5)
    transformed_x = abs(setup.maps.pixel_size) * (row + 0.5)

    # Return the transformed coordinates based on the input type
    if output_type == np.ndarray:
        return np.column_stack((transformed_x, transformed_y))
    if output_type == list:
        return [tuple(row) for row in np.column_stack((transformed_x, transformed_y))]


def from_map_to_pixel(coordinates, setup):
    '''
    Transforms an array of coordinates or a list of tupels in pixel into the coordinates of a map
        Parameters:
            coordinates (ndarray): Must have size (n,2) or len n (if tupellist)
            setup (Setup): setup file containing the map data as well as the map_size_in_pixel
        Returns:
            transformed_coordinates (ndarray): 2D array with size (n,2)
    '''
    # Extract x and y coordinates from the input array or the tupel ist
    if isinstance(coordinates, np.ndarray):
        # If coordinates is a NumPy array
        output_type = np.ndarray
    elif isinstance(coordinates, list):
        # If coordinates is a list of tuples
        coordinates = tupellist_to_array(coordinates)
        output_type = list
    else:
        raise TypeError("Invalid type for 'coordinates'. Must be a NumPy array or a list of tuples.")
    
    x = coordinates[:, 0]
    y = coordinates[:, 1]
    
    transformed_y = (setup.maps.n_px_height-1 - y//abs(setup.maps.pixel_size)).astype(int)
    transformed_x = (x//abs(setup.maps.pixel_size)).astype(int)

    # Return the transformed coordinates based on the input type
    if output_type == np.ndarray:
        return np.column_stack((transformed_x, transformed_y))
    if output_type == list:
        return [tuple(row) for row in np.column_stack((transformed_x, transformed_y))]


def tupellist_to_array(tupellist):
    '''
    Transforms an array size (n,2) into a list of tupels with len n
        Parameters:
            tupellist ((int, int)[]): List of tupels
        Returns:
            ndarray: 2D array of size (n,2)
    '''
    return np.array([list(t) for t in tupellist])


def array_to_tupellist(array):
    '''
    Transforms a list of tupels with len n into an array size (n,2)
        Parameters:
            array (ndarray): 2D array of size (n,2)
        Returns:
            (int, int)[]: List of tupels
    '''
    return [tuple(row) for row in array]


def from_globe_to_map(coordinates, setup):
    '''
    Transforms one pair of coordinates from the globe coordinates to coordinates of the simulation
        Parameters:
            coordinates (ndarray): original coordinates as longitude and latitude
            setup (Setup): setup file containing the map data as well as the map_size_in_pixel
        Returns:
            transformed_coordinates (ndarray): 2D array of size (1,2)
    '''
    if isinstance(coordinates, np.ndarray):
        # If coordinates is a NumPy array
        output_type = np.ndarray
    elif isinstance(coordinates, list):
        # If coordinates is a list of tuples
        coordinates = tupellist_to_array(coordinates)
        output_type = list
    else:
        raise TypeError("Invalid type for 'coordinates'. Must be a NumPy array or a list of tuples.")

    reference_heading = math.pi/2

    cn = np.cos(reference_heading)
    sn = np.sin(reference_heading)
    kn = 180.0 / 1736000 / np.pi
    ke = 180.0 / 1738100 / np.pi
    lat_tmp = (coordinates[:, 1] - setup.maps.ymin) / kn
    lon_tmp = (coordinates[:, 0] - setup.maps.xmin) / ke

    x_transformed = cn * lat_tmp + sn * lon_tmp
    y_transformed = sn * lat_tmp - cn * lon_tmp

    # Return the transformed coordinates based on the input type
    if output_type == np.ndarray:
        return np.column_stack((x_transformed, y_transformed))
    if output_type == list:
        return [tuple(row) for row in np.column_stack((x_transformed, y_transformed))]


def from_map_to_globe(coordinates, setup):
    '''
    Transforms one pair of coordinates from coordinates of the simulation to the globe coordinates
        Parameters:
            coordinates (ndarray): original coordinates as difference in m from bottom left corner
            setup (Setup): setup file containing the map data as well as the map_size_in_pixel
        Returns:
            transformed_coordinates (ndarray): 2D array of size (1,2)
    '''
    if isinstance(coordinates, np.ndarray):
        # If coordinates is a NumPy array
        output_type = np.ndarray
    elif isinstance(coordinates, list):
        # If coordinates is a list of tuples
        coordinates = tupellist_to_array(coordinates)
        output_type = list
    else:
        raise TypeError("Invalid type for 'coordinates'. Must be a NumPy array or a list of tuples.")

    reference_heading = math.pi/2

    cn = np.cos(reference_heading)
    sn = np.sin(reference_heading)
    kn = 180.0 / 1736000 / np.pi
    ke = 180.0 / 1738100 / np.pi

    lat_tmp = cn * coordinates[:, 0] + sn * coordinates[:, 1]
    lon_tmp = sn * coordinates[:, 0] - cn * coordinates[:, 1]

    y_transformed = lat_tmp * kn + setup.maps.ymin
    x_transformed = lon_tmp * ke + setup.maps.xmin

    # Return the transformed coordinates based on the input type
    if output_type == np.ndarray:
        return np.column_stack((x_transformed, y_transformed))
    if output_type == list:
        return [tuple(row) for row in np.column_stack((x_transformed, y_transformed))]


def calculate_distance_on_globe(lon1, lat1, lon2, lat2, globe_radius):
    '''
    Function to calculate distance between two points using the haversine formula
        Parameters:
            lon1 (Float): Longitude of point 1
            lat1 (Float): Latitude of point 1
            lon2 (Float): Longitude of point 2
            lat2 (Float): Latitude of point 2
        Returns:
            Float
    '''
    lon1_rad = degrees_to_radians(lon1)
    lat1_rad = degrees_to_radians(lat1)
    lon2_rad = degrees_to_radians(lon2)
    lat2_rad = degrees_to_radians(lat2)

    delta_lon = lon2_rad - lon1_rad
    delta_lat = lat2_rad - lat1_rad

    a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) \
        * np.sin(delta_lon / 2) ** 2
    c = 2 * np.arctan(np.sqrt(a), np.sqrt(1 - a))

    # Distance on the surface of the sphere (Moon)
    distance = globe_radius * c

    return distance


def degrees_to_radians(degrees):
    '''
    Function to convert degrees to radians
        Parameters:
            degrees (Float)
        Returns:
            Float
    '''
    return degrees * math.pi / 180


