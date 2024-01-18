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
from collections import defaultdict
from itertools import combinations
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist


def create_paths(scale, save_data=False):
    '''This function first creates a distribtion between the three path optimization weights and
    thereafter calculates paths for each combination'''
    # Iterate over different combinations of a, b, and c
    a_values = np.logspace(0, 1, scale)
    b_values = np.logspace(0, 1, scale)
    c_values = np.logspace(0, 1, scale)
    n = len(list(product(a_values, b_values, c_values)))-1
    
    # Define start and goal
    setup = Setup('src/mapdata/', 1.0, 0, 0, plot_global=True)
    setup.maps.choose_start_and_goal_on_image()
    start = setup.maps.start
    goal = setup.maps.goal
    # start = (-46.755803, 25.059801)
    # goal = (-46.771790, 25.041539)
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
        os.makedirs(folder_name+'/raw/')
    
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

                    file_path = os.path.join(folder_name+'/raw/', f'path{len(done_weights)}.dat')
                    np.savetxt(file_path, path_globe, delimiter='\t', fmt='%-3f')

    # Show the map with all paths
    plt.show()


def load_and_plot_paths(folder_path, show_in_one_plot=True, clustering_policy=False, n_clusters=3):
    '''This function loads all paths of a folder or all paths of three different folders. The primer
    can be used to analyse the influence of three weights at once, while the second can be used to 
    pairwise compare two of the three weights'''
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

        # Get "average" path as baseline to compare other paths to
        average_point_index = np.argmin(cdist(data[:,0:3], [[0.333333, 0.333333, 0.333333]]))
        print(f"Average path is at index {average_point_index}")

        # Perform KMeans clustering
        if clustering_policy:
            kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(np.column_stack((E_P, R_P, I_P)))
            labels = kmeans.labels_
            cluster_centers = kmeans.cluster_centers_

            ax.scatter(E_P, R_P, I_P, c=labels, cmap='viridis', marker='o')
            closest_paths = []
            all_points = data[:, 3:6]

            # Print information for each cluster
            for cluster_label, center in enumerate(cluster_centers):
                cluster_points = data[labels == cluster_label, 3:6]

                # Find the point closest to the centroid
                closest_point_index = np.argmin(cdist(all_points, [center]))
                closest_point = all_points[closest_point_index]
                closest_paths.append(closest_point_index+1)

                # Calculate variance within the cluster
                cluster_variance = np.var(cluster_points, axis=0)

                print(f"Cluster {cluster_label + 1}:")
                print(f"Number of paths in cluster: {len(cluster_points)}")
                print(f"Cluster center: {center}")
                print(f"Variance within cluster: {cluster_variance} with average of {np.average(cluster_variance)}")
                print(f"Closest point to centroid: {closest_point}")
                print(f"Weights of closest point: {data[closest_point_index,0]},{data[closest_point_index,1]},{data[closest_point_index,2]}")
                
                # compare to average path
                energysave = (data[average_point_index,3] - data[closest_point_index,3]) / data[average_point_index,3] * 100
                risksave = (data[average_point_index,4] - data[closest_point_index,4]) / data[average_point_index,4] * 100
                sciencegain = (data[closest_point_index,5] - data[average_point_index,5]) / data[average_point_index,3] * 100
                prewords = []
                if energysave>0:
                    prewords.append('less')
                else: 
                    prewords.append('more')
                if risksave>0:
                    prewords.append('less')
                else:
                    prewords.append('more')
                if sciencegain>0: 
                    prewords.append('less')
                else:
                    prewords.append('more')
                print(f"This path has {np.abs(energysave)}% "+prewords[0]+f" energy consumption, {np.abs(risksave)}% "+
                      prewords[1]+f" risk and {np.abs(sciencegain)}% "+prewords[2]+" scientific outcome than baseline.")
                print()

                # # Show ellipsoid
                # theta = np.linspace(0, np.pi, 50)
                # phi = np.linspace(0, 2 * np.pi, 100)
                # Theta, Phi = np.meshgrid(theta, phi)
                # x = cluster_variance[0] * 0.5 * np.cos(Theta) * np.sin(Phi) + center[0]
                # y = cluster_variance[1] * 0.5 * np.sin(Theta) * np.sin(Phi) + center[1]
                # z = cluster_variance[2] * 0.5 * np.cos(Theta) + center[2]

                ax.scatter(closest_point[0], closest_point[1], closest_point[2], c='red', marker='o', s=100, label='Closest Point')
        else:
            ax.scatter(E_P, R_P, I_P, c=np.column_stack((r, g, b)), marker='o')
        ax.set_xlabel('E_P')
        ax.set_ylabel('R_P')
        ax.set_zlabel('I_P')
        ax.set_title('Cost distribution')

        # Create a separate axis for the circular colormap legend
        if show_in_one_plot:
            ax_legend = fig.add_subplot(133, projection='3d')
        else:
            ax_legend = fig.add_subplot(330+(3*i+3), projection='3d')

        if clustering_policy:
            sc = ax_legend.scatter(r, g, b, c=labels, cmap='viridis', marker='o')
        else:
            sc = ax_legend.scatter(r, g, b, c=np.column_stack((r, g, b)), marker='o')
        for highlight in closest_paths:
            ax_legend.scatter(r[highlight-1], g[highlight-1], b[highlight-1], color='red', marker='o', s=100)
        ax_legend.set_xlabel('alpha')
        ax_legend.set_ylabel('beta')
        ax_legend.set_zlabel('gamma')
        ax_legend.set_title('Used colors for visualisation')
        ax_legend.view_init(elev=0, azim=45)

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
        dat_files = [file for file in os.listdir(folder_path+'/raw/') if file.endswith('.dat') if file.startswith('path')]
        for dat_file in dat_files:
            file_path = os.path.join(folder_path+'/raw/', dat_file)
            path_globe = np.loadtxt(file_path, delimiter='\t')
            path_number = int(dat_file[4:-4])-1
            if clustering_policy:
                color = sc.cmap(sc.norm(labels[path_number]))
                ax_pic.plot(path_globe[:, 0], path_globe[:, 1], color=color, linewidth=2)
            else:
                ax_pic.plot(path_globe[:, 0], path_globe[:, 1], color=[r[path_number], g[path_number], b[path_number]], linewidth=2)
        
        if clustering_policy:
            for number in closest_paths:
                path_highlight = np.loadtxt(folder_path+'/raw/path'+str(number)+'.dat', delimiter='\t')
                ax_pic.plot(path_highlight[:, 0], path_highlight[:, 1], 'r:', linewidth=2)


    # Show the plot
    # plt.show()


def plot_rgb_circle():
    '''This function plots an rgb cycle in matplotlib'''
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


def create_and_plot_distribution(num_samples):
    '''This function creates and plots several distributions that can be used to
    get more or less uniform samples between three variables'''
    # # 1
    # intervals = np.linspace(0, 1, num_samples+1)
    # a_samples = np.zeros(num_samples)
    # b_samples = np.zeros(num_samples)
    # c_samples = np.zeros(num_samples)

    # for i in range(num_samples):
    #     a_samples[i] = np.random.uniform(intervals[i], intervals[i+1])
    #     b_samples[i] = np.random.uniform(0, 1 - a_samples[i])
    #     c_samples[i] = 1 - a_samples[i] - b_samples[i]

    # # 2
    # a_values = np.linspace(0, 1, num_samples)
    # b_values = np.linspace(0, 1, num_samples)
    # c_values = np.linspace(0, 1, num_samples)
    # samples = []
    # i = 0

    # for a, b, c in product(a_values, b_values, c_values):
    #     if a+b+c!=0:
    #         [a_samples,b_samples,c_samples] = [a,b,c]/(a+b+c)
    #         samples.append((a_samples,b_samples,c_samples))
    # a_samples, b_samples, c_samples = zip(*samples)

    # 3
    a_values = np.logspace(0, 1, num_samples)
    b_values = np.logspace(0, 1, num_samples)
    c_values = np.logspace(0, 1, num_samples)
    samples = []
    i = 0

    for a, b, c in product(a_values, b_values, c_values):
        if a+b+c!=0:
            [a_samples,b_samples,c_samples] = [a,b,c]/(a+b+c)
            samples.append((a_samples,b_samples,c_samples))
    a_samples, b_samples, c_samples = zip(*samples)

    # Create a 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(a_samples, b_samples, c_samples, c=np.column_stack((a_samples, b_samples, c_samples)), marker='o')
    ax.set_xlabel('a')
    ax.set_ylabel('b')
    ax.set_zlabel('c')
    plt.show()


def sort_paths(folder_path):
    '''Sorts through all paths and outputs dict with sorted paths'''
    ### Kick out doubles ###
    files = [file for file in os.listdir(folder_path) if file.endswith('.dat') and file.startswith('path')]
    grouped_paths = defaultdict(list)

    for file in files:
        # Load coordinates from the file and use hashable representation of coordinates as a key
        file_path = os.path.join(folder_path, file)
        coordinates = np.loadtxt(file_path, delimiter='\t')
        key = tuple(map(tuple, coordinates))
        
        # Append the file to the corresponding path group
        path_number = int(file[4:-4])  # Extract the path number from the file name
        grouped_paths[key].append(path_number)

    # Filter out single paths (those that don't have duplicates)
    i = 0
    for keys, paths in grouped_paths.items():
        i = i+1
        print(f"Group {i}: Grouped paths {paths}")

    return grouped_paths


def group_paths(grouped_paths):
    ### Group similar paths ###
    similar_paths_dict = defaultdict(list)
    checked_paths = []
    distributed_paths = []

    # Iterate through each combination of paths
    for (key1, paths1), (key2, paths2) in combinations(grouped_paths.items(), 2):
        # Check if key2 was already checked
        if key1 in distributed_paths or key2 in distributed_paths:
            continue
        if key1 not in checked_paths:
            # Create dict entry
            similar_paths_dict[key1].extend(paths1)
            checked_paths.append(key1)
        
        # Calculate Jaccard similarity
        intersection_size = len(set(key1) & set(key2))
        union_size = len(set(key1) | set(key2))
        jaccard_similarity = intersection_size / union_size if union_size != 0 else 0

        # If Jaccard similarity is above the threshold (e.g., 0.9 for 90% overlap)
        if jaccard_similarity >= 0.8:
            distributed_paths.append(key2)
            similar_paths_dict[key1].extend(paths2)

    similar_paths = {index+1: paths for index, (key, paths) in enumerate(similar_paths_dict.items())}
    return similar_paths

if __name__ == '__main__':
    # PREP
    # plot_rgb_circle()
    # create_and_plot_distribution(10)

    # CALC PATHS
    # create_paths(10, True)

    # SORT PATHS
    # grouped_paths = sort_paths('src/globalplanner/data/124_log/raw/')
    # similar_paths = group_paths(grouped_paths)
    # for group_number, paths in similar_paths.items():
    #     print(f"Group {group_number}: Similar paths {paths}")

    # PLOT PATHS AND STATS
    # load_and_plot_paths('src/globalplanner/data/1000', show_in_one_plot=False)
    # load_and_plot_paths('src/globalplanner/data/1000_log', show_in_one_plot=True)
    load_and_plot_paths('src/globalplanner/data/1000_log_scew', show_in_one_plot=True,
                        clustering_policy=True, n_clusters=5)
    plt.show()

