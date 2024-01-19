
from globalplanner import astar, transform
from mapdata import setup_aristarchus 


# Load setup file
setup = setup_aristarchus.Setup('src/mapdata/', 0.5, 0.0, 0.5, plot_global=True)

# Define start and goal manually
start = (-46.75458, 25.03874) #(longitude, latitude)
goal = (-46.77286, 25.05064) #(longitude, latitude)
[start_sim, goal_sim] = transform.from_globe_to_sim([start, goal], setup)
[start_pixel, goal_pixel] = transform.from_sim_to_pixel([start_sim, goal_sim], setup)

# Define start and goal through click on map
print('Choose start & goal by clicking with the left & right mouse button (respectively) on the image.')
setup.maps.choose_start_and_goal_on_image()
[start_sim, goal_sim] = transform.from_globe_to_sim([setup.maps.start, setup.maps.goal], setup)
[start_pixel, goal_pixel] = transform.from_sim_to_pixel([start_sim, goal_sim], setup)

# Run A* algorithm
path, stats = astar.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup.h_func, setup.g_func, allow_diagonal=True)

# Show result
path_globe = transform.from_pixel_to_globe(path, setup)
setup.maps.show_image_with_path(path_globe)

