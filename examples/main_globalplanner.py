
from globalplanner import astar, transform
from mapdata import setup_aristarchus 
import matplotlib.pyplot as plt
import numpy as np


# Load setup file
setup = setup_aristarchus.Setup('src/mapdata/', 0.6, 0.0, 0.4, plot_global=True)

# Define start and goal manually
start = (-46.75458, 25.03874) #(longitude, latitude)
goal = (-46.77286, 25.05064) #(longitude, latitude)
[start_sim, goal_sim] = transform.from_globe_to_map([start, goal], setup)
[start_pixel, goal_pixel] = transform.from_map_to_pixel([start_sim, goal_sim], setup)

# Define start and goal through click on map
#print('Choose start & goal by clicking with the left & right mouse button (respectively) on the image.')
#setup.maps.choose_start_and_goal_on_image()
#[start_sim, goal_sim] = transform.from_globe_to_map([setup.maps.start, setup.maps.goal], setup)
#[start_pixel, goal_pixel] = transform.from_map_to_pixel([start_sim, goal_sim], setup)

# Run A* algorithm
path, stats = astar.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup, allow_diagonal=True)

if stats[0]!=-1:
    # Print some stats
    results = np.sum(stats, axis=0)
    energy = results[0] * 345 * 3.255
    risk = 1 - (1-results[1]*(1-(1-0.01512)**(3.255/8)))**(8/3.255)
    science = 1 - results[2]/len(path)
    banned = results[3]/len(path)
    print('The complete energy consumption is '+str(round(energy/1000,2))+' kNm^2.')
    print('The taken risk is '+str(round(risk*100,2))+' %.')
    print('The scientific outcome is '+str(round(science*100,2))+' % of what would have been possible on the same path length.')
    print('')

    # Show result
    plt.close()
    path_globe = transform.from_pixel_to_globe(path, setup)
    setup.maps.show_image_with_path(path_globe)
    #setup.maps.show_8plots_with_path(path_globe, path, [])
