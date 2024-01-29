#!/usr/bin/env python3

import sys
import numpy as np
import os
from python_qt_binding import loadUi
from PyQt5 import QtWidgets
from mapdata.setup_aristarchus import Setup
from globalplanner import transform, astar
from user_interface.map_widget import MapWidget
from itertools import product
import csv
import pandas as pd

import time
import resource
from datetime import datetime


class PathCreatorPlugin(QtWidgets.QWidget):
    '''
    Child class of the Rqt Plugin.
  
    Attributes: 
        _widget (QWidget): Main window that includes all objects (Buttons, Labels etc.)
        mapwidget (MapWidget): To show different plots in matplotlib style

    Methods:
        show_pic:
        show_path:
        shutdown_plugin: Unregister all publishers   
        save_settings: Save intrinsic configuration
        restore_settings: Restore intrinsic configuration
    '''
    PLOT_GLOBAL = False

    def __init__(self, ui_file):
        '''Init function for the class'''
        super().__init__()
        loadUi(ui_file, self)

        # # Create QWidget and load ui file
        # self.mainwindow = QtWidgets.QWidget()
        # ui_file = os.path.join(self.path_to_root, 'ui', 'PathCreator.ui')
        # loadUi(ui_file, self.mainwindow)
        # self.mainwindow.setWindowTitle('Lodia Path Creator')
        # context.add_widget(self.mainwindow)

        # Init map frame
        self.setup = Setup('src/mapdata/', 0.5, 0.5, 0, True)
        self.mapframe = MapWidget(width=self.setup.maps.n_px_width, 
                                   height=self.setup.maps.n_px_height, 
                                   extent=self.setup.get_geo_xmin_ymin_xmax_ymax(),
                                   pixel_size=self.setup.maps.pixel_size,
                                   map_image=self.setup.maps.map_image, 
                                   maps_array=self.setup.maps.maps_array, 
                                   layer_names=self.setup.maps.layer_names,
                                   toolbar=True,
                                   plot_global=self.PLOT_GLOBAL)
        QtWidgets.QVBoxLayout(self.mapwidget).addWidget(self.mapframe)
        self.mapframe.plot_layer_local(-1)
        
        # Connect buttons
        self.mapframe.canvas.mpl_connect('button_press_event', self.click_on_map_sets_new_goal)
        self.globalcoordbutton.clicked.connect(self.change_map_frame_to_global)
        self.localcoordbutton.clicked.connect(self.change_map_frame_to_local)
        self.loadpathbutton.clicked.connect(self.load_path)
        self.deletepathbutton.clicked.connect(self.delete_path)
        self.deletepointbutton.clicked.connect(self.delete_last_point)
        self.calculatebutton.clicked.connect(self.calculate_path)
        self.calculatebutton.setEnabled(False)
        self.stackedWidget.setCurrentIndex(0)
        
        # Init variables
        self.waypoints = []


    def change_map_frame_to_global(self, event):
        if not self.PLOT_GLOBAL:
            self.PLOT_GLOBAL = True
            self.mapframe.plot_layer_global(-1)
            if len(self.waypoints)>0:
                self.waypoints = transform.from_map_to_globe(self.waypoints, self.setup)
            self.mapframe.plot_path_on_canvas(self.waypoints, 'red')
            for point in self.waypoints:
                self.mapframe.plot_point_on_canvas(point, 'ro')


    def change_map_frame_to_local(self, event):
        if self.PLOT_GLOBAL:
            self.PLOT_GLOBAL = False
            self.mapframe.plot_layer_local(-1)
            if len(self.waypoints)>0:
                self.waypoints = transform.from_globe_to_map(self.waypoints, self.setup)
            self.mapframe.plot_path_on_canvas(self.waypoints, 'red')
            for point in self.waypoints:
                self.mapframe.plot_point_on_canvas(point, 'ro')

    
    def load_path(self, event):
        # Load path
        input_str = self.pathinput.text()
        if len(input_str)>0:
            pairs = input_str.replace('(', '').replace(')', '').split(',')
            self.delete_path(0)

            try:
                self.waypoints = [(float(pairs[i]), float(pairs[i + 1])) for i in range(0, len(pairs), 2)]
                if len(self.waypoints)>1:
                    # Show path
                    self.mapframe.plot_path_on_canvas(self.waypoints, 'red')
                    for point in self.waypoints:
                        self.mapframe.plot_point_on_canvas(point, 'ro')
                    self.calculatebutton.setEnabled(True)
            except:
                pass


    def delete_path(self, _):
        self.waypoints = []
        self.replot_map()
        self.calculatebutton.setEnabled(False)


    def delete_last_point(self, event):
        self.waypoints.pop()
        self.replot_map()


    def replot_map(self):
        if self.PLOT_GLOBAL:
            self.mapframe.plot_layer_global(-1)
        else:
            self.mapframe.plot_layer_local(-1)
        if len(self.waypoints)>0:
            self.mapframe.plot_path_on_canvas(self.waypoints, 'red')
            for point in self.waypoints:
                self.mapframe.plot_point_on_canvas(point, 'ro')


    def click_on_map_sets_new_goal(self, event):
        '''Clicking with the right mouse button sets a new goal on the canvas'''
        input_point = (event.xdata, event.ydata)
        if event.button == 1:
            if input_point[0] is not None and input_point[1] is not None:
                self.waypoints.append(input_point)
                self.mapframe.plot_point_on_canvas(input_point, 'ro')
                if len(self.waypoints)>=2:
                    self.mapframe.plot_path_on_canvas([self.waypoints[len(self.waypoints)-2], input_point], 'red')
                    self.calculatebutton.setEnabled(True)


    def calculate_path(self, event):
        # Create folder for storage
        string_input = self.outputfolder.text()
        project_name = string_input.replace(" ", "")
        output_folder = 'user_data/path_storage/'+project_name
        if os.path.exists(output_folder):
            self.erroroutput.setStyleSheet("color: red;")
            self.erroroutput.setText("Foldername already exists in path '/user_data/path_storage'. Please choose different name.")
            self.erroroutput.setWordWrap(True)
        else:
            # Show screen with progress bar
            self.stackedWidget.setCurrentIndex(1)
            QtWidgets.QApplication.processEvents()

            # Create paths 
            os.makedirs(output_folder)
            if not self.PLOT_GLOBAL:
                self.waypoints = transform.from_map_to_globe(self.waypoints, self.setup)

            num_segments = len(self.waypoints)-1
            segment = 0
            for coord1, coord2 in zip(self.waypoints[:-1], self.waypoints[1:]):
                segment = segment+1
                self.create_paths(10, coord1, coord2, output_folder, segment, num_segments) # TODO change scale to 10

            self.successmsg.setText("Paths successfully calculated and saved in folder '"+output_folder+"'. You can now close this window.")
            self.successmsg.setWordWrap(True)



    def create_paths(self, scale, start_global, goal_global, folder_name, segmentindex, num_segments):
        '''This function first creates a distribtion between the three path optimization weights and
        thereafter calculates paths for each combination'''
        # Iterate over different combinations of a, b, and c
        scale = 10
        a_values = np.logspace(0, 1, scale)
        b_values = np.logspace(0, 1, scale)
        c_values = np.logspace(0, 1, scale)
        n = len(list(product(a_values, b_values, c_values)))
        
        # Define start and goal
        setup = Setup('src/mapdata/', 1.0, 0, 0, plot_global=True)
        [start_sim, goal_sim] = transform.from_globe_to_map([start_global, goal_global], setup)
        [start_pixel, goal_pixel] = transform.from_map_to_pixel([start_sim, goal_sim], setup)
        
        done_weights = []
        i=0
        start_time = time.time()
        for a, b, c in product(a_values, b_values, c_values):
            if a+b+c!=0:
                # Status
                i += 1
                self.progressBar.setValue(int(((segmentindex-1)/num_segments + i/(n*num_segments))*100))
                QtWidgets.QApplication.processEvents()
                [a,b,c] = [a,b,c]/(a+b+c)

                if [a,b,c] not in done_weights:
                    done_weights.append([a,b,c])
                    setup = Setup('src/mapdata/', a, b, c, plot_global=True)

                    # Run A* algorithm
                    path, stats = astar.astar(setup.map_size_in_pixel, start_pixel, goal_pixel, setup, allow_diagonal=True)
                    path_globe = transform.from_pixel_to_globe(path, setup)
                    path_sim = transform.from_pixel_to_map(path, setup)

                    # Get total length
                    path = np.array(path_sim)
                    pairwise_distances = np.linalg.norm(path[1:] - path[:-1], axis=1)
                    total_length = np.sum(pairwise_distances)
                    total_pixel = len(path)

                    # Save sum of stats to file
                    stats_sum = np.sum(stats, axis=0, where=[1, 1, 1, 1, 1, 1])
                    if i == 1:
                        with open(folder_name+'/segment'+str(segmentindex)+'_stats.csv', 'w', newline='') as file:
                            stats_header = ['Path no.', 'a', 'b', 'c', 'E_P', 'R_P', 'I_P', 'Length', 'No. pixel']
                            writer = csv.writer(file, delimiter='\t')
                            writer.writerow(stats_header)

                    # Save stats and path coordinates
                    with open(folder_name+'/segment'+str(segmentindex)+'_stats.csv', 'a', newline='') as file:
                        stats_with_weights = np.hstack([i, a, b, c, stats_sum[0:3], total_length, total_pixel])
                        writer = csv.writer(file, delimiter='\t')
                        writer.writerow(stats_with_weights)

                    with open(folder_name+'/segment'+str(segmentindex)+'_paths.csv', 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter='\t')
                        for coord_type in ["LON", "LAT"]:
                            header = [f'Path {i} {coord_type}']
                            coordinates = [str(coord[0 if coord_type == "LON" else 1]) for coord in path_globe]
                            writer.writerow(header + coordinates)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('The calculation took: '+str(elapsed_time/60)+' Minutes.')

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        self.pub_global_path.unregister()


    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass


    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass


    # def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    my_widget = PathCreatorPlugin("src/user_interface/ui/PathCreator.ui")
    my_widget.show()
    sys.exit(app.exec_())

