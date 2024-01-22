import sys
import os
from PyQt5 import QtWidgets
from python_qt_binding import loadUi
from user_interface.map_widget import MapWidget
from user_interface.cluster_widget import ClusterWidget
from mapdata import setup_aristarchus as setup_file
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pandas as pd
from matplotlib import cm


class MyQtMainWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_file):
        super().__init__()

        # Load the UI file
        loadUi(ui_file, self)

        # Initialize map widget
        self.setup = setup_file.Setup('src/mapdata/', 0.5, 0.5, 0, True)
        self.mapwidget = MapWidget(width=self.setup.maps.n_px_width,
                                   height=self.setup.maps.n_px_height,
                                   extent=self.setup.get_geo_xmin_ymin_xmax_ymax(),
                                   pixel_size=self.setup.maps.pixel_size,
                                   map_image=self.setup.maps.map_image,
                                   maps_array=self.setup.maps.maps_array,
                                   layer_names=self.setup.maps.layer_names,
                                   toolbar=True,
                                   plot_global=True)
        QtWidgets.QVBoxLayout(self.pathplot).addWidget(self.mapwidget)
        self.map_up.clicked.connect(self.change_to_next_map)
        self.map_down.clicked.connect(self.change_to_previous_map)
        self.map_down.setEnabled(False)
        self.current_map = -1
        self.mapwidget.plot_layer_global(self.current_map)

        # Initialize cluster widget
        self.clusterwidget = ClusterWidget()
        self.toolbar = NavigationToolbar(self.clusterwidget.mpl_canvas, self)
        layout_clusterwidget = QtWidgets.QVBoxLayout(self.analysisplot)
        layout_clusterwidget.addWidget(self.clusterwidget)
        layout_clusterwidget.addWidget(self.toolbar)

        # Init other ui parts
        self.getpathfolder.clicked.connect(self.define_path_folder)
        self.recalculatebutton.clicked.connect(self.show_path_analysis)

        # Disable buttons
        self.recalculatebutton.setEnabled(False)

        # Init some variables
        self.project_folder = ''
        self.paths_files = []
        self.stats_files = []
        self.current_paths = []
        self.colors = []


    def define_path_folder(self):
        initial_directory = 'user_data/path_storage'
        selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project Folder", initial_directory)
        if selected_folder:
            paths_files = [file for file in os.listdir(selected_folder) if file.endswith("_paths.csv")]
            stats_files = [file for file in os.listdir(selected_folder) if file.endswith("_stats.csv")]
            if not paths_files or not stats_files:
                self.erroroutput.setStyleSheet("color: red;")         
                self.erroroutput.setText("Folder does not contain a file that ends with '_paths.csv' and '_stats.csv'.")
            elif len(paths_files)!=len(stats_files):
                self.erroroutput.setStyleSheet("color: red;")         
                self.erroroutput.setText("The number of '_paths.csv' and '_stats.csv' files must be equal and should follow the naming policy 'segmentX_paths.csv' and 'segmentX_stats.csv', where X are upcounting integers (1,2,...).")
                self.erroroutput.setWordWrap(True)
            else:
                self.erroroutput.setText("")

                self.project_folder = selected_folder+'/'
                self.paths_files = sorted(paths_files, key=self.extract_number)
                self.stats_files = sorted(stats_files, key=self.extract_number)

                entries = [f"Segment {i}" for i in range(1, len(self.paths_files) + 1)]
                self.pathsegmentchooser.addItems(entries)
                self.pathsegmentchooser.setEditable(True)

                self.recalculatebutton.setEnabled(True)


    def extract_number(self, file_name):
        '''Helper function for sorting files'''
        return int(''.join(filter(str.isdigit, file_name)))


    def show_path_analysis(self):
        '''Reads how many clusters for which path segment user wants and updates the plots'''
        current_segment = self.pathsegmentchooser.currentIndex()

        # Load stats from the file
        data = np.loadtxt(self.project_folder+self.stats_files[current_segment], skiprows=1)
        n_clusters = self.numberofclusters.value()
        
        # Extract columns
        r = data[:, 1]
        g = data[:, 2]
        b = data[:, 3]
        E_P = data[:, 4]
        R_P = data[:, 5]
        I_P = data[:, 6]
        n_pixel = data[:, 8]

        # Define path for comparison
        average_point_index = np.argmin(cdist(data[:,1:4], [[0.333333, 0.333333, 0.333333]]))

        # Calculate clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init='auto').fit(np.column_stack((E_P, R_P, I_P)))
        labels = kmeans.labels_
        cluster_centers = kmeans.cluster_centers_
        self.clusterwidget.plot(E_P, R_P, I_P, color=labels)
        closest_paths = []
        all_points = data[:, 4:7]

        # Create data for comparison table
        for cluster_label, center in enumerate(cluster_centers):
            cluster_points = data[labels == cluster_label, 4:7]

            # Find the point closest to the centroid
            closest_point_index = np.argmin(cdist(all_points, [center]))
            closest_point = all_points[closest_point_index]
            closest_paths.append(closest_point_index)

            # Calculate variance within the cluster
            cluster_variance = np.var(cluster_points, axis=0)

            # # Data for comparison table
            # print(f"Cluster {cluster_label + 1}:")
            # print(f"Number of paths in cluster: {len(cluster_points)}")
            # print(f"Cluster center: {center}")
            # print(f"Variance within cluster: {cluster_variance} with average of {np.average(cluster_variance)}")
            # print(f"Closest point to centroid: {closest_point}")
            # print(f"Weights of closest point: {data[closest_point_index,1]},{data[closest_point_index,2]},{data[closest_point_index,3]}")
            
            # # compare to average path
            # energysave = (data[average_point_index,4] - data[closest_point_index,4]) / data[average_point_index,5] * 100
            # risksave = (data[average_point_index,5] - data[closest_point_index,5]) / data[average_point_index,5] * 100
            # sciencegain = (data[closest_point_index,6] - data[average_point_index,6]) / data[average_point_index,6] * 100
            # prewords = []
            # if energysave>0:
            #     prewords.append('less')
            # else: 
            #     prewords.append('more')
            # if risksave>0:
            #     prewords.append('less')
            # else:
            #     prewords.append('more')
            # if sciencegain>0: 
            #     prewords.append('less')
            # else:
            #     prewords.append('more')
            # print(f"This path has {np.abs(energysave)}% "+prewords[0]+f" energy consumption, {np.abs(risksave)}% "+
            #         prewords[1]+f" risk and {np.abs(sciencegain)}% "+prewords[2]+" scientific outcome than baseline.")
            # print()

            self.clusterwidget.plot_highlight(closest_point)

        # Loop through all paths and plot them
        max_pixel = int(np.max(n_pixel))
        df = pd.read_csv(self.project_folder+self.paths_files[current_segment], delimiter='\t', names=list(range(max_pixel+1)))
        num_rows = int(df.shape[0]/2)

        # for path_number in range(num_rows):
        #     lon = df.loc[2*path_number]
        #     lat = df.loc[2*path_number+1]
        #     path_globe = np.array([(float(lon.iloc[i]), float(lat.iloc[i])) for i in range(1,lon.last_valid_index()+1)])
        #     sc = self.clusterwidget.scatter_plot
        #     color = sc.cmap(sc.norm(labels[path_number]))
        #     print(path_globe)
        #     print(color)
        #     self.mapwidget.plot_path_on_canvas(path_globe, color)

        
        self.current_paths = []
        self.colors = []
        sc = self.clusterwidget.scatter_plot
        for number in closest_paths:
            lon = df.loc[2*number]
            lat = df.loc[2*number+1]
            path_globe = np.array([(float(lon.iloc[i]), float(lat.iloc[i])) for i in range(1,lon.last_valid_index()+1)])
            color = sc.cmap(sc.norm(labels[number]))
            self.current_paths.append(path_globe)
            self.colors.append(color)

        self.plot_layer_with_paths()


    def change_to_next_map(self):
        '''
        Changes background of map one map layer down
        The following numbers define the maps: -1 = satellite picture; 0...n = layers of Maps object
        '''
        self.current_map = self.current_map + 1
        # Enable/ disable button function if on first/ last map
        if self.current_map == self.setup.maps.maps_array.shape[2] - 1:
            self.map_up.setEnabled(False)
        elif self.current_map == 0:
            self.map_down.setEnabled(True)
        self.plot_layer_with_paths()


    def change_to_previous_map(self):
        '''Changes background of map one map layer up'''
        self.current_map = self.current_map - 1
        # Enable/ disable button function if on first/ last map
        if self.current_map == -1:
            self.map_down.setEnabled(False)
        elif self.current_map == self.setup.maps.maps_array.shape[2] - 2:
            self.map_up.setEnabled(True)
        self.plot_layer_with_paths()


    def plot_layer_with_paths(self):
        '''Plots the current selected layer (self.current_map) and if applicable also the path'''
        self.mapwidget.plot_layer_global(self.current_map)
        for path, color in zip(self.current_paths, self.colors):
            self.mapwidget.plot_path_on_canvas(path, color)
        # plot paths


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_main_window = MyQtMainWindow("src/user_interface/ui/MainWindow.ui")
    my_main_window.show()
    sys.exit(app.exec_())


