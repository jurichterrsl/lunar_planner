import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from mapdata.setup_aristarchus import Setup
from globalplanner import transform, astar
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import colors
import colorsys
import matplotlib.image as mpimg
import os
from datetime import datetime


def create_paths(scale, save_data=False):
    # Iterate over different combinations of a, b, and c
    a_values = np.linspace(0, 1, scale)
    b_values = np.linspace(0, 1, scale)
    c_values = np.linspace(0, 1, scale)
    n = len(list(product(a_values, b_values, c_values)))-1
    
    # Define start and goal
    setup = Setup('src/mapdata/', 1.0, 0, 0, plot_global=True)
    # setup.maps.choose_start_and_goal_on_image()
    # start = setup.maps.start
    # goal = setup.maps.goal
    start = (-46.755803, 25.059801)
    goal = (-46.771790, 25.041539)
    [start_sim, goal_sim] = transform.from_globe_to_sim([start, goal], setup)
    [start_pixel, goal_pixel] = transform.from_sim_to_pixel([start_sim, goal_sim], setup)
    
    # Plot image
    plt.close()
    _, ax = plt.subplots()
    ax.imshow(setup.maps.map_image, extent=setup.maps.extent, aspect=setup.maps.aspect_ratio, alpha=0.5)
    done_weights = []

    # Prepare folder to save paths
    if save_data:
        folder_name = 'src/globalplanner/data/'+datetime.now().strftime('%d%m%Y_%H%M')
        os.makedirs(folder_name)
    
    i=0
    for a, b, c in product(a_values, b_values, c_values):
        if a+b+c!=0:
            # Status
            i += 1
            print("Calculation "+str(i)+"/"+str(n))
            [a,b,c] = [a,b,c]/(a+b+c)

            if [a,b,c] not in done_weights:
                done_weights.append([a,b,c])

                # Load setup file
                setup = Setup('src/mapdata/', a, b, c, plot_global=True)

                # Run A* algorithm
                path, stats = astar.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup.h_func, setup.g_func, allow_diagonal=True)
                path_globe = transform.from_pixel_to_globe(path, setup)
                ax.plot(path_globe[:,0], path_globe[:,1], 'red', linewidth=2)

                # Save sum of stats to file
                if save_data:
                    stats_sum = np.sum(stats, axis=0, where=[1, 1, 1, 1, 1, 1])
                    if i==1:
                        with open(folder_name+'/stats.dat', 'w') as file:
                            stats_header = '\t\t'.join(('a', 'b', 'c', 'E_P', 'R_P', 'I_P', 'B_P', 'g_func', 'h_func'))
                            file.write(stats_header + '\n')
                    
                    # save stats and path coordinates
                    with open(folder_name+'/stats.dat', 'a') as file:
                        stats_with_weights = np.hstack([a,b,c,stats_sum])
                        np.savetxt(file, [stats_with_weights], comments='', delimiter='\t', fmt='%-3f')

                    file_path = os.path.join(folder_name, f'path{len(done_weights)}.dat')
                    np.savetxt(file_path, path_globe, delimiter='\t', fmt='%-3f')

    # Show the map with all paths
    plt.show()


def load_and_plot_paths(folder_path, show_in_one_plot=True):
    if show_in_one_plot:
        folder_path_list = [folder_path]
    else:
        folder_path_list = [folder_path+'_ab',
                            folder_path+'_ac',
                            folder_path+'_bc']

    fig = plt.figure()
    for i, folder_path in enumerate(folder_path_list):
        # Load stats from the file
        data = np.loadtxt(folder_path+'/stats.dat', skiprows=1)

        # Extract columns
        r = data[:, 0]
        g = data[:, 1]
        b = data[:, 2]
        E_P = data[:, 3]
        R_P = data[:, 4]
        I_P = data[:, 5]

        # Create a 3D plot
        if show_in_one_plot:
            ax = fig.add_subplot(132, projection='3d')
        else:
            ax = fig.add_subplot(330+(3*i+2), projection='3d')

        # Scatter plot
        sc = ax.scatter(E_P, R_P, I_P, c=np.column_stack((r, g, b)), marker='o')
        ax.set_xlabel('E_P')
        ax.set_ylabel('R_P')
        ax.set_zlabel('I_P')
        ax.set_title('Cost distribution')

        # Create a separate axis for the circular colormap legend
        if show_in_one_plot:
            ax_legend = fig.add_subplot(133, projection='3d')
        else:
            ax_legend = fig.add_subplot(330+(3*i+3), projection='3d')

        ax_legend.scatter(r, g, b, c=np.column_stack((r, g, b)), marker='o')
        ax_legend.set_xlabel('alpha')
        ax_legend.set_ylabel('beta')
        ax_legend.set_zlabel('gamma')
        ax_legend.set_title('Used colors for visualisation')

        # Prepare tp plot paths
        if show_in_one_plot:
            ax_pic = fig.add_subplot(131)
        else:
            ax_pic = fig.add_subplot(330+(3*i+1))
        
        setup = Setup('src/mapdata/', 1.0, 0, 0, plot_global=True)
        ax_pic.imshow(setup.maps.map_image, extent=setup.maps.extent, aspect=setup.maps.aspect_ratio, alpha=0.5)
        ax_pic.set_title('Paths')
        ax_pic.set_xlabel('LON')
        ax_pic.set_ylabel('LAT')

        # Get folder to all paths and loop through each .dat file to plot the path
        dat_files = [file for file in os.listdir(folder_path) if file.endswith('.dat') if file.startswith('path')]
        for dat_file in dat_files:
            file_path = os.path.join(folder_path, dat_file)
            path_globe = np.loadtxt(file_path, delimiter='\t')

            # Plot in right color
            path_number = int(dat_file[4:-4])-1
            ax_pic.plot(path_globe[:, 0], path_globe[:, 1], color=[r[path_number], g[path_number], b[path_number]], linewidth=2)

    # Show the plot
    # plt.show()


def plot_rgb_circle():
    fig = plt.figure()
    ax = fig.add_subplot(projection='polar')

    rho = np.linspace(0,1,100) # Radius of 1, distance from center to outer edge
    phi = np.linspace(0, np.pi*2.,1000 ) # in radians, one full circle

    RHO, PHI = np.meshgrid(rho,phi) # get every combination of rho and phi

    h = (PHI-PHI.min()) / (PHI.max()-PHI.min()) # use angle to determine hue, normalized from 0-1
    h = np.flip(h)        
    s = RHO               # saturation is set as a function of radias
    v = np.ones_like(RHO) # value is constant

    # convert the np arrays to lists. This actually speeds up the colorsys call
    h,s,v = h.flatten().tolist(), s.flatten().tolist(), v.flatten().tolist()
    c = [colorsys.hsv_to_rgb(*x) for x in zip(h,s,v)]
    c = np.array(c)

    ax.scatter(PHI, RHO, c=c)
    _ = ax.axis('off')

    plt.show()


if __name__ == '__main__':
    # plot_rgb_circle()
    #create_paths(10, True)
    load_and_plot_paths('src/globalplanner/data/1000', False)
    load_and_plot_paths('src/globalplanner/data/1000', True)
    plt.show()