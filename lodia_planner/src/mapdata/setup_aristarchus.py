""" This file sets the energy function as well as the map-layers up. """

import lodia_planner.src.globalplanner.maps as maps_file
import math
import numpy as np

class Setup:
    """
    A class to create and change the map.
    
    Attributes and Methods can be seen in the class diagram by running 'pyreverse -o png \
        path/to/src/globalplanner'
    """

    ### class parameters
    # define parameters which are useful throughout the class
    ALPHA = 0.5 # weights optimisation between low energy (alpha=1)
    BETA = 0.5 # low risk (beta=1)
    GAMMA = 0 # and high scientific value (gamma=1); alpha+beta+gamma=1
    s_max = 30
    r_max = 0.3
    PLOT_GLOBAL = True


    def __init__(self, path_to_root, a, b, c, plot_global):
        '''
        Init Setup Function
            Parameters:
                # start_coordinates ((int, int)): Start coordinates in pixel scale
                # goal_coordinates ((int, int)): Goal coordinates in pixel scale
                path_to_root (String): path to ROS package root (e.g. /path/to/lodia_planner)
        '''
        self.ALPHA = a
        self.BETA = b
        self.GAMMA = c
        self.PLOT_GLOBAL = plot_global

        self.path_to_root = path_to_root
        self.create_map()

        distance_max = math.sqrt(2) * abs(self.maps.pixel_size)
        self.E_max = self.E(30,0.3,distance_max)
        self.R_max = self.R(-30,0.3,distance_max)
        self.E_min = 0.3922
        

    def create_map(self):
        '''Define the map as an object of class Maps'''
        # Define static parameters of the map
        self.map_size_in_pixel = (256, 256)
        n_layers = 5

        # Create Maps object with first tif file
        self.maps = maps_file.Maps(self.map_size_in_pixel, n_layers,
                                   self.path_to_root+"Aristarchus_IMP/height_slope_rockabundance.tif",
                                   self.path_to_root+"Aristarchus_IMP/pic.png",
                                   layer_description=['Height map', 'Slope', 'Rock abundance'],
                                   plot_global=self.PLOT_GLOBAL)
        
        # Add further tif files if needed
        self.maps.load_npy_file_and_add_to_array(self.path_to_root+'Aristarchus_IMP/banned_blurred.npy',
                                                 'Scientific interest')
        self.maps.load_npy_file_and_add_to_array(self.path_to_root+'Aristarchus_IMP/banned.npy',
                                                 'Banned areas')
        
        # Add steep and rocky areas to banned areas
        slope = self.maps.maps_array[:,:,1]
        rockabundance = self.maps.maps_array[:,:,2]
        banned = self.maps.maps_array[:,:,4]
        banned[slope>30] = 1
        banned[slope<-30] = 1
        banned[rockabundance>0.3] = 1
        self.maps.maps_array[:,:,4] = banned
        #self.maps.maps_array[:,:,4] = np.zeros(self.map_size_in_pixel)

    
    def h_func(self, node, goal):
        '''
        Define the heuristic function h(x, y)
            Parameters:
                node ((int, int)): Node x, y in pixels defining the current node of which \
                    heuristic is calculated
            Returns:
                Float: heuristic value
        '''
        # E_min is minimum of normalized curve for 8m field
        return self.ALPHA * self.E_min * self.getdistance(node, goal)/8


    def g_func(self, current, previous, output_separately=False):
        '''
        Define the cost function g(x, y) that calculates the cost from previous to current node
            Parameters:
                current ((int, int)): Node x, y in pixels defining the current node
                previous ((int, int)): Node x, y in pixels defining the previouse node
                output_separately (Boolean): Outputs the components of the costfunction separately
            Returns:
                Float: cost
        '''
        # get slope and rock abundance of node
        maps = self.maps.get_maps_array()
        x, y = current
        x0, y0 = previous
        distance = self.getdistance(current, previous)
        s = math.degrees(math.atan((maps[x,y,0]-maps[x0,y0,0]) / (distance*abs(self.maps.pixel_size))))
        t = maps[x,y,2]

        if output_separately:
            if (-30 <= s <= 30) and (t <= 0.3):
                E_P = self.E(s,t,distance)/self.E_max
                R_P = self.R(s,t,distance)/self.R_max
            else:
                E_P = math.inf
                R_P = math.inf
            I_P = 1-maps[x,y,3]
            if maps[x,y,4]==1:
                B_P = math.inf
            else:
                B_P = 0

            total = self.ALPHA * E_P + self.BETA * R_P + self.GAMMA * I_P
            return E_P, R_P, I_P, B_P, total

        else:
            if (-30 <= s <= 30) and (t <= 0.3):
                E_P = self.E(s,t,distance)/self.E_max
                R_P = self.R(s,t,distance)/self.R_max
            else:
                return math.inf
            I_P = 1-maps[x,y,3]
            if maps[x,y,4]==1:
                return math.inf
            else:
                B_P = 0

            return self.ALPHA * E_P + self.BETA * R_P + self.GAMMA * I_P     


    def E(self, s, r, distance):
        '''single energy efficient value'''
        # run script 'plot_3D.py' to get coefficients
        return (803.3 + 10.54*s + 70.25*r + 0.7386*s**2 + -1.420*s*r + 1773*r**2) * distance/8


    def R(self, s, r, distance):
        '''single risk value'''
        # run script 'plot_3D.py' to get coefficients
        crash = (0.0005310*s + 0.3194*r + 0.0003137*s**2 + -0.02298*s*r + 10.8*r**2)/100
        if crash<0:
            crash=0
        return 1-(1-crash)**(distance/8)


    def getdistance(self, node1, node2):
        '''
        Calculates the euclidean distance between two nodes
            Parameters:
                node1 ((int, int)): Tupel x, y
                node2 ((int, int)): Tupel x, y
            Returns:
                Float: distance scales on map
        '''
        x1, y1 = node1
        x2, y2 = node2
        return math.sqrt((x2-x1)**2 + (y2-y1)**2) * abs(self.maps.pixel_size)


    def get_geo_xmin_ymin_xmax_ymax(self):
        return self.maps.get_geo_xmin_ymin_xmax_ymax()
