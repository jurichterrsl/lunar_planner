from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

import numpy as np
import matplotlib.pyplot as plt
import yaml 
from tkinter import *
from tkinter.colorchooser import askcolor

from lodia_planner.globalplanner.setups import setup_wells_extended as setup_file
import lodia_planner.globalplanner.astar as astar_file
import lodia_planner.globalplanner.transform as transform

import time
import resource
from datetime import datetime

##### Select start and goal #####
## First segment
start = (746, 83)
goal = (134, 160)
setup = setup_file.Setup('lodia_planner', 0.25, 0.25, 0.5, False)

## Second segment
start = (134, 160)
goal = (352, 744)
setup = setup_file.Setup('lodia_planner', 0.4, 0.1, 0.5, False)

## Third segment
start = (352, 744)
goal = (746, 83)
setup = setup_file.Setup('lodia_planner', 0.7, 0.2, 0.1, False)


##### Plot used maps #####
#setup.maps.plot_layers([0,1,2],[True, False, False])
#setup.maps.plot_layers_with_path([0,1,2],[True, False, False], [])
#setup.maps.plot_five_layers([])
# setup.maps.plot_four_layers_in_pixel([])
# setup.maps.show_image_with_path([start, goal])
# plt.show()

##### Run A* algorithm #####
# setup.maps.choose_start_and_goal_on_image()
setup.maps.start = start
setup.maps.goal = goal
[start_pixel, goal_pixel] = transform.from_sim_to_pixel([setup.maps.start, setup.maps.goal], setup)

path, stats = astar_file.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup.h_func, setup.g_func, allow_diagonal=True)
print(path.shape)
##### Show result #####
path_sim = transform.from_pixel_to_sim(path, setup)
setup.maps.show_8plots_with_path(path_sim, path)

# setup.maps.show_image_with_path(path_sim)
# setup.maps.plot_layers_with_path([3,4],[False, False], path_sim)
# plt.show()
#setup.maps.plot_layers_with_path([3],[False],path_globe)
#setup.maps.show_image_with_path_and_energy(path_sim, np.array(stats)[:,0])

