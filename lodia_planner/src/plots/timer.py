from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

import numpy as np
import matplotlib.pyplot as plt
import yaml 
from tkinter import *
from tkinter.colorchooser import askcolor

from lodia_planner.globalplanner.setups import setup_allmend_small as setup_file
import lodia_planner.globalplanner.astar as astar_file
import lodia_planner.globalplanner.transform as transform

import time
import resource
from datetime import datetime

# def calc_sim_globe_sim_transform_mistake(point, setup):
#     '''
#     This function calculates and plots the deviation that occures bc of low 
#     resolution of the Maps object (aka how many pixel the Maps array has)
#         Parameters:
#             point ((float x, float y))
#             setup (Setup)
#         Returns:
#             deltax_m (float): deviation in x direction in m
#             deltay_m (float): deviation in y direction in m
#     '''
#     transformed1 = transform.from_globe_to_pixel([point], setup)
#     [transformed2] = transform.from_pixel_to_globe(transformed1, setup)
#     print(point, transformed2)
#     deltax = point[0] - transformed2[0]
#     deltay = point[1] - transformed2[1]
#     deltax_m = transform.calculate_distance_on_globe(point[0], point[1], point[0]+deltax, point[1], setup.maps.globe_radius)
#     deltay_m = transform.calculate_distance_on_globe(point[0], point[1], point[0], point[1]+deltay, setup.maps.globe_radius)
#     return deltax_m, deltay_m

# For time calc: ARCHE with these settings
# start = (246, 493)
# goal = (229, 90)
# setup = setup_file.Setup('lodia_planner', 0.5, 0.0, 0.5, False)

# Define the start and goal positions and load the setup file
#start, goal = (0, 0), (255, 255)
# start = (-46.770, 25.054)
# goal = (-46.753, 25.043)
# start = (66, 462)
# goal = (479, 79)
# Allmend fav setup for sim and globe coordinates
# start = (80, 175)
# goal = (110, 40)
# start = (8.51816, 47.35655)
# goal = (8.51854, 47.3553)
# Moon
start = (-46.77313, 25.05090)
goal = (-46.77422, 25.03763)
factor=256/256
start = (752.5*factor, 105.9*factor)
goal = (77.2*factor, 645.0*factor)

setup = setup_file.Setup('lodia_planner', 0.5, 0.0, 0.5, True)
setup.maps.plot_five_layers([])
plt.show()
# print(setup.maps.get_geo_xmin_ymin_xmax_ymax())

# # Check if transformation works alright
# print(setup.length_of_pixel)
# print(calc_sim_globe_sim_transform_mistake(start, setup))
# print(transform.calculate_distance_on_globe(-46.770, 25.054, -46.7701, 25.054, setup.maps.globe_radius))

# # Plot used maps
#setup.maps.plot_layers([0,1,2],[True, False, False])
#setup.maps.plot_layers_with_path([0,1,2],[True, False, False], [])
#setup.maps.plot_five_layers([])
# setup.maps.plot_four_layers_in_pixel([])
# setup.maps.show_image_with_path([start, goal])
# plt.show()

########## Run A* algorithm ##########
# setup.maps.choose_start_and_goal_on_image()
setup.maps.start = start
setup.maps.goal = goal
# [start_sim, goal_sim] = transform.from_globe_to_sim([setup.maps.start, setup.maps.goal], setup)
# print(start_sim, goal_sim)
[start_pixel, goal_pixel] = transform.from_sim_to_pixel([setup.maps.start, setup.maps.goal], setup)
# print(start_pixel, goal_pixel)

# # prep CPU and time analysis
# start_time = time.time()
# start_time_print = datetime.now().strftime('%H:%M:%S.%f')[:-3]
# Run astart
path, stats = astar_file.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup.h_func, setup.g_func, allow_diagonal=True)
# # finish CPU and time analysis and print
# end_time_print = datetime.now().strftime('%H:%M:%S.%f')[:-3]
# end_time = time.time()

# elapsed_time = end_time - start_time
# print("Running A* started ",str(start_time_print), " and ended ", str(end_time_print), " so it took ", elapsed_time," s.")

# Show result
# path_sim = transform.from_pixel_to_sim(path, setup)
# # path_globe = transform.from_sim_to_globe(path_sim, setup)
# setup.maps.show_image_with_path(path_sim)
# setup.maps.plot_layers_with_path([3,4],[False, False], path_sim)
# plt.show()
#setup.maps.plot_layers_with_path([3],[False],path_globe)
#setup.maps.show_image_with_path_and_energy(path_sim, np.array(stats)[:,0])


# # Show result in pixel
# path_transformed = []
# for point in path:
#     path_transformed.append((point[0], setup.maps.n_px_width-point[1]-1))
# coordinates = transform.tupellist_to_array(path_transformed)
# setup.maps.plot_four_layers_in_pixel(coordinates)

# # Sampling of waypoints
# n = 5
# last = path[path.shape[0]-1,:]
# wp_pixel = np.vstack([path[::n,:], last])

# # Transform in different coordinate systems in save in one dat file
# wp_coordinates = transform.from_pixel_to_globe(wp_pixel, setup)
# print(wp_coordinates)
# x_0, y_0, _, _ = setup.get_geo_xmin_ymin_xmax_ymax()
# print(wp_coordinates[0])
# wp_sim = np.array([transform.from_globe_to_sim(row,setup) for row in wp_coordinates])

# print(transform.from_sim_to_globe(wp_sim[0],setup))

# wp_all = np.concatenate((wp_coordinates, wp_sim, wp_pixel), axis=1)
# column_names = np.array(['# Longitute', 'Latitude', 'x in sim', 'y in sim', 'Row in arr', 'Col in arr'])
# wp_header = '\t'.join(column_names)
# np.savetxt('lodia_planner/data/waypoints.dat', wp_all, header=wp_header, comments='', delimiter='\t', fmt='%-3f')

# # Show result
# path_sim = transform.from_pixel_to_sim(path, setup)
# setup.maps.show_image_with_path(path_sim)
# setup.maps.plot_layers_with_path([3],[False],path_sim)

# plt.figure()
# plt.imshow(setup.maps.map_image, extent=(0, setup.height_of_map, 0, setup.height_of_map))
# plt.plot(wp_sim[:,0], wp_sim[:,1], 'r')
# plt.show()

# # Load data and adapt start position in yaml file for simulation
# loaded_array = np.loadtxt('../pathfollowing/waypoints.dat', comments='#', delimiter='\t')

# # safe first wp as start point in yaml file
# with open("../../configs/aristarchus_imp.yaml") as f:
#     list_doc = yaml.safe_load(f)
# custom_height_adjustment = -2
# height = setup.maps.get_maps_array()[int(loaded_array[0,4]), int(loaded_array[0,5]), 0] + 1300 - custom_height_adjustment
# list_doc['spawn_anymal']['init_pose'] = {'x': float(loaded_array[0,2]), 'y': float(loaded_array[0,3]), 'z': float(height), 'R': 0.0, 'P': 0.0, 'Y': 3.14159265359}
# with open("../../configs/aristarchus_imp.yaml", "w") as f:
#     yaml.dump(list_doc, f)


# import sys
# import time

# import numpy as np

# from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
# if is_pyqt5():
#     from matplotlib.backends.backend_qt5agg import (
#         FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
# else:
#     from matplotlib.backends.backend_qt4agg import (
#         FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
# from matplotlib.figure import Figure


# class ApplicationWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self._main = QtWidgets.QWidget()
#         self.setCentralWidget(self._main)
#         layout = QtWidgets.QVBoxLayout(self._main)

#         fig = Figure(figsize=(5, 3))
#         static_canvas = FigureCanvas(fig)
#         layout.addWidget(static_canvas)
#         self.addToolBar(NavigationToolbar(static_canvas, self))

#         self._static_ax = static_canvas.figure.subplots()
#         t = np.linspace(0, 10, 501)
#         self._static_ax.plot(t, np.tan(t), ".")

#         #fig.canvas.mpl_connect('button_press_event', self.onclick)
#         static_canvas.mpl_connect('button_press_event', self.onclick)
#         self.goal = (1, 2)


#     def onclick(self, event):
#         print(self.goal)
#         self.goal = (event.xdata, event.ydata)
#         print(self.goal)


# if __name__ == "__main__":
#     qapp = QtWidgets.QApplication(sys.argv)
#     app = ApplicationWindow()
#     app.show()
#     qapp.exec_()
