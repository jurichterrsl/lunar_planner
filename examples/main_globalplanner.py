
from globalplanner import astar, transform
from mapdata import setup_aristarchus_hm as setup_file
import matplotlib.pyplot as plt
import numpy as np


# Load setup file
setup = setup_file.Setup('src/mapdata/', 0.0, 1.0, 0.0, plot_global=True)
# setup.maps.plot_four_layers_in_pixel([])
# setup.maps.plot_layers([0,1,2],[True,False,False])
# setup.maps.show_image()

# Define start and goal manually
# start = (-46.75458, 25.03874) #(longitude, latitude)
# goal = (-46.77286, 25.05064) #(longitude, latitude)
# [start_sim, goal_sim] = transform.from_globe_to_map([start, goal], setup)
start_sim, goal_sim = (6000.0, 4000.0), (12000.0, 8000.0)
[start_pixel, goal_pixel] = transform.from_map_to_pixel([start_sim, goal_sim], setup)

# # Define start and goal through click on map
# print('Choose start & goal by clicking with the left & right mouse button (respectively) on the image.')
# setup.maps.choose_start_and_goal_on_image()
# [start_sim, goal_sim] = transform.from_globe_to_map([setup.maps.start, setup.maps.goal], setup)
# [start_pixel, goal_pixel] = transform.from_map_to_pixel([start_sim, goal_sim], setup)

# Run A* algorithm
path, stats = astar.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup, allow_diagonal=True, show_all_visited_nodes=True)

if stats[0]!=-1:
    # Save stats to file
    header = '\t\t'.join(('E_P', 'R_P', 'I_P', 'B_P', 'g_func', 'h_func'))
    stats_with_wp = np.vstack((stats, np.sum(stats, axis=0)))
    np.savetxt('src/globalplanner/data/stats.dat', stats_with_wp, header=header, comments='', delimiter='\t', fmt='%-3f')

    # Print some stats
    results = np.sum(stats, axis=0)
    E_star = results[0] * setup.Emax
    energy = E_star

    risk_list = np.array(stats)[:,1]
    crash = 1
    for R_cost in risk_list:
        R_star = R_cost * setup.Rmax
        crash_single = 1 - (1-R_star)**(8/setup.maps.pixel_size)
        crash = crash * (1-crash_single)
    risk = 1-crash

    science = 1 - abs(results[2])/len(path)
    banned = results[3]/len(path)

    print('The complete energy consumption is '+str(round(energy/1000,2))+' kNm^2.')
    print('The taken risk is '+str(round(risk*100,6))+' %.')
    print('The scientific outcome is '+str(round(science*100,2))+' % of what would have been possible on the same path length.')
    print('')

    # Show result
    plt.close()
    path_globe = transform.from_pixel_to_globe(path, setup)
    # setup.maps.plot_layers_with_path([1],[False],path_globe)
    # setup.maps.show_8plots_with_path(path_globe, path, [path_globe[0], path_globe[len(path_globe)-1]])
    setup.maps.show_image_with_path(path_globe)
