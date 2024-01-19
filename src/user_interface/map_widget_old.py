'''File with all functions needed to plot the path on a canvas'''

from matplotlib import ticker, colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

class MapWidget(QtWidgets.QMainWindow):
    '''
        Child class of the Qt QWidget.

        Attributes: 
            figure (matplotlib Figure): Holder for the plots
            axis (matplotlib Axis): To actually plot functions or images
            canvas (FigureCanvasQTAgg): Canvas to show Figure in Qt environment
            mainwindow (QtWidgets): Connection to main plugin to load relevant map setups

        Methods:
            plot_picture
            plot_layer
            add_path_to_four_layer_view_on_canvas   
    '''
    # DEFAULT_CMAP = colors.LinearSegmentedColormap.from_list\
    #     ("", ["darkslategray","mediumturquoise",'#c9a687','#a6611a'])
    DEFAULT_CMAP = 'viridis'

    def __init__(self, width, height, extent, pixel_size, map_image, maps_array, \
                 layer_names, toolbar, plot_global):
        '''
        Init function for the class
            Parameters:
                width (int): Number of columns in maps array
                height (int): Number of rows in maps array
                extent (xmin (float), ymin (float), xmax (float), ymax (float)): Corners of map in
                    global coordinates
                pixel_size (float): Size of one pixel
                map_image (String): Path to satellite image from area
                maps_array (ndarray): 3D array with (x,y,layer)
                layer_names (String[]): List with names of layers as identifier
                toolbar (Boolean): Decides wether a toolbar should be added to the plot
                plot_global (Boolean): Sets flag if map is plotted in global coordinates (GPS) or 
                    local coordinates ((0,0) to (width,height)m)
        '''
        super().__init__()

        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.figure = Figure()
        self.axis = self.figure.add_subplot(111)
        self.cbar = None
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        if toolbar:
            self.toolbar = NavigationToolbar(self.canvas, self)
            layout.addWidget(self.toolbar)

        if plot_global:
            self.xlabel = 'LON'
            self.ylabel = 'LAT'
            self.axis.set_xlabel(self.xlabel, fontsize=24)
            self.axis.set_ylabel(self.ylabel, fontsize=24)
            self.xmin, self.ymin, self.xmax, self.ymax = extent
            self.extent = (self.xmin, self.xmax, self.ymin, self.ymax)
            self.aspect_ratio = abs(self.xmax-self.xmin) / abs(self.ymax-self.ymin) * \
                                height / width
        else:
            self.xlabel = 'x [m]'
            self.ylabel = 'y [m]'
            self.axis.set_xlabel(self.xlabel, fontsize=24)
            self.axis.set_ylabel(self.ylabel, fontsize=24)
            self.extent = (0, width*pixel_size, 0, height*pixel_size)
            self.aspect_ratio = 'equal'
        self.axis.tick_params(axis='both', which='major', labelsize=20)
        
        self.map_img = map_image
        self.maps_array = maps_array
        self.layer_names = layer_names
        

    def plot_layer_global(self, layer):
        '''
        Plots one or several layers of the maps plus the calculated path
            Parameters:
                layers (int): which layer is to be plotted (from 0 to n_array-1); -1 stands for satellite image
                is_height_map (boolean): setting this to true for the respective layer activates \
                height lines
        '''
        # Clear previous content of figure including colorbar
        self.axis.cla()
        if self.cbar != None:
            self.cbar.remove()
            self.cbar = None
        
        if layer == -1:
            self.axis.imshow(self.map_img, extent=self.extent, aspect = self.aspect_ratio)
        else:
            plot_map = self.maps_array[:,:,layer]
            self.img = self.axis.imshow(plot_map.T, cmap=self.DEFAULT_CMAP,\
                                extent=self.extent, aspect = self.aspect_ratio)
            if layer==0:
                self.axis.contour(np.flip(plot_map.T, axis=0), levels=20, colors='#333333', linestyles='solid', \
                            linewidths=1, extent=self.extent)
            self.cbar = self.figure.colorbar(self.img)
            self.cbar.ax.set_ylabel(self.layer_names[layer])

        self.axis.set_xlabel(self.xlabel, fontsize=24)
        self.axis.set_ylabel(self.ylabel, fontsize=24)
        self.axis.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))
        self.axis.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))
        self.axis.xaxis.set_major_locator(ticker.MaxNLocator(4))
        self.axis.yaxis.set_major_locator(ticker.MaxNLocator(5))
        self.axis.tick_params(axis='both', which='major', labelsize=24)

        self.canvas.draw()


    def plot_layer_local(self, layer):
        '''
        Plots one or several layers of the maps plus the calculated path
            Parameters:
                layers (int): which layer is to be plotted (from 0 to n_array-1); -1 stands for satellite image
                is_height_map (boolean): setting this to true for the respective layer activates \
                height lines
        '''
        # Clear previous content of figure including colorbar
        self.axis.cla()
        if self.cbar != None:
            self.cbar.remove()
            self.cbar = None
        
        if layer == -1:
            self.axis.imshow(self.map_img, extent=self.extent, aspect = self.aspect_ratio)
        else:
            plot_map = self.maps_array[:,:,layer]
            self.img = self.axis.imshow(plot_map.T, cmap=self.DEFAULT_CMAP,\
                                extent=self.extent, aspect = self.aspect_ratio)
            if layer==0:
                self.axis.contour(np.flip(plot_map.T, axis=0), levels=20, colors='#333333', linestyles='solid', \
                            linewidths=1, extent=self.extent)
            self.cbar = self.figure.colorbar(self.img)
            self.cbar.ax.set_ylabel(self.layer_names[layer])

        self.axis.set(xlabel=self.xlabel, ylabel=self.ylabel)        
        self.canvas.draw()
        

    def plot_path_on_canvas(self, path, type):
        '''
        Plots path on whichever picture was shown before
            Parameters:
                path (ndarray): 2D array with coordinates and size (n, 2)
                type (String): Defines style of line ('planned_path'/'tracked_path')
        '''
        if type=='planned_path':
            color = 'r'
        elif type=='tracked_path':
            color = 'lime'
        else:
            print("The path type '"+type+"' is not known to the program. Possible options \
                  are 'planned_path' or 'tracked_path'.")
        try:
            self.axis.plot(path[:,0], path[:,1], color, linewidth=3)
            self.canvas.draw()
        except TypeError:
            pass
        

    def plot_point_on_canvas(self, coordinate, type):
        '''
        Plots one point on whichever picture was shown before
            Parameters:
                coordinate (float[]): list with len (2) defining the coordinates (x, y)
                type (String): Defines style of marker ('start'/'goal'/'new_goal')
        '''
        if type=='goal':
            color = 'r*'
        elif type=='start':
            color = 'ro'

        else:
            print("The point type '"+type+"' is not known to the program. Possible options \
                  are 'start', 'goal', 'old_start' or 'old_goal'.")
        self.axis.plot(coordinate[0], coordinate[1], color)
        self.canvas.draw()


    def plot_four_layers_with_details(self):
        '''Prepares 8 plots to analyse path more in depth'''
        self.figure.clf()

        # Plot layers of array
        self.axis = self.figure.subplots(2, 4)

        for i, ax in enumerate(self.axis.flat):
            if i%2==0:
                img = ax.imshow(self.maps_array[:, :, i//2].T, cmap=self.DEFAULT_CMAP,
                                extent=self.extent, aspect = self.aspect_ratio)
                ax.set(xlabel=self.xlabel, ylabel=self.ylabel)
                #ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
                #ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
        
        # Add contour for height map
        self.axis[0, 0].contour(np.flip(self.maps_array[:,:,0].T, axis=0), levels=20, colors='#000000',
                                linestyles='solid', linewidths=1, extent=self.extent)
        
        # Add colorbars with label
        cbar1 = self.figure.colorbar(img, ax=self.axis[0, 0])
        cbar1.ax.set_ylabel('m')
        cbar2 = self.figure.colorbar(img, ax=self.axis[0, 2])
        cbar2.ax.set_ylabel('deg')
        cbar3 = self.figure.colorbar(img, ax=self.axis[1, 0])
        cbar3.ax.set_ylabel('100%')
        cbar4 = self.figure.colorbar(img, ax=self.axis[1, 2])
        cbar4.ax.set_ylabel('100%')

        # Add titles and axes
        self.axis[0, 0].set_title('Height map')
        self.axis[0, 2].set_title('Slope')
        self.axis[1, 0].set_title('Traversability score')
        self.axis[1, 2].set_title('Scientific interest')

        self.axis[0, 1].set(xlabel='pixel', ylabel='m')
        self.axis[0, 3].set(xlabel='pixel', ylabel='deg')
        self.axis[1, 1].set(xlabel='pixel', ylabel='100%')
        self.axis[1, 3].set(xlabel='pixel', ylabel='100%')

        self.canvas.draw()


    def add_path_to_four_layer_view(self, wp_coordinates, path_pixel):
        '''
        Plots the path as well as path details in the prepared plots
            Parameters:
                wp_coordinates (ndarray): 2D Array of size (n,2) with the waypoints coordinates. 
                path_pixel (ndarray): 2D Array of size (n,2) with the full path pixel. 
        '''
        for i, ax in enumerate(self.axis.flat):
            if i%2==0:
                ax.plot(wp_coordinates[:, 0], wp_coordinates[:, 1], 'r', linewidth=3)
            else:
                ax.plot(self.maps_array[path_pixel[:,0], path_pixel[:,1], i//2])

        self.canvas.draw()


    def prepare_four_sat_pics(self):
        '''Plots the satellite picture four times to compare paths on'''
        self.figure.clf()

        # Plot layers of array
        self.axis = self.figure.subplots(1, 4)

        for i, ax in enumerate(self.axis.flat):
            ax.imshow(self.map_img, extent=self.extent, aspect = self.aspect_ratio)
            ax.set_xlabel('x [m]', fontsize = 18)
            ax.set_ylabel('y [m]', fontsize = 18)
            #ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
            #ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
            ax.set_title('Path segment '+str(i+1), fontsize = 22)
            ax.tick_params(axis='both', which='major', labelsize=18)
        
        self.canvas.draw()


    def clear_one_of_four_sat_pics(self, i):
        '''
        Clears the canvas and puts satellite pic up again
            Parameters:
                i (int): 0...3; number of which path is plotted
        '''
        self.axis.flat[i].cla()
        self.axis.flat[i].imshow(self.map_img, extent=self.extent, aspect = self.aspect_ratio)
        self.axis.flat[i].set(xlabel=self.xlabel, ylabel=self.ylabel)
        #self.axis.flat[i].xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
        #self.axis.flat[i].yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
        self.axis.flat[i].set_title('Path segment '+str(i+1), fontsize = 22)
        self.axis.flat[i].tick_params(axis='both', which='major', labelsize=18)
        self.canvas.draw()


    def plot_path_on_one_of_four_sat_pic(self, path, i):
        '''
        Plots path on one of the four sat pics
            Parameters:
                path (ndarray): 2D array with coordinates and size (n, 2)
                i (int): 0...3; number of which path is plotted
        '''
        self.axis.flat[i].plot(path[:,0], path[:,1], 'r', linewidth=3)
        self.canvas.draw()
