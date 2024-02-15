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

from mapdata import setup_aristarchus_imp as setup_file
from globalplanner import transform, astar

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

      plot_global = True

      setup = setup_file.Setup('src/mapdata/', 1.0, 0.0, 0.0, plot_global)
      setup1 = setup_file.Setup('src/mapdata/', 0.8, 0.2, 0.0, plot_global)
      setup2 = setup_file.Setup('src/mapdata/', 0.6, 0.4, 0.0, plot_global)
      setup3 = setup_file.Setup('src/mapdata/', 0.4, 0.6, 0.0, plot_global)
      setup4 = setup_file.Setup('src/mapdata/', 0.2, 0.8, 0.0, plot_global)
      # setup1 = setup_file.Setup('src/mapdata/', 0.5, 0.5, 0.0, plot_global)
      setup5 = setup_file.Setup('src/mapdata/', 0.0, 1.0, 0.0, plot_global)
      title = '(a, b)='
      setups_a = [setup, setup1, setup2, setup3, setup4, setup5]

      setup = setup_file.Setup('src/mapdata/', 0, 1.0, 0.0, plot_global)
      setup1 = setup_file.Setup('src/mapdata/', 0, 0.8, 0.2, plot_global)
      setup2 = setup_file.Setup('src/mapdata/', 0, 0.6, 0.4, plot_global)
      setup3 = setup_file.Setup('src/mapdata/', 0, 0.4, 0.6, plot_global)
      setup4 = setup_file.Setup('src/mapdata/', 0, 0.2, 0.8, plot_global)
      # setup1 = setup_file.Setup('src/mapdata/', 0, 0.5, 0.5, plot_global)
      setup5 = setup_file.Setup('src/mapdata/', 0, 0.0, 1.0, plot_global)
      title = '(b, c)='
      setups_b = [setup, setup1, setup2, setup3, setup4, setup5]

      setup = setup_file.Setup('src/mapdata/', 1.0, 0.0, 0.0, plot_global)
      setup1 = setup_file.Setup('src/mapdata/', 0.8, 0.0, 0.2, plot_global)
      setup2 = setup_file.Setup('src/mapdata/', 0.6, 0.0, 0.4, plot_global)
      setup3 = setup_file.Setup('src/mapdata/', 0.4, 0.0, 0.6, plot_global)
      setup4 = setup_file.Setup('src/mapdata/', 0.2, 0.0, 0.8, plot_global)
      # setup1 = setup_file.Setup('src/mapdata/', 0.5, 0.0, 0.5, plot_global)
      setup5 = setup_file.Setup('src/mapdata/', 0.0, 0.0, 1.0, plot_global)
      title = '(a, c)='
      setups_c = [setup, setup1, setup2, setup3, setup4, setup5]

      # setup = setup_file.Setup('lodia_planner', 1.0, 0.0, 0.0, True)
      # setup4 = setup_file.Setup('lodia_planner', 0.5, 0.0, 0.5, True)
      # setup5 = setup_file.Setup('lodia_planner', 0.0, 0.0, 1.0, True)
      # title = '(a, c)='
      # setups_c = [setup, setup4, setup5]

      ##### All combos #####
      setups_all = [setups_a, setups_b, setups_c]
      axis_legend = ['(1.0, 0.0)', '(0.8, 0.2)', '(0.6, 0.4)', '(0.4, 0.6)', 
                  '(0.2, 0.8)', '(0.0, 1.0)']
      colors = [['red', 'orange', 'yellow', 'green', 'blue', 'purple'],
                ['red', 'orange', 'yellow', 'green', 'blue', 'purple'],
                ['red', 'orange', 'yellow', 'green', 'blue', 'purple']]
      titles = ['('+r'$\alpha_1$'+','r'$\alpha_2$'+')=', 
            '('+r'$\alpha_2$'+','r'$\alpha_3$'+')=', 
            '('+r'$\alpha_1$'+','r'$\alpha_3$'+')=']
      # titles = ['(a, b)=', '(b, c)=', '(a, c)=']
      what = ['','',''] # ['Energy vs. Risk', 'Risk vs. Interest', 'Energy vs. Interest']
      fig, axis = plt.subplots(1, 3)
      fig2, axis2 = plt.subplots(1, 1)
      for k, ax in enumerate(axis.flat):

      ###### Without plots ######
      # start_time = time.time()
      # for k in range(3):

      # ##### Only one #####
      # setups_all = [setups_c]
      # axis_legend = ['(1.0, 0.0)', '(0.8, 0.2)', '(0.6, 0.4)', '(0.4, 0.6)', 
      #                '(0.2, 0.8)', '(0.0, 1.0)']
      # axis_legend = ['(1.0, 0.0)', '0.5, 0.5', '(0.0, 1.0)']
      #colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
      # colors = ['red', 'yellow', 'purple']
      # titles = ['(a, c)=']
      # what = ['Energy vs. Interest']
      # fig, axis = plt.subplots(1, 1)
      # k = 0
      # ax = axis
      # if True: 
      
            # setup.maps.plot_layers([0,1,2],[True,False,False])
            paths_pixel = []
            paths_coordinates = []
            stats_list = []
            setups = setups_all[k]

            # Run A* in loops
            for i, setup in enumerate(setups):
                  #setup.maps.plot_five_layers([])
                  #[start_pixel, goal_pixel] = transform.from_sim_to_pixel([start, goal], setup)
                  # [start_sim, goal_sim] = transform.from_globe_to_sim([start, goal], setup)
                  path, stats = astar.astar(setup.map_size_in_pixel, start, goal, setup, allow_diagonal=True)
                  path_globe = transform.from_pixel_to_globe(path, setup)
                  #path_coordinates = transform.from_sim_to_globe(path_sim, setup)
                  paths_pixel.append(path)
                  paths_coordinates.append(path_globe)
                  # stats_list.append(stats)
                  print(len(paths_pixel))
                  # setup.maps.show_image_with_path(path_coordinates)
                  # setup.maps.plot_layers_with_path([0],[True],path_coordinates)
                  # setup.maps.plot_five_layers(path_coordinates)
                  # CHANGE next line according to which data is collected
                  # header = '\t\t'.join(('LON', 'LAT', 'E_P', 'R_P', 'I_P', 'B_P', 'g_func', 'h_func'))
                  # stats_with_wp = np.hstack((path_coordinates[1:], np.array(stats)))
                  # stats_with_wp = np.vstack((stats_with_wp, np.sum(stats_with_wp, axis=0, where=[0,0,1,1,1,1,1,1])))
                  # np.savetxt('lodia_planner/data/stats'+str(i)+'.dat', stats_with_wp, header=header, comments='', delimiter='\t', fmt='%-3f')

            # Show image:
            ax.imshow(setup.maps.map_image, extent=setup.maps.extent, aspect=setup.maps.aspect_ratio, alpha=0.5)
            axis2.imshow(setup.maps.map_image, extent=setup.maps.extent, aspect=setup.maps.aspect_ratio, alpha=0.5)
            # Show some layer of maps array:
            # plot_map = setup.maps.maps_array[:,:,3]
            # img = ax.imshow(plot_map.T, cmap='viridis', extent=setup.maps.extent,
            #                 aspect = setup.maps.aspect_ratio)
            # cbar = plt.colorbar(img)
            # cbar.ax.set_ylabel(setup.maps.layer_names[3], fontsize=24)
            # cbar.ax.tick_params(labelsize=20)

            ax.set_xlabel("LON [deg]", fontsize=16)
            ax.set_ylabel("LAT [deg]", fontsize=16)
            axis2.set_xlabel("LON [deg]", fontsize=16)
            axis2.set_ylabel("LAT [deg]", fontsize=16)

            ls = ['-', (5, (10,2)), (0, (10,2,1,2)) ,'--', (0, (1,1)), (0, (3,2,1,2,1,2))]
            for j, path in enumerate(paths_coordinates):
                  ax.plot(path[:,0], path[:,1], colors[k][j], linewidth=5, linestyle=ls[j])
                  axis2.plot(path[:,0], path[:,1], 'r', linewidth=2)
            ax.set_title(what[k], fontsize=16)
            ax.tick_params(axis='both', which='major', labelsize=16)
            axis2.tick_params(axis='both', which='major', labelsize=16)
            legend = ax.legend(axis_legend, fontsize=13, title = titles[k])
            legend.set_draggable(True)

            legend.get_title().set_fontsize(14)

      plt.show()
      # end_time = time.time()
      # elapsed_time = end_time - start_time
      # return elapsed_time


# ###### Run once ######

setup = setup_file.Setup('src/mapdata/', 1.0, 0.0, 0.0, True)

# IMP
# start = (-46.77546186, 25.03932639)
# goal = (-46.75064526, 25.05898353)
start = (-46.77877996828475, 25.034789363991408)
goal = (-46.75469896510251, 25.062598388586796)

# # HM
# start = (-52.99632770016827, 27.425843848099724)
# goal = (-52.85282349257713, 27.59859732093237)
# start = (-53.07859125866001, 27.384712068853858)
# goal = (-52.80437939702088, 27.587628846466806)

[start_pixel, goal_pixel] = transform.from_globe_to_pixel([start, goal], setup)

# # Define start and goal through click on map
# print('Choose start & goal by clicking with the left & right mouse button (respectively) on the image.')
# setup.maps.choose_start_and_goal_on_image()
# [start_sim, goal_sim] = transform.from_globe_to_map([setup.maps.start, setup.maps.goal], setup)
# [start_pixel, goal_pixel] = transform.from_map_to_pixel([start_sim, goal_sim], setup)

# size = 256
# faktor = size/256
outtime = run_all_combos_once(start_pixel, goal_pixel, faktor=1)

###### Create random numbers ######
# starts = [(752, 105)]
# goals = [(77, 645)]
# for i in range(4):
#       starts.append((random.randint(0, 830), random.randint(0, 830)))
#       goals.append((random.randint(0, 830), random.randint(0, 830)))
# print('starts = ', starts)
# print('goals = ', goals)

###### OUTPUT ###### 
# # # size = 1024
# faktor = 256/256
# starts = [(752, 105), (493, 606), (352, 779), (29,33), (336, 331)]
# goals = [(77, 645), (284, 401), (679, 491), (750, 812), (781, 793)]
# # print(starts)

# time_list = []
# for j in range(len(starts)):
#       print('Start & goal position ',j+1)
#       for i in range(2):
#             # Run astar
#             outtime = run_all_combos_once(starts[j], goals[j], faktor)
#             print("Running A* took ", outtime," s.")
#             time_list.append(outtime)

# print('list_'+str(size)+' =', time_list)
# print('avg_all_'+str(size)+' = ', np.average(time_list),'s')
# print('avg_'+str(size)+' = ', np.average(time_list)/18,'s')

###### Save times ######
# list_256 = [38.59761190414429,37.844971895217896,37.59815216064453,37.6522331237793,37.60393476486206,
#             37.58712458610535,37.701122999191284,37.68010354042053,37.98957633972168,37.710187911987305]

# list_64 = [2.2855284214019775, 2.245969772338867, 0.5255024433135986, 0.5179293155670166, 0.7746152877807617, 0.7830061912536621, 2.576740264892578, 2.5970940589904785, 1.9127850532531738, 1.9134125709533691]
# avg_all_64 =  1.6132583379745484 s
# avg_64 = 0.08962546322080825 s
# list_128 = [9.807166576385498, 9.32327151298523, 2.062228202819824, 1.9949331283569336, 3.1584649085998535, 3.1803598403930664, 11.201108694076538, 11.53169322013855, 7.914302587509155, 8.593668222427368]
# avg_all_128 =  6.876719689369201 s
# avg_128 = 0.38203998274273343 s
# list_256 = [38.395681381225586, 37.64828562736511, 6.560179710388184, 6.545897483825684, 11.486464977264404, 11.484886884689331, 44.283506631851196, 45.04706335067749, 30.360028505325317, 32.112184286117554]
# avg_all_256 =  26.392417883872987 s
# avg_256 = 1.4662454379929437 s
# list_512 = [157.29361772537231, 154.98153257369995, 22.674581289291382, 22.59432029724121, 46.34591794013977, 44.944191217422485, 174.7486491203308, 173.50214529037476, 124.32524681091309, 125.50176858901978]
# avg_all_512 =  104.69119708538055 s
# avg_512 =  5.816177615854475 s
# list_1024 = [622.9269869327545, 616.7375133037567, 82.14757990837097, 81.41052293777466, 177.82565236091614, 178.3453950881958, 689.0156915187836, 691.5291917324066, 506.4404728412628, 502.94163823127747]
# avg_all_1024 =  414.9320644855499 s
# avg_1024 =  23.05178136030833 s
# list_2048 = [2511.141668319702, 2484.219484567642, 315.1444809436798, 315.36807346343994, 738.645898103714, 738.1393547058105, 2848.1005952358246, 2847.8298003673553, 2042.226182937622, 2042.0088675022125]
# avg_all_2048 =  1688.2824406147004 s
# avg_2048 =  93.79346892303892 s

