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

# positions = [(755,88), (792, 178), (786, 295), (735, 410), (539, 546),
#             (392, 622), (363, 680), (239, 722), (144, 672), (137, 590),
#             (92, 441), (145, 375), (192, 358), (251, 299), (301, 284),
#             (311, 232), (345, 220), (391, 216), (444, 217), (514, 193),
#             (593, 189), (584, 135), (599, 64), (569, 9), (419, 12),
#             (384, 43), (332, 11), (284, 46), (206, 53), (142, 106), (16, 168)]

# positions = [(746, 83), (134, 160), (352, 744), (746, 83)]


# weights = [(0.25, 0.25, 0.5), (0.4, 0.1, 0.5), (0.7, 0.2, 0.1)]

setup = setup_file.Setup('lodia_planner', 0.0, 0.0, 1.0, False)

start = (146,144)
goal = (155, 69)
[start_pixel, goal_pixel] = transform.from_sim_to_pixel([start, goal], setup)

full_path = np.array((231, 228))
all_stats = np.array([0,0,0,0,0,0])
positions_pixel = [start_pixel, goal_pixel]
positions = (start, goal)

for i in range(len(positions_pixel)-1):
    #print(i,'/',len(positions)-1)
    start_pixel = positions_pixel[i]
    goal_pixel = positions_pixel[i+1]
    
    # (setup.ALPHA, setup.BETA, setup.GAMMA) = weights[i]
    path, stats = astar_file.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup.h_func, setup.g_func, allow_diagonal=True)

    full_path = np.vstack((full_path, path))
    all_stats = np.vstack((all_stats, stats))

path_sim = transform.from_pixel_to_sim(full_path, setup)

setup.maps.show_10plots_with_path(path_sim, full_path, np.array(positions))

# CHANGE next line according to which data is collected
header = '\t\t'.join(('E_P', 'R_P', 'I_P', 'B_P', 'g_func', 'h_func'))
#stats_with_wp = np.hstack((path_sim[1:], np.array(stats)))
stats_with_wp = np.vstack((all_stats, np.sum(all_stats, axis=0)))
np.savetxt('lodia_planner/src/lodia_planner/globalplanner/stats/aristarchusIMP_manual.dat', stats_with_wp, header=header, comments='', delimiter='\t', fmt='%-3f')

results = np.sum(all_stats, axis=0)

energy = results[0] * 345 * 3.255
risk = 1 - (1-results[1]*(1-(1-0.01512)**(3.255/8)))**(8/3.255)
science = 1 - results[2]/len(full_path)
banned = results[3]/len(full_path)

print('The complete energy consumption is '+str(energy)+' Nm^2.')
print('The taken risk is '+str(risk*100)+' %.')
print('The scientific outcome is '+str(science*100)+' % of what would have been possible on the same path length.')
print(str(banned*100)+' % of the path is in banned areas.')

print(results[0])