from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

import numpy as np
import math
import matplotlib.pyplot as plt
import yaml 
from tkinter import *
from tkinter.colorchooser import askcolor

from lodia_planner.globalplanner.setups import setup_wells_extended as setup_file
import lodia_planner.globalplanner.astar as astar_file
import lodia_planner.globalplanner.transform as transform
from scipy.ndimage import maximum_filter, minimum_filter
import time
import resource
from datetime import datetime
import random
from scipy.optimize import curve_fit

def run_all_combos_once(start, goal, faktor):
      # Define the start and goal positions and load the setup file
      # start = (100, 1000)
      # goal = (1900, 1000)
      # start = (5.980815, 46.164613)
      # goal = (5.980683, 46.161752)
      # start = (247, 459)
      # goal = (225, 152)
      # start = (-46.77, 25.056)
      # goal = (-46.752, 25.042)
      # start = (60, 465)
      # goal = (512, 146)

      # Allmend
      # start = (80, 175)
      # goal = (110, 40)
      # start = (8.51816, 47.35655)
      # goal = (8.51854, 47.3553)

      # Moon
      # start = (-46.77313, 25.05090)
      # goal = (-46.77422, 25.03763)
      start = (start[0]*faktor, start[1]*faktor)
      goal = (goal[0]*faktor, goal[1]*faktor)

      # setup = setup_file.Setup('lodia_planner', 0.5, 0.0, 0.5, False)
      # # setup.maps.plot_five_layers([])
      # # [start_globe] = transform.from_sim_to_globe([start], setup)
      # # print(start_globe)
      # setup.maps.show_image_with_path([start, goal], False)
      # # setup.maps.show_image_with_path([start_globe, goal_globe], True)
      # plt.show()

      setups = []
      step = 0.1
      number = int(1/step)

      for i in range(0, number):  # Using integer values and converting to float
            for j in range(0, number):
                  # for k in range(0, number):
                        if i+j != 0:
                              i_float = i * step
                              j_float = j * step
                              # k_float = k * step
                              i_float = i_float / (i_float+j_float)
                              j_float = j_float / (i_float+j_float)
                              # k_float = k_float / (i_float+j_float+k_float)
                              print(i_float, j_float)
                        
                              setup = setup_file.Setup('lodia_planner', i_float, 0, j_float, False)
                              setups.append(setup)

      ##### All combos #####
      num_total = len(setups)
      fig, ax = plt.subplots()
      paths_pixel = []
      paths_coordinates = []
      stats_list = []

      # Run A* in loops
      for i, setup in enumerate(setups):
            [start_pixel, goal_pixel] = transform.from_sim_to_pixel([start, goal], setup)
            path, stats = astar_file.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup.h_func, setup.g_func, allow_diagonal=True)
            path_sim = transform.from_pixel_to_sim(path, setup)
            paths_pixel.append(path)
            paths_coordinates.append(path_sim)
            print(num_total-len(paths_pixel))

      ax.imshow(setup.maps.map_image, extent=setup.maps.extent, aspect=setup.maps.aspect_ratio, alpha=0.5)
      # Show some layer of maps array:
      # plot_map = setup.maps.maps_array[:,:,3]
      # img = ax.imshow(plot_map.T, cmap='viridis', extent=setup.maps.extent,
      #                 aspect = setup.maps.aspect_ratio)
      # cbar = plt.colorbar(img)
      # cbar.ax.set_ylabel(setup.maps.layer_names[3], fontsize=24)
      # cbar.ax.tick_params(labelsize=20)

      ax.set_xlabel("x [m]", fontsize=14)
      ax.set_ylabel("y [m]", fontsize=14)
      # ls = ['-', (5, (10,2)), (0, (10,2,1,2)) ,'--', (0, (1,1)), (0, (3,2,1,2,1,2))]
      for j, path in enumerate(paths_coordinates):
            ax.plot(path[:,0], path[:,1], 'red', linewidth=2)
      # ax.set_title(what[k], fontsize=35)
      ax.tick_params(axis='both', which='major', labelsize=14)
      # legend = ax.legend(axis_legend, fontsize=23, title = titles[k])
      # legend.get_title().set_fontsize(23)

      plt.show()
      # end_time = time.time()
      # elapsed_time = end_time - start_time
      # return elapsed_time


# ###### Run once ######
start = (86, 134)
goal = (760, 657)
size = 256
faktor = size/256
outtime = run_all_combos_once(start, goal, faktor)

