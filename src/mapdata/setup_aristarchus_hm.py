""" This file sets the energy function as well as the map-layers up. """

from globalplanner import maps
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

        # Define constants for h and g function

        # Get map of maximal slope
        max_slope_map = self.maps.get_slope_from_height(self.maps.maps_array[:,:,0])
        max_slope_map[max_slope_map>self.s_max]=self.s_max
        max_slope_map[max_slope_map<-self.s_max]=-self.s_max
        # Get map of maximal energy consumption
        distance_max = math.sqrt(2) * abs(self.maps.pixel_size)
        E_map_max = self.E_star(max_slope_map, self.maps.maps_array[:,:,2], distance_max)
        # Get map of maximal risk (manually bc R function with if statement does not support array)
        crash_max_map = -0.0288 + 0.0005310*max_slope_map + \
            0.3194*self.maps.maps_array[:,:,2] + 0.0003137*max_slope_map**2 + \
                -0.02298*-max_slope_map*self.maps.maps_array[:,:,2] + 10.8*self.maps.maps_array[:,:,2]**2
        self.crash_max = np.nanmax(crash_max_map)

        R_map_max = np.zeros(max_slope_map.shape)
        for i in range(max_slope_map.shape[0]):
            for j in range(max_slope_map.shape[1]):
                R_map_max[i,j] = self.R_star(max_slope_map[i,j], self.maps.maps_array[i,j,2], distance_max)
        # Get maximal values
        self.Emax = np.nanmax(E_map_max)
        self.Rmax = np.nanmax(R_map_max)

        # Get map of minimal slope
        min_slope_map = self.maps.get_slope_from_height(self.maps.maps_array[:,:,0], get_min_slope=True)
        min_slope_map[min_slope_map>self.s_max]=self.s_max
        min_slope_map[min_slope_map<-self.s_max]=-self.s_max
        # Get map of minimal energy consumption
        distance_min = abs(self.maps.pixel_size)
        E_map_min = self.E_star(min_slope_map, self.maps.maps_array[:,:,2], distance_min)
        # Get map of minimal risk (manually bc R function with if statement does not support array)
        R_map_min = np.zeros(min_slope_map.shape)
        for i in range(min_slope_map.shape[0]):
            for j in range(min_slope_map.shape[1]):
                R_map_min[i,j] = self.R_star(min_slope_map[i,j], self.maps.maps_array[i,j,2], distance_min)
        # Get minimal values
        Emin = np.nanmin(E_map_min)/self.Emax
        Rmin = np.nanmin(R_map_min)/self.Rmax
        # Get minimal cost for heuristic
        self.hmin = self.ALPHA * Emin + self.BETA * Rmin

        # print("Emin, Rmin: ", Emin, Rmin)
        # print("hmin: ", self.hmin)
        # print("Emax, Rmax: ", self.Emax, self.Rmax)
        

    def create_map(self):
        '''Define the map as an object of class Maps'''
        # Define static parameters of the map
        self.map_size_in_pixel = (256, 191)
        n_layers = 5
        self.costcomponents = 4 #E_P, R_P, I_P, B_P
        self.energyreserve = np.inf #Nm^2

        # Create Maps object with first tif file
        self.maps = maps.Maps(self.map_size_in_pixel, n_layers,
                                   self.path_to_root+"Herodutus_Mons/hsr.tif",
                                   self.path_to_root+"Herodutus_Mons/pic.png",
                                   layer_description=['Height map [m]', 'Slope [deg]', 'Rock abundance'],
                                   plot_global=self.PLOT_GLOBAL)
        
        # Change height and slope so that slope is second and heigth first entry
        slope = np.copy(self.maps.maps_array[:,:,0])
        self.maps.maps_array[:,:,0] = self.maps.maps_array[:,:,1]
        self.maps.maps_array[:,:,1] = slope
        
        # Add more layers
        self.maps.extract_geotiff_science(self.path_to_root+"Herodutus_Mons/clino_feo_tio_plagio.tif")
        self.maps.load_npy_file_and_add_to_array(self.path_to_root+'Herodutus_Mons/banned.npy',
                                                  'Banned areas')
        
        # Add steep and rocky areas to banned areas
        slope = self.maps.maps_array[:,:,1]
        rockabundance = self.maps.maps_array[:,:,2]
        # Load banned areas or set to zero
        banned = self.maps.maps_array[:,:,4]
        banned[slope>30] = 1
        banned[slope<-30] = 1
        banned[rockabundance>0.3] = 1
        self.maps.maps_array[:,:,4] = banned
        self.maps.layer_names.append("Banned")


    def h_func(self, node, goal):
        '''
        Define the heuristic function h(x, y)
            Parameters:
                node ((int, int)): Node x, y in pixels defining the current node of which \
                    heuristic is calculated
            Returns:
                Float: heuristic value
        '''
        x1, y1 = node
        x2, y2 = goal
        return self.hmin * math.sqrt((x2-x1)**2 + (y2-y1)**2)


    def g_func(self, current, previous):
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
        s = math.degrees(math.atan((maps[x,y,0]-maps[x0,y0,0]) / distance))
        t = maps[x,y,2]

        if (-30 <= s <= 30) and (t <= 0.3):
            E = self.E_star(s,t,distance)/self.Emax
            R = self.R_star(s,t,distance)/self.Rmax
        else:
            E = math.inf
            R = math.inf
        I = 1-maps[x,y,3]
        if maps[x,y,4]==1:
            B = math.inf
        else:
            B = 0

        total = self.ALPHA * E + self.BETA * R + self.GAMMA * I
        return E, R, I, B, total


    def max_func(self, g_score):
        '''Function to check the hard constraints'''
        if g_score[0] >= self.energyreserve/(345*3.255):
            return True


    def E_star(self, s, r, distance):
        '''single energy efficient value'''
        # run script 'plot_3D.py' to get coefficients
        return (803.3 + 10.54*s + 70.25*r + 0.7386*s**2 + -1.420*s*r + 1773*r**2) * distance/8


    def R_star(self, s, r, distance):
        '''single risk value'''
        # run script 'plot_3D.py' to get coefficients
        crash = -0.0288 + 0.0005310*s + 0.3194*r + 0.0003137*s**2 + -0.02298*s*r + 10.8*r**2
        if crash<=0.00001:
            crash=0.00001
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
