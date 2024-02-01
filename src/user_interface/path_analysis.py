import sys
import os
from PyQt5 import QtWidgets
from python_qt_binding import loadUi
from user_interface.map_widget import MapWidget
from user_interface.cluster_widget import ClusterWidget
from mapdata import setup_aristarchus_hm as setup_file
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pandas as pd
from matplotlib import cm
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QSizePolicy

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
        self.pathplot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialize cluster widget
        self.clusterwidget = ClusterWidget()
        QtWidgets.QVBoxLayout(self.analysisplot).addWidget(self.clusterwidget)
        # layout_clusterwidget = QtWidgets.QVBoxLayout(self.analysisplot)
        self.analysisplot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Prepare table
        self.analysistable.setRowCount(4)
        self.analysistable.setColumnCount(12)

        titles_tabel1 = ['','Weights','','','Energy','','Risk','','Science','','# Paths in cluster','Custer var']
        titles_tabel2 = ['','alpha','beta','gamma','[kNm^2]','cmp to base','%','cmp to base','% of path','cmp to base','','']
        for i, title in enumerate(titles_tabel1):
            self.analysistable.setItem(0, i, QtWidgets.QTableWidgetItem(title))
        for i, title in enumerate(titles_tabel2):
            self.analysistable.setItem(1, i, QtWidgets.QTableWidgetItem(title))
        self.analysistable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

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
                self.erroroutput.setStyleSheet("color: black;")
                self.erroroutput.setText("Selected folder: "+selected_folder)

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

        # Adapt table
        self.analysistable.setRowCount(n_clusters+3)
        self.analysistable.setItem(2, 0, QtWidgets.QTableWidgetItem('Baseline'))
        for i in range(n_clusters):
            self.analysistable.setItem(i+3, 0, QtWidgets.QTableWidgetItem('Path '+str(i+1)))

        # Extract columns
        data_a = data[:, 1]
        data_b = data[:, 2]
        data_c = data[:, 3]
        data_E_P = data[:, 4]
        data_R_P = data[:, 5]
        data_I_P = data[:, 6]
        data_E_star = data[:, 7]
        data_C = data[:, 8]
        data_S = data[:, 9]
        n_pixel = data[:, 10]

        # Calculate clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init='auto').fit(np.column_stack((data_E_P, data_R_P, data_I_P)))
        labels = kmeans.labels_
        cluster_centers = kmeans.cluster_centers_
        self.clusterwidget.plot(data_E_P, data_R_P, data_I_P, color=labels)
        closest_paths = []
        all_points = data[:, 4:7]

        # Load path file
        max_pixel = int(np.max(n_pixel))
        df = pd.read_csv(self.project_folder+self.paths_files[current_segment], delimiter='\t', names=list(range(max_pixel+1)))
        num_rows = int(df.shape[0]/2)
        self.current_paths = []
        self.colors = []

        # Define path for comparison
        average_point_index = np.argmin(cdist(data[:,1:4], [[0.333333, 0.333333, 0.333333]]))

        # Load specs of baseline and add to table
        lon = df.loc[2*average_point_index]
        lat = df.loc[2*average_point_index+1]
        path_globe_baseline = np.array([(float(lon.iloc[i]), float(lat.iloc[i])) for i in range(1,lon.last_valid_index()+1)])
        self.current_paths.append(path_globe_baseline)
        self.colors.append('r')

        energy_base = data_E_star[average_point_index]/1000
        risk_base = data_C[average_point_index]
        science_base = data_S[average_point_index]

        self.analysistable.item(2,0).setBackground(QBrush(QColor(255, 0, 0, 80)))
        self.analysistable.setItem(2, 1, QtWidgets.QTableWidgetItem(str(round(data_a[average_point_index],4))))
        self.analysistable.setItem(2, 2, QtWidgets.QTableWidgetItem(str(round(data_b[average_point_index],4))))
        self.analysistable.setItem(2, 3, QtWidgets.QTableWidgetItem(str(round(data_c[average_point_index],4))))
        self.analysistable.setItem(2, 4, QtWidgets.QTableWidgetItem(str(round(energy_base,2))))
        self.analysistable.setItem(2, 6, QtWidgets.QTableWidgetItem(str(round(risk_base*100,2))))
        self.analysistable.setItem(2, 8, QtWidgets.QTableWidgetItem(str(round(science_base*100,2))))

        # Create data for comparison table
        for cluster_label, center in enumerate(cluster_centers):
            cluster_points = data[labels == cluster_label, 4:7]

            # Find the point closest to the centroid
            closest_point_index = np.argmin(cdist(all_points, [center]))
            closest_point = all_points[closest_point_index]
            closest_paths.append(closest_point_index)

            # Show cluster plot
            self.clusterwidget.plot_highlight(closest_point)

            # Calculate variance within the cluster
            cluster_variance = np.var(cluster_points, axis=0)

            # Plot path in mapwiget TOOOOODOOOOOO
            sc = self.clusterwidget.scatter_plot

            lon = df.loc[2*closest_point_index]
            lat = df.loc[2*closest_point_index+1]
            path_globe = np.array([(float(lon.iloc[i]), float(lat.iloc[i])) for i in range(1,lon.last_valid_index()+1)])
            color = sc.cmap(sc.norm(labels[closest_point_index]))
            self.current_paths.append(path_globe)
            self.colors.append(color)

            # Data for comparison table
            energy = data_E_star[closest_point_index]/1000
            risk = data_C[closest_point_index]
            science = data_S[closest_point_index]
            energysave = (energy-energy_base)/energy_base * 100
            if risk_base == 0:
                risksave = risk * 100
            else:
                risksave = (risk-risk_base)/risk_base * 100
            sciencegain = (science-science_base)/science_base * 100

            color = [int(i*255) for i in color]
            self.analysistable.item(cluster_label+3,0).setBackground(QBrush(QColor(*color[:3], 80)))
            self.analysistable.setItem(cluster_label+3, 1, QtWidgets.QTableWidgetItem(str(round(data_a[closest_point_index],4))))
            self.analysistable.setItem(cluster_label+3, 2, QtWidgets.QTableWidgetItem(str(round(data_b[closest_point_index],4))))
            self.analysistable.setItem(cluster_label+3, 3, QtWidgets.QTableWidgetItem(str(round(data_c[closest_point_index],4))))
            self.analysistable.setItem(cluster_label+3, 4, QtWidgets.QTableWidgetItem(str(round(energy,2))))
            self.analysistable.setItem(cluster_label+3, 5, QtWidgets.QTableWidgetItem(str(round(energysave,2))+'%'))
            self.analysistable.setItem(cluster_label+3, 6, QtWidgets.QTableWidgetItem(str(round(risk*100,2))))
            self.analysistable.setItem(cluster_label+3, 7, QtWidgets.QTableWidgetItem(str(round(risksave,2))+'%'))
            self.analysistable.setItem(cluster_label+3, 8, QtWidgets.QTableWidgetItem(str(round(science*100,2))))
            self.analysistable.setItem(cluster_label+3, 9, QtWidgets.QTableWidgetItem(str(round(sciencegain,2))+'%'))
            self.analysistable.setItem(cluster_label+3, 10, QtWidgets.QTableWidgetItem(str(len(cluster_points))))
            self.analysistable.setItem(cluster_label+3, 11, QtWidgets.QTableWidgetItem(str(round(np.average(cluster_variance),2))))
            self.analysistable.resizeColumnsToContents()

        # Plot all paths in map
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
        linestyles = [(0,(3,0)),(0,(3,1)),(0,(3,2)),(0,(2,2)),(0,(1,1)),
                      (0,(1,2)),(1,(1,2)),(0,(1,3)),(1,(1,3)),(2,(1,3)),
                      (0,(1,3))]

        for path, color, linestyle in zip(self.current_paths, self.colors, linestyles):
            self.mapwidget.plot_path_on_canvas(path, color, linestyle)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_main_window = MyQtMainWindow("src/user_interface/ui/PathAnalysis.ui")
    my_main_window.show()
    sys.exit(app.exec_())


