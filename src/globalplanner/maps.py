""" This file loads and analyses geotiff data.
It saves the different map layers into an array, which can be imported by the setup.py file """

### modules
import sys
import numpy as np
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import ticker, colors
import globalplanner.transform as transform
import rasterio as rs
import math


class Maps:
    """
    A class to create and change the map.
    
    Attributes and Methods can be seen in the class diagram by running 'pyreverse -o png \
        path/to/src/globalplanner'
    """

    # DEFAULT_CMAP = colors.LinearSegmentedColormap.from_list\
    #     ("", ["darkslategray","mediumturquoise",'#c9a687','#a6611a'])
    DEFAULT_CMAP = 'viridis'
    
    def __init__(self, map_size, n_layers, init_filename, map_picture, layer_description, plot_global=True, plot_pixel=False):
        ''' 
        Initialize object map
            Parameters:
                map_size ((int, int)): n_pixel_width and n_pixel_height
                n_layers (int): final number of layers of the map
                init_filename(String): the first tif-file to initiate the map; following tif \
                    files have to be at the same location on the map
                map_picture(String): if picture of map is available, put filename here
                layer_description (list[int]): List with Strings to describe the first added layers
                plot_global (Boolean): if plots are plotted in global (usually LON & LAT) or \
                    local coordinates (x=(0,width), y=(0,height))
        '''
        self.n_px_width, self.n_px_height = map_size
        self.n_layers = n_layers

        # define extent of maps from one tif example
        self.xmin, self.ymin, self.xmax, self.ymax, self.width, self.height = \
            self.define_corners(init_filename)
        print(self.xmin, self.ymin, self.xmax, self.ymax)
        self.pixel_size = self.width / self.n_px_width
        if plot_global:
            self.extent = (self.xmin, self.xmax, self.ymin, self.ymax)
            self.aspect_ratio = abs(self.xmax-self.xmin) / abs(self.ymax-self.ymin) * \
                                self.n_px_height / self.n_px_width
        else:
            self.extent = (0, self.width, 0, self.height)
            self.aspect_ratio = 'equal'

        # initalize a list of strings as a look-up which kind of data is saved in which layer of \
        # the array
        self.layer_names = []
        
        # initialize the maps array, where all map data is saves
        self.maps_array = np.zeros((self.n_px_width, self.n_px_height, self.n_layers))

        # append the first geotif to array
        self.extract_geotiff_and_add_to_array(init_filename, layer_description)

        # load image if image is available
        if map_picture!="":
            self.map_image = mpimg.imread(map_picture)
        else:
            self.map_image = None

        # Save clicked points as start or goal
        self.start = (0, 0)
        self.goal = (0, 0)


    def define_corners(self, init_filename):
        '''
        Creates an array with the first map layer and additionally saves the corners of the map \
        in globe-coordinates; should only be called once when initializing the object
            Parameters:
                init_finename (String): path to first geotif (can be any of the wanted)
            Returns:
                xmin (float)
                ymin (float)
                xmax (float)
                ymax (float)
                width (float)
                height (float)
        '''
        # open tif file
        dataset = rs.open(init_filename)

        # get width and height in m
        width = dataset.bounds.right - dataset.bounds.left
        height = dataset.bounds.top - dataset.bounds.bottom

        # Get reference lon & lat
        crs_dict = dataset.crs.to_dict()
        lonref = crs_dict['lon_0']
        latref = crs_dict['lat_0']
        radius = crs_dict['R']

        # Get extent of geotiff file
        lonmin = lonref - width / 2 * 180 / math.pi / radius
        lonmax = lonref + width / 2 * 180 / math.pi / radius
        latmin = latref - height / 2 * 180 / math.pi / radius
        latmax = latref + height / 2 * 180 / math.pi / radius

        return lonmin, latmin, lonmax, latmax, width, height


    def extract_geotiff_and_add_to_array(self, filename, description):
        '''
        Extracts one or several geotiff layers from a file and adds them as one or \
        respectively several rows into the array
            Parameters:
                filename (String): path to geotif file
        '''
        # load geotiff file
        dataset = rs.open(filename)

        # check how many layers are already in the array:
        n_layers_inscribed = len(self.layer_names)
        # check if user tries to input too many layers
        if n_layers_inscribed+dataset.count > self.n_layers:
            print("ERROR: The maps_array has "+str(self.n_layers)+" layers, where each of them is \
                  already filled.")
            sys.exit()
        if (dataset.width != self.n_px_width) or (dataset.height != self.n_px_height):
            for band in range(dataset.count):
                raster_band = dataset.read(band+1)
                # New size n, resize factor m
                m = self.n_px_width/dataset.width
                if m>=1:
                    # make array bigger
                    m = int(m)
                    n = dataset.width
                    resized_array = np.zeros((m*n, m*n), dtype=raster_band.dtype)
                    for i in range(n):
                        for j in range(n):
                            resized_array[i*m:(i+1)*m, j*m:(j+1)*m] = raster_band[i, j]
                else:
                    # make array smaller
                    m = int(1/m)
                    n = self.n_px_width
                    reshaped_array = raster_band.reshape(n, m, n, m)
                    resized_array = np.mean(reshaped_array, axis=(1,3))

                self.layer_names.append(raster_band.GetDescription())
                self.maps_array[:, :, band+n_layers_inscribed] = \
                    np.transpose(resized_array)
        else:
            # extract the types from the geotif and save geotif data as an array
            for band in range(dataset.count):
                raster_band = dataset.read(band+1)
                self.layer_names.append(description[band])
                self.maps_array[:, :, band+n_layers_inscribed] = \
                    np.transpose(np.array(raster_band))
        

    def load_npy_file_and_add_to_array(self, filename, description):
        '''
        Loads a npy file and saves it to the maps_array
            Parameters:
                filename (String): path to npy file
                description (String): will be added to the layer_names list and should describe \
                the new layer
        '''
        loaded_arr = np.load(filename)

        # check how many layers are already in the array:
        n_layers_inscribed = len(self.layer_names)
        # check if user tries to input too many layers
        if n_layers_inscribed+1 > self.n_layers:
            print("ERROR: The maps_array has "+str(self.n_layers)+" layers, where each of them is \
                  already filled.")
            sys.exit()
        if (loaded_arr.shape[0] != self.n_px_height) or (loaded_arr.shape[1] != self.n_px_width):
            print("ERROR: The raster size of this file ("+str(loaded_arr.shape[0])+","\
                  +str(loaded_arr.shape[1])+") does not fit the array size of the map ("\
                    +str(self.n_px_height)+","+str(self.n_px_width)+").")
            sys.exit()

        self.layer_names.append(description)
        self.maps_array[:, :, n_layers_inscribed] = np.transpose(loaded_arr)


    def get_slope_from_height(self, heightmap):
        '''
        Returns the maximal slope between one pixel and its 8 neighboring pixel 
        numpy array
            Parameters:
                heightmap (ndarray): 2D array
            Return:
                slopemap (ndarray): 2D array with same size as input size
        '''
        distance = np.sqrt((np.gradient(heightmap, axis=0)/10) ** 2 + (np.gradient(heightmap, axis=1)/10) ** 2)
        slopemap = np.degrees(np.arctan(distance))

        return slopemap


    def plot_layers(self, layers, is_height_map, colormap='viridis'):
        '''
        plots one or several layers of the maps
            Parameters:
                layers (int[]): which layer is to be plotted (from 0 to n_array-1)
                is_height_map (boolean[]): setting this to true for the respective layer activates \
                height lines
                colormap (String)
        '''
        for i in range(len(layers)):
            plot_map = self.maps_array[:,:,layers[i]]
            _, axs = plt.subplots()
            img = plt.imshow(plot_map.T, cmap=colormap,
                             extent=self.extent,
                             aspect = self.aspect_ratio)
            if is_height_map[i]:
                plt.contour(np.flip(plot_map.T, axis=0), levels=9, colors='#000000', linestyles='solid', \
                            linewidths=1, extent=self.extent)
            cbar = plt.colorbar(img)
            axs.set_xlabel('LON')
            axs.set_ylabel('LAT')
            #axs.set_xticklabels([f"{val:.{4}f}" for val in axs.get_xticks()])
            #axs.set_yticklabels([f"{val:.{4}f}" for val in axs.get_yticks()])
            cbar.ax.set_ylabel(self.layer_names[layers[i]])
        plt.show()
    

    def plot_five_layers(self, path):
        '''
        Plot 5 layers, where first is height map, plus the image of the map
            Parameters:
                path (ndarray): 2D Array of size (n,2) with the path coordinates. Can be an 
                empty list in case no path should be plotted.
        '''
        if len(self.layer_names) != 5:
            print("ERROR: There are "+str(len(self.layer_names))+" layers in the array. \
                  This function only works for 5 layers.")
            sys.exit()

        colormap='viridis'
        #colormap=self.DEFAULT_CMAP

        # Copy array to use in function
        plotting_array = self.maps_array


        # Plot layers of array
        cols = 2 #2 for rqt
        rows = 3 #3 for rqt
        fig, axs = plt.subplots(rows, cols)
        fig.tight_layout(h_pad=0.1, w_pad=0.2)
        n = 0
        for i in range(rows):
            for j in range(cols):
                if n<5:
                    if n==2:
                        img = axs[i, j].imshow(plotting_array[:, :, n].T, cmap=colormap,
                                            extent=self.extent, aspect = self.aspect_ratio,
                                            vmin=0.0, vmax=0.01)
                    else:
                        img = axs[i, j].imshow(plotting_array[:, :, n].T, cmap=colormap,
                                            extent=self.extent, aspect = self.aspect_ratio)
                    if n==0:
                        axs[0, 0].contour(np.flip(self.maps_array[:,:,0].T, axis=0), 
                                          levels=20, colors='#000000', linestyles='solid', linewidths=1,
                                          extent=self.extent)

                    cbar = plt.colorbar(img, ax=axs[i, j])
                    cbar.ax.tick_params(labelsize=26)
                if n==0:
                    cbar.set_label('m', fontsize=26)
                if n==1:
                    cbar.set_label('deg', fontsize=26)
                if n==2:
                    cbar.set_label('', fontsize=26)
                if n==3:
                    cbar.set_label('100%', fontsize=26)
                if n==4:
                    cbar.set_label('', fontsize=26)  
                try:
                    axs[i, j].plot(path[:,0], path[:,1], 'r')
                except:
                    pass 
                n=n+1

        # Plot image in last plot
        # axs[1, 2].imshow(self.map_image, extent=self.extent,
        #                      aspect = self.aspect_ratio)
        axs[2, 1].imshow(self.map_image, extent=self.extent,
                              aspect = self.aspect_ratio)

        # # Add titles and axes
        # axs[0, 0].set_title('Height map', fontsize=26)
        # axs[0, 1].set_title('Slope', fontsize=26)
        # axs[0, 2].set_title('Traversability score', fontsize=26)
        # axs[1, 0].set_title('Scientific interest', fontsize=26)
        # axs[1, 1].set_title('Banned areas', fontsize=26)
        # axs[1, 2].set_title('Satellite Image', fontsize=26)

        axs[0, 0].set_title('Height map', fontsize=26)
        axs[0, 1].set_title('Slope', fontsize=26)
        axs[1, 0].set_title('Rock abundance', fontsize=26)
        axs[1, 1].set_title('Scientific interest', fontsize=26)
        axs[2, 0].set_title('Banned areas', fontsize=26)
        axs[2, 1].set_title('Satellite Image', fontsize=26)

        for ax in axs.flat:
            if self.extent[0]!=0:
                ax.set_xlabel('LON', fontsize=26)
                ax.set_ylabel('LAT', fontsize=26)
                ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
                ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
                ax.xaxis.set_major_locator(ticker.MaxNLocator(3))
                ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
                ax.tick_params(axis='both', which='major', labelsize=23)
            else:
                ax.set_xlabel('x [m]', fontsize=26)
                ax.set_ylabel('y [m]', fontsize=26)
                ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
                ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
                ax.tick_params(axis='both', which='major', labelsize=23)
        plt.show()


    def plot_four_layers_in_pixel(self, path):
        # Copy array to use in function
        plotting_array = self.maps_array

        # Plot layers of array
        cols = 4 #2 for rqt
        rows = 1 #3 for rqt
        fig, axs = plt.subplots(rows, cols)
        fig.tight_layout(h_pad=0.56, w_pad=0.2)
        fig.set_size_inches((20, 6))
        n = 0
        for i in range(rows):
            for j in range(cols):
                if n==2:
                    img = axs[j].imshow(plotting_array[:, :, n].T,
                                           extent=(0,self.n_px_width,0,self.n_px_height), aspect = 'equal',
                                           vmin=0.0, vmax=0.01)
                else:
                    img = axs[j].imshow(plotting_array[:, :, n].T,
                                           extent=(0,self.n_px_width,0,self.n_px_height), aspect = 'equal')
                if n==0:
                    axs[0].contour(np.flip(self.maps_array[:,:,0].T, axis=0), 
                                      levels=20, colors='#000000', linestyles='solid', linewidths=1,
                                      extent=(0,self.n_px_width,0,self.n_px_height))
                try:
                    axs[j].plot(path[:,0], path[:,1], 'r', linewidth=3)
                except:
                    pass 
                n=n+1

        # Add titles and axes
        axs[0].set_title('Height map', fontsize=26)
        axs[1].set_title('Slope', fontsize=26)
        axs[2].set_title('Traversability score', fontsize=26)
        axs[3].set_title('Scientific interest', fontsize=26)

        for ax in axs.flat:
            ax.set_xlabel('x [Pixel]', fontsize=26)
            ax.set_ylabel('y [Pixel]', fontsize=26)
            # ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
            # ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
            ax.tick_params(axis='both', which='major', labelsize=24)
        plt.show()


    def show_8plots_with_path(self, path, path_pixel, intermediate_goals=[]):
        # Copy array to use in function
        plotting_array = self.maps_array

        # Plot layers of array
        cols = 2
        rows = 4
        fig, axs = plt.subplots(rows, cols)
        fig.tight_layout(h_pad=0.3, w_pad=0.2)
        cbar_label = ['[m]', '[deg]', '', '']
        plt.subplots_adjust(left=0.02, bottom=0.06, right=0.95, top=0.96, wspace=0.45, hspace=0.55)

        for i, ax in enumerate(axs.flat):
            if i%2==0:
                # Change colormap for traversability score
                if i==4:
                    img = ax.imshow(plotting_array[:, :, i//2].T, cmap='viridis',
                                    extent=self.extent, aspect=self.aspect_ratio,
                                    vmin=0.0, vmax=0.01)
                # Plot base for other layers
                else:
                    img = ax.imshow(plotting_array[:, :, i//2].T, cmap='viridis',
                                extent=self.extent, aspect=self.aspect_ratio)
                ax.set_xlabel("x [m]", fontsize=26)
                ax.set_ylabel("y [m]", fontsize=26)
                ax.tick_params(axis='both', which='major', labelsize=22)
                cbar = plt.colorbar(img, ax=ax)
                cbar.ax.set_ylabel(cbar_label[i//2], fontsize=22)
                cbar.ax.tick_params(labelsize=22)

                # Add contour for height map
                if i==0:
                    axs[0, 0].contour(np.flip(plotting_array[:,:,0].T, axis=0), levels=20, colors='#000000',
                                            linestyles='solid', linewidths=1, extent=self.extent)
                # Add path
                ax.plot(path[:,0], path[:,1], 'red', linewidth=3)
                ax.plot(intermediate_goals[:,0], intermediate_goals[:,1], linestyle='none', marker='o', color='red', markersize=10)
            else:
                # Calculate and output length
                pairwise_distances = np.linalg.norm(path[1:] - path[:-1], axis=1)
                total_length = np.sum(pairwise_distances)

                # Prepare scaled x axis
                num_points = len(path)
                scaled_x = np.linspace(0, total_length, num_points)

                # Plot
                ax.plot(scaled_x, plotting_array[path_pixel[:,0], path_pixel[:,1], i//2], linewidth=3)
                ax.tick_params(axis='both', which='major', labelsize=22)

        # Add titles and axes
        axs[0, 0].set_title('Height map',fontsize=26)
        axs[0, 1].set_title('Height profile',fontsize=26)
        axs[1, 0].set_title('Slope map',fontsize=26)
        axs[1, 1].set_title('Slope profile',fontsize=26)
        axs[2, 0].set_title('Traversability map',fontsize=26)
        axs[2, 1].set_title('Traversability profile',fontsize=26)
        axs[3, 0].set_title('Scientific interest map',fontsize=26)
        axs[3, 1].set_title('Scientific interest profile',fontsize=26)

        axs[0, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[0, 1].set_ylabel("Height [m]", fontsize=26)
        axs[1, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[1, 1].set_ylabel("Slope [deg]", fontsize=26)
        axs[2, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[2, 1].set_ylabel("Rock abundance", fontsize=26)
        axs[3, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[3, 1].set_ylabel("Scientific value", fontsize=26)

        plt.show()


    def show_10plots_with_path(self, path, path_pixel, intermediate_goals=[]):
        # Copy array to use in function
        plotting_array = self.maps_array

        # Plot layers of array
        cols = 2
        rows = 5
        fig, axs = plt.subplots(rows, cols)
        fig.tight_layout(h_pad=0.3, w_pad=0.2)
        cbar_label = ['[m]', '[deg]', '', '', '']
        plt.subplots_adjust(left=0.02, bottom=0.06, right=0.95, top=0.96, wspace=0.45, hspace=0.55)

        for i, ax in enumerate(axs.flat):
            if i%2==0:
                # Change colormap for traversability score
                if i==4:
                    img = ax.imshow(plotting_array[:, :, i//2].T, cmap='viridis',
                                    extent=self.extent, aspect=self.aspect_ratio,
                                    vmin=0.0, vmax=0.01)
                # Plot base for other layers
                else:
                    img = ax.imshow(plotting_array[:, :, i//2].T, cmap='viridis',
                                extent=self.extent, aspect=self.aspect_ratio)
                ax.set_xlabel("x [m]", fontsize=26)
                ax.set_ylabel("y [m]", fontsize=26)
                ax.tick_params(axis='both', which='major', labelsize=22)
                cbar = plt.colorbar(img, ax=ax)
                cbar.ax.set_ylabel(cbar_label[i//2], fontsize=22)
                cbar.ax.tick_params(labelsize=22)

                # Add contour for height map
                if i==0:
                    axs[0, 0].contour(np.flip(plotting_array[:,:,0].T, axis=0), levels=20, colors='#000000',
                                            linestyles='solid', linewidths=1, extent=self.extent)
                # Add path
                ax.plot(path[:,0], path[:,1], 'red', linewidth=3)
                ax.plot(intermediate_goals[:,0], intermediate_goals[:,1], linestyle='none', marker='o', color='red', markersize=10)
            else:
                # Calculate and output length
                pairwise_distances = np.linalg.norm(path[1:] - path[:-1], axis=1)
                total_length = np.sum(pairwise_distances)

                # Prepare scaled x axis
                num_points = len(path)
                scaled_x = np.linspace(0, total_length, num_points)

                # Plot
                ax.plot(scaled_x, plotting_array[path_pixel[:,0], path_pixel[:,1], i//2], linewidth=3)
                ax.tick_params(axis='both', which='major', labelsize=22)

        # Add titles and axes
        axs[0, 0].set_title('Height map',fontsize=26)
        axs[0, 1].set_title('Height profile',fontsize=26)
        axs[1, 0].set_title('Slope map',fontsize=26)
        axs[1, 1].set_title('Slope profile',fontsize=26)
        axs[2, 0].set_title('Traversability map',fontsize=26)
        axs[2, 1].set_title('Traversability profile',fontsize=26)
        axs[3, 0].set_title('Scientific interest map',fontsize=26)
        axs[3, 1].set_title('Scientific interest profile',fontsize=26)
        axs[4, 0].set_title('Banned map',fontsize=26)
        axs[4, 1].set_title('Banned profile',fontsize=26)

        axs[0, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[0, 1].set_ylabel("Height [m]", fontsize=26)
        axs[1, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[1, 1].set_ylabel("Slope [deg]", fontsize=26)
        axs[2, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[2, 1].set_ylabel("Rock abundance", fontsize=26)
        axs[3, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[3, 1].set_ylabel("Scientific value", fontsize=26)
        axs[4, 1].set_xlabel("Distance [m]", fontsize=26)
        axs[4, 1].set_ylabel("Banned area", fontsize=26)

        plt.show()



    def plot_layers_with_path(self, layers, is_height_map, path):
        '''
        Plots one or several layers of the maps plus the calculated path
            Parameters:
                layers (int[]): which layer is to be plotted (from 0 to n_array-1)
                is_height_map (boolean[]): setting this to true for the respective layer activates \
                height lines
                path (ndarray): 2D array of dimension (2,n) or rsp. length n (if tupellist)
        '''
        if isinstance(path, np.ndarray):
            pass
        elif isinstance(path, list):
            path = transform.tupellist_to_array(path)
        else:
            raise TypeError("Invalid type for 'path'. Must be a NumPy array or a list of tuples.")

        for i in range(len(layers)):
            plot_map = self.maps_array[:,:,layers[i]]
            _, axs = plt.subplots()
            img = plt.imshow(plot_map.T, cmap=self.DEFAULT_CMAP, extent=self.extent,
                             aspect = self.aspect_ratio)
            if is_height_map[i]:
                plt.contour(np.flip(plot_map.T, axis=0), levels=9, colors='#000000', linestyles='solid', \
                            linewidths=1, extent=self.extent)
            plt.plot(path[:,0], path[:,1], 'r')
            cbar = plt.colorbar(img)
            if self.extent[0]!=0:
                axs.set(xlabel='LON', ylabel='LAT')
                axs.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
                axs.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
            else:
                axs.set(xlabel='x(m)', ylabel='y(m)')
            cbar.ax.set_ylabel(self.layer_names[layers[i]])
        plt.show()
    

    def define_image(self, filename):
        '''
        Define surface image
            Parameters:
                filename (String): Path to image file
        '''
        self.map_image = mpimg.imread(filename)


    def show_image(self):
        '''Show previously defined image'''
        try:
            _, axs = plt.subplots()
            plt.imshow(self.map_image, extent=self.extent,
                       aspect=self.aspect_ratio)
            if self.extent[0]!=0:
                axs.set(xlabel='LON', ylabel='LAT')
                axs.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
                axs.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
            else:
                axs.set(xlabel='x(m)', ylabel='y(m)')
            plt.show()
        except TypeError: 
            print("ERROR: This map does no have a surface image. Please define one using the\
                  function define_image(filename).")


    def choose_start_and_goal_on_image(self):
        '''Show previously defined image'''
        _, axs = plt.subplots()
        plt.imshow(self.map_image, extent=self.extent,
                aspect=self.aspect_ratio)
        if self.extent[0]!=0:
            axs.set(xlabel='LON', ylabel='LAT')
            axs.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
            axs.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
        else:
            axs.set(xlabel='x(m)', ylabel='y(m)')

        # Connect the onclick function to the figure's button press event
        cid = plt.gcf().canvas.mpl_connect('button_press_event', self.onclick)
        plt.show()
        # Disconnect the event handler when done
        plt.gcf().canvas.mpl_disconnect(cid)

    def onclick(self, event):
        # Check if the click event occurred within the axes
        if event.inaxes:
            # Get the x and y coordinates of the click event
            x = event.xdata
            y = event.ydata
            if event.button == 1:
                self.start = (x, y)
                print(f"Start at x={x}, y={y}")
            elif event.button == 3:
                self.goal = (x, y)
                print(f"Goal at x={x}, y={y}")


    def show_image_with_path(self, path, plot_global=None):
        '''
        Show image of area plus calculated path
            Parameters:
                path (ndarray): 2D array of dimension (2,n) or rsp. length n (if tupellist)
                plot_global (bool): Defines if plot is showed in the local or global coordinate frame
        '''
        if plot_global==None:
            extent = self.extent
            aspect_ratio = self.aspect_ratio
        elif plot_global:
            extent = (self.xmin, self.xmax, self.ymin, self.ymax)
            aspect_ratio = abs(self.xmax-self.xmin) / abs(self.ymax-self.ymin) * \
                                self.n_px_height / self.n_px_width
        else:
            extent = (0, self.width, 0, self.height)
            aspect_ratio = 'equal'

        if isinstance(path, np.ndarray):
            pass
        elif isinstance(path, list):
            path = transform.tupellist_to_array(path)
        else:
            raise TypeError("Invalid type for 'path'. Must be a NumPy array or a list of tuples.")

        try:
            _, axs = plt.subplots()
            plt.imshow(self.map_image, extent=extent, aspect = aspect_ratio)
            if plot_global:
                axs.set_xlabel('LON')
                axs.set_ylabel('LAT')
                #axs.set_xticklabels([f"{val:.{4}f}" for val in axs.get_xticks()])
                #axs.set_yticklabels([f"{val:.{4}f}" for val in axs.get_yticks()])
            else:
                axs.set_xlabel('x(m)')
                axs.set_ylabel('y(m)')
            plt.plot(path[:,0], path[:,1], 'r', linewidth=3)
            plt.show()
        except TypeError: 
            print("ERROR: This map does no have a surface image. Please define one using the \
                  function define_image(filename).")


    def show_image_with_path_and_energy(self, path, energy_stats, plot_global=None):
        '''
        Show image of area plus calculated path
            Parameters:
                path (ndarray): 2D array of dimension (2,n) or rsp. length n (if tupellist)
                plot_global (bool): Defines if plot is showed in the local or global coordinate frame
        '''
        if plot_global==None:
            extent = self.extent
            aspect_ratio = self.aspect_ratio
        elif plot_global:
            extent = (self.xmin, self.xmax, self.ymin, self.ymax)
            aspect_ratio = abs(self.xmax-self.xmin) / abs(self.ymax-self.ymin) * \
                                self.n_px_height / self.n_px_width
        else:
            extent = (0, self.width, 0, self.height)
            aspect_ratio = 'equal'

        if isinstance(path, np.ndarray):
            pass
        elif isinstance(path, list):
            path = transform.tupellist_to_array(path)
        else:
            raise TypeError("Invalid type for 'path'. Must be a NumPy array or a list of tuples.")

        # Normalize energy consumption to max and min value from energy plot
        norm_energy = Normalize(vmin=0.27, vmax=1.0)
        cmap = plt.get_cmap(self.DEFAULT_CMAP)

        # Create scalable colormap
        sm = ScalarMappable(cmap=cmap, norm=norm_energy)
        sm.set_array([])  # Empty array, the actual data is not needed for the colorbar

        _, axs = plt.subplots()
        plt.imshow(self.map_image, extent=extent, aspect = aspect_ratio)
        if plot_global:
            axs.set_xlabel('LON')
            axs.set_ylabel('LAT')
            #axs.set_xticklabels([f"{val:.{4}f}" for val in axs.get_xticks()])
            #axs.set_yticklabels([f"{val:.{4}f}" for val in axs.get_yticks()])
        else:
            axs.set_xlabel('x(m)')
            axs.set_ylabel('y(m)')

        for i in range(len(path)-1):
            plt.plot(path[i][0], path[i][1], marker='o', color=cmap(norm_energy(energy_stats[i])))

        cbar = plt.colorbar(sm, ax=axs)
        cbar.set_label('Energy Consumption')
        plt.show()

    def get_maps_array(self):
        '''Returns the maps_array'''
        return self.maps_array
    
    def get_layer_names(self):
        '''Returns the list with layer names'''
        return self.layer_names
    
    def get_geo_xmin_ymin_xmax_ymax(self):
        '''Returns the four edges of the map in globe coordinates'''
        return self.xmin, self.ymin, self.xmax, self.ymax
    
    def check_if_array_is_completely_filled(self):
        '''Checks if there are layers in the array missing'''
        return len(self.layer_names)==self.n_layers
    

### Example of setting up a Maps object
if __name__ == "__main__":
    maps = Maps((256, 256), 3, "../mapdata/Aristarchus_IMP/height_slope_rockabundance.tif", \
                "../mapdata/Aristarchus_IMP/pic.png", ['Height', 'Slope', 'Rock Abundance'])

    maps.plot_layers([0], [False])
    maps.show_image()
