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

# Define the start and goal positions and load the setup file
start = (86, 134)
goal = (760, 657)

# setup = setup_file.Setup('lodia_planner', 0.5, 0.0, 0.5, False)
# # setup.maps.plot_five_layers([])
# # [start_globe] = transform.from_sim_to_globe([start], setup)
# # print(start_globe)
# setup.maps.show_image_with_path([start, goal], False)
# # setup.maps.show_image_with_path([start_globe, goal_globe], True)
# plt.show()

setup = setup_file.Setup('lodia_planner', 1.0, 0.0, 0.0, False)
setup1 = setup_file.Setup('lodia_planner', 0.0, 1.0, 0.0, False)
setup2 = setup_file.Setup('lodia_planner', 0.0, 0.0, 1.0, False)
title = '('+r'$\alpha$'+','+r'$\beta$'+','+r'$\gamma$'+')=' 

setups = [setup, setup1, setup2]

paths_pixel = []
paths_coordinates = []
stats_list = []
axis_legend = ['(1.0, 0.0, 0.0)', '(0.0, 1.0, 0.0)', '(0.0, 0.0, 1.0)']

# Run A* in loops
for i, setup in enumerate(setups):
      #setup.maps.plot_five_layers([])
      [start_pixel, goal_pixel] = transform.from_sim_to_pixel([start, goal], setup)
      path, stats = astar_file.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup.h_func, setup.g_func, allow_diagonal=True)
      path_coordinates = transform.from_pixel_to_sim(path, setup)
      paths_pixel.append(path)
      paths_coordinates.append(path_coordinates)
      stats_list.append(stats)
      print(len(paths_pixel))

# Prepare 4 plots
fig, axis = plt.subplots(2, 2)
plt.subplots_adjust(left=0.04, bottom=0.07, right=1.0, top=0.96, wspace=0.19, hspace=0.33)
cbar_label = ['m', 'deg', '100%', '100%']
for i, ax in enumerate(axis.flat):
      if i==2:
            img = ax.imshow(setup.maps.maps_array[:, :, i].T, cmap='viridis',
                        extent=setup.maps.extent, aspect=setup.maps.aspect_ratio,
                        vmin=0.0, vmax=0.01)
      else:
            img = ax.imshow(setup.maps.maps_array[:, :, i].T, cmap='viridis',
                        extent=setup.maps.extent, aspect=setup.maps.aspect_ratio)
      ax.set_xlabel("x [m]", fontsize=26)
      ax.set_ylabel("y [m]", fontsize=26)
      ax.tick_params(axis='both', which='major', labelsize=22)
      cbar = plt.colorbar(img, ax=ax)
      cbar.ax.set_ylabel(cbar_label[i], fontsize=22)
      cbar.ax.tick_params(labelsize=22)
      axis[0,0].contour(np.flip(setup.maps.maps_array[:,:,0].T, axis=0), levels=20, colors='#000000',
                              linestyles='solid', linewidths=1, extent=setup.maps.extent)

# Plot paths in prepared plots
colors = ['yellow', 'orange', 'red']
for i, ax in enumerate(axis.flat):
      for j, path in enumerate(paths_coordinates):
            ax.plot(path[:,0], path[:,1], colors[j], linewidth=3)
      legend = ax.legend(axis_legend, fontsize=22, title = title)
      legend.get_title().set_fontsize(22)

# Add titles and axes
axis[0,0].set_title('Height map',fontsize=26)
axis[0,1].set_title('Slope',fontsize=26)
axis[1,0].set_title('Traversability score',fontsize=26)
axis[1,1].set_title('Scientific interest',fontsize=26)

# # Plots values of energy function
# fig, axis = plt.subplots(1, 6)
# names = ['E_P', 'R_P', 'I_P', 'B_P', 'g_func']
# for i, stat in enumerate(stats_list):
#       stat = np.array(stat)
#       ax = axis.flat[i]
#       for j in range(5):
#             ax.plot(stat[:,j], color=colors[j], linewidth=3)
#       ax.set_title(title+axis_legend[i])
# axis[len(axis)-1].legend(names, loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()