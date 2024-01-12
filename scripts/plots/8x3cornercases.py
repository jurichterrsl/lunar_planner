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
from matplotlib import ticker, colors

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
start = (110, 240)
goal = (115, 130)
start = (86, 134)
goal = (760, 657)


# setup = setup_file.Setup('lodia_planner', 0.5, 0.0, 0.5, False)
# # setup.maps.plot_five_layers([])
# # [start_globe] = transform.from_sim_to_globe([start], setup)
# # print(start_globe)
# setup.maps.show_image_with_path([start, goal], False)
# # setup.maps.show_image_with_path([start_globe, goal_globe], True)
# plt.show()

### TWO PARAMS ###
# setup = setup_file.Setup('lodia_planner', 1.0, 0.0, 0.0, False)
# setup1 = setup_file.Setup('lodia_planner', 0.8, 0.0, 0.2, False)
# setup2 = setup_file.Setup('lodia_planner', 0.6, 0.0, 0.4, False)
# setup3 = setup_file.Setup('lodia_planner', 0.4, 0.0, 0.6, False)
# setup4 = setup_file.Setup('lodia_planner', 0.2, 0.0, 0.8, False)
# setup5 = setup_file.Setup('lodia_planner', 0.0, 0.0, 1.0, False)
# title = '(a, c)='

# setups = [setup, setup1, setup2, setup3, setup4, setup5]

# paths_pixel = []
# paths_coordinates = []
# stats_list = []
# axis_legend = ['(1.0, 0.0)', '(0.8, 0.2)', '(0.6, 0.4)', '(0.4, 0.6)', 
#                '(0.2, 0.8)', '(0.0, 1.0)']

### THREE PARAMS ###
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

# Prepare 8 plots
fig, axis = plt.subplots(4, 2)
plt.subplots_adjust(left=0.02, bottom=0.06, right=0.81, top=0.96, wspace=0.42, hspace=0.42)
cbar_label = ['[m]', '[deg]', '', '']
for i, ax in enumerate(axis.flat):
      if i%2==0:
            if i==4:
                  img = ax.imshow(setup.maps.maps_array[:, :, i//2].T, cmap='viridis',
                              extent=setup.maps.extent, aspect=setup.maps.aspect_ratio,
                              vmin=0.0, vmax=0.01)
            else:
                  img = ax.imshow(setup.maps.maps_array[:, :, i//2].T, cmap='viridis',
                              extent=setup.maps.extent, aspect=setup.maps.aspect_ratio)
            ax.set_xlabel("x [m]", fontsize=26)
            ax.set_ylabel("y [m]", fontsize=26)
            ax.tick_params(axis='both', which='major', labelsize=22)
            cbar = plt.colorbar(img, ax=ax)
            cbar.ax.set_ylabel(cbar_label[i//2], fontsize=22)
            cbar.ax.tick_params(labelsize=22)
      axis[0, 0].contour(np.flip(setup.maps.maps_array[:,:,0].T, axis=0), levels=20, colors='#000000',
                              linestyles='solid', linewidths=1, extent=setup.maps.extent)

# Plot paths in prepared plots
colors = ['yellow', 'orange', 'red']

for i, ax in enumerate(axis.flat):
      if i%2==0:
            for j, path in enumerate(paths_coordinates):
                  ax.plot(path[:,0], path[:,1], colors[j], linewidth=3)
      else:
            # if i==5:
            #       ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
            for j, path in enumerate(paths_pixel):
                  # Calculate and output length
                  pairwise_distances = np.linalg.norm(paths_coordinates[j][1:] - paths_coordinates[j][:-1], axis=1)
                  total_length = np.sum(pairwise_distances)

                  # Prepare scaled x axis
                  num_points = len(path)
                  scaled_x = np.linspace(0, total_length, num_points)

                  # Plot
                  ax.set_facecolor("slategray")
                  if i == 3:
                        slopes = []
                        for k in range(1,len(path)):
                              current = path[k]
                              previous = path[k-1]
                              x, y = current
                              x0, y0 = previous
                              distance = setup.getdistance(current, previous)
                              s = math.degrees(math.atan((setup.maps.maps_array[x,y,0]-setup.maps.maps_array[x0,y0,0]) 
                                                      / (distance*abs(setup.maps.pixel_size))))
                              slopes.append(s)
                        slopes.append(s)
                        ax.plot(scaled_x, slopes, colors[j], linewidth=3)
                  else:
                        ax.plot(scaled_x, setup.maps.maps_array[path[:,0], path[:,1], i//2], colors[j], linewidth=3)
                  ax.tick_params(axis='both', which='major', labelsize=22)

                  # Add legend outside of plot
                  legend = ax.legend(axis_legend, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=22, title=title)
                  legend.get_title().set_fontsize(26)
                  legend.get_frame().set_facecolor('slategray')

# Add titles and axes
axis[0, 0].set_title('Height map',fontsize=26)
axis[0, 1].set_title('Height profile',fontsize=26)
axis[1, 0].set_title('Slope map',fontsize=26)
axis[1, 1].set_title('Slope profile',fontsize=26)
axis[2, 0].set_title('Traversability map',fontsize=26)
axis[2, 1].set_title('Traversability profile',fontsize=26)
axis[3, 0].set_title('Scientific interest map',fontsize=26)
axis[3, 1].set_title('Scientific interest profile',fontsize=26)

axis[0, 1].set_xlabel("Distance [m]", fontsize=26)
axis[0, 1].set_ylabel("Height [m]", fontsize=26)
axis[1, 1].set_xlabel("Distance [m]", fontsize=26)
axis[1, 1].set_ylabel("Slope [deg]", fontsize=26)
axis[2, 1].set_xlabel("Distance [m]", fontsize=26)
axis[2, 1].set_ylabel("Rock abundance", fontsize=26)
axis[3, 1].set_xlabel("Distance [m]", fontsize=26)
axis[3, 1].set_ylabel("Scientific value", fontsize=26)


# # Plots values of energy function
# fig, axis = plt.subplots(1, 6)
# names = ['E_P', 'R_P', 'I_P', 'B_P', 'g_func']
# for i, stat in enumerate(stats_list):
#       stat = np.array(stat)
#       ax = axis.flat[i]
#       for j in range(3):
#             ax.plot(stat[:,j], color=colors[j], linewidth=3)
#       ax.set_title(title+axis_legend[i])
# axis[len(axis)-1].legend(names, loc='center left', bbox_to_anchor=(1, 0.5))

# # Print total length of paths
# for i, path in enumerate(paths_coordinates):
#       path = np.array(path)
#       pairwise_distances = np.linalg.norm(path[1:] - path[:-1], axis=1)
#       total_length = np.sum(pairwise_distances)
#       print("Path "+str(i+1)+" has a total length of "+str(total_length)+" m.")

plt.show()