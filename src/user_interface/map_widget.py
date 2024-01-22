'''File with all functions needed to plot the path on a canvas'''

from matplotlib import ticker, colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

class MapWidget(QtWidgets.QWidget):
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
    FONTSIZE = 11

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

        layout = QtWidgets.QVBoxLayout(self)

        self.figure = Figure()
        self.axis = self.figure.add_subplot(111)
        self.cbar = None
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.figure.subplots_adjust(left=0.05, right=0.90, bottom=0.15, top=0.9)

        if toolbar:
            self.toolbar = NavigationToolbar(self.canvas, self)
            layout.addWidget(self.toolbar)

        self.xlabel_global = 'LON [deg]'
        self.ylabel_global = 'LAT [deg]'
        self.axis.set_title("Calculated paths")
        self.axis.set_xlabel(self.xlabel_global, fontsize=self.FONTSIZE)
        self.axis.set_ylabel(self.ylabel_global, fontsize=self.FONTSIZE)
        self.xmin, self.ymin, self.xmax, self.ymax = extent
        self.extent_global = (self.xmin, self.xmax, self.ymin, self.ymax)
        self.aspect_ratio_global = abs(self.xmax-self.xmin) / abs(self.ymax-self.ymin) * \
                                   height / width
        self.xlabel_local = 'x [m]'
        self.ylabel_local = 'y [m]'
        self.axis.set_xlabel(self.xlabel_local, fontsize=self.FONTSIZE)
        self.axis.set_ylabel(self.ylabel_local, fontsize=self.FONTSIZE)
        self.extent_local = (0, width*pixel_size, 0, height*pixel_size)
        self.aspect_ratio_local = 'equal'

        self.axis.tick_params(axis='both', which='major', labelsize=self.FONTSIZE)
        
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
            self.axis.imshow(self.map_img, extent=self.extent_global, aspect = self.aspect_ratio_global)
        else:
            plot_map = self.maps_array[:,:,layer]
            self.img = self.axis.imshow(plot_map.T, cmap=self.DEFAULT_CMAP,\
                                extent=self.extent_global, aspect = self.aspect_ratio_global)
            if layer==0:
                self.axis.contour(np.flip(plot_map.T, axis=0), levels=20, colors='#333333', linestyles='solid', \
                            linewidths=1, extent=self.extent_global)
            self.cbar = self.figure.colorbar(self.img)
            self.cbar.ax.set_ylabel(self.layer_names[layer])

        self.axis.set_xlabel(self.xlabel_global, fontsize=self.FONTSIZE)
        self.axis.set_ylabel(self.ylabel_global, fontsize=self.FONTSIZE)
        self.axis.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))
        self.axis.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.4f}'))
        self.axis.xaxis.set_major_locator(ticker.MaxNLocator(4))
        self.axis.yaxis.set_major_locator(ticker.MaxNLocator(5))
        self.axis.tick_params(axis='both', which='major', labelsize=10)

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
            self.axis.imshow(self.map_img, extent=self.extent_local, aspect = self.aspect_ratio_local)
        else:
            plot_map = self.maps_array[:,:,layer]
            self.img = self.axis.imshow(plot_map.T, cmap=self.DEFAULT_CMAP,\
                                extent=self.extent_local, aspect = self.aspect_ratio_local)
            if layer==0:
                self.axis.contour(np.flip(plot_map.T, axis=0), levels=20, colors='#333333', linestyles='solid', \
                            linewidths=1, extent=self.extent_local)
            self.cbar = self.figure.colorbar(self.img)
            self.cbar.ax.set_ylabel(self.layer_names[layer])

        self.axis.set(xlabel=self.xlabel_local, ylabel=self.ylabel_local)        
        self.canvas.draw()
        

    def plot_path_on_canvas(self, path, color):
        '''
        Plots path on whichever picture was shown before
            Parameters:
                path (ndarray): 2D array with coordinates and size (n, 2)
                type (String): Defines style of line ('planned_path'/'tracked_path')
        '''
        if isinstance(path, list):
            path = np.array(path)
        if path.shape[0]>0:
            self.axis.plot(path[:,0], path[:,1], color=color, linewidth=3)
        self.canvas.draw()


    def plot_point_on_canvas(self, coordinate, color='r*'):
        '''
        Plots one point on whichever picture was shown before
            Parameters:
                coordinate (float[]): list with len (2) defining the coordinates (x, y)
                type (String): Defines style of marker (e.g. 'r*' or 'ro')
        '''
        self.axis.plot(coordinate[0], coordinate[1], color)
        self.canvas.draw()

