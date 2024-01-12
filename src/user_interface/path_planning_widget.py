'''The basic file for the rqt plugin of the long distance autonomy (LODIA) project'''

import sys
import numpy as np
from python_qt_binding import loadUi, QtWidgets
from mapdata import setup_aristarchus as setup_file
from globalplanner import astar, transform
from user_interface.map_widget import MapWidget

class PathPlanningWidget(QtWidgets.QWidget):
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
    PLOT_GLOBE = False

    def __init__(self, setup):
        '''Init function for the class'''
        super().__init__()

        # Create QWidget and load ui file
        ui_file = ui_file = 'src/user_interface/ui/PathPlanningWidget.ui'
        loadUi(ui_file, self)

        # Load the setup file and init path variables
        self.setup = setup
        self.wp_pixel = None
        self.wp_global = None
        self.wp_sim = None
        self.path_pixel = None
        self.start = None
        self.goal = None

        # Init widget functions for adjusting path
        self.mapwidget = MapWidget(width=self.setup.maps.n_px_width, 
                                   height=self.setup.maps.n_px_height, 
                                   extent=self.setup.get_geo_xmin_ymin_xmax_ymax(),
                                   pixel_size=self.setup.maps.pixel_size,
                                   map_image=self.setup.maps.map_image, 
                                   maps_array=self.setup.maps.maps_array, 
                                   layer_names=self.setup.maps.layer_names,
                                   toolbar=True,
                                   plot_global=False)
        QtWidgets.QVBoxLayout(self.mapwidget_adjust).addWidget(self.mapwidget)
        self.mapwidget.canvas.mpl_connect('button_press_event', self.click_on_map_sets_new_goal)

        self.plan_button.clicked.connect(self.calc_and_plot_path)
        self.alpha_slider.valueChanged.connect(self.slider_value_change)
        self.beta_slider.valueChanged.connect(self.slider_value_change)
        self.gamma_slider.valueChanged.connect(self.slider_value_change)
        self.map_up.clicked.connect(self.change_to_next_map)
        self.map_down.clicked.connect(self.change_to_previous_map)
        self.map_down.setEnabled(False)

        # Init widget functions to compare different paths
        self.four_wp_pixel = [[],[],[],[]]
        self.four_wp_global = [[],[],[],[]]
        self.four_wp_sim = [[],[],[],[]]
        self.four_goals = [[],[],[],[]]

        self.mapwidget_cmp = []
        for i in range(4):
            new_widget = MapWidget(width=self.setup.maps.n_px_width,
                                   height=self.setup.maps.n_px_height,
                                   extent=self.setup.get_geo_xmin_ymin_xmax_ymax(),
                                   pixel_size=self.setup.maps.pixel_size,
                                   map_image=self.setup.maps.map_image, 
                                   maps_array=self.setup.maps.maps_array, 
                                   layer_names=self.setup.maps.layer_names,
                                   toolbar=False,
                                   plot_global=False)
            new_widget.plot_four_layers_with_details()
            self.mapwidget_cmp.append(new_widget)
        QtWidgets.QVBoxLayout(self.graph_path0).addWidget(self.mapwidget_cmp[0])
        QtWidgets.QVBoxLayout(self.graph_path1).addWidget(self.mapwidget_cmp[1])
        QtWidgets.QVBoxLayout(self.graph_path2).addWidget(self.mapwidget_cmp[2])
        QtWidgets.QVBoxLayout(self.graph_path3).addWidget(self.mapwidget_cmp[3])

        self.mapwidget_4images = MapWidget(width=self.setup.maps.n_px_width, 
                                           height=self.setup.maps.n_px_height, 
                                           extent=self.setup.get_geo_xmin_ymin_xmax_ymax(),
                                           pixel_size=self.setup.maps.pixel_size,
                                           map_image=self.setup.maps.map_image, 
                                           maps_array=self.setup.maps.maps_array, 
                                           layer_names=self.setup.maps.layer_names,
                                           toolbar=True,
                                           plot_global=False)
        self.mapwidget_4images.prepare_four_sat_pics()

        QtWidgets.QVBoxLayout(self.img_paths).addWidget(self.mapwidget_4images)

        self.load_coordinates.clicked.connect(self.load_and_plot_coordinates)

        self.save_path0.clicked.connect(self.add_path0)
        self.save_path1.clicked.connect(self.add_path1)
        self.save_path2.clicked.connect(self.add_path2)
        self.save_path3.clicked.connect(self.add_path3)
        self.save_path0.setEnabled(False)
        self.save_path1.setEnabled(False)
        self.save_path2.setEnabled(False)
        self.save_path3.setEnabled(False)

        self.delete_path0.clicked.connect(self.reset_path0)
        self.delete_path1.clicked.connect(self.reset_path1)
        self.delete_path2.clicked.connect(self.reset_path2)
        self.delete_path3.clicked.connect(self.reset_path3)

        self.execute0.clicked.connect(self.execute_path0)
        self.execute1.clicked.connect(self.execute_path1)
        self.execute2.clicked.connect(self.execute_path2)
        self.execute3.clicked.connect(self.execute_path3)
        self.execute_buttons = [self.execute0, self.execute1, self.execute2, self.execute3]
        for button in self.execute_buttons:
            button.setEnabled(False)

        # Prepare table to compare paths
        self.tablewidget = QtWidgets.QTableWidget()
        self.tablewidget.setRowCount(6)
        self.tablewidget.setColumnCount(5)
        QtWidgets.QVBoxLayout(self.results_table).addWidget(self.tablewidget)
        self.tablewidget.setItem(0, 0, QtWidgets.QTableWidgetItem('Spec'))
        self.tablewidget.setItem(0, 1, QtWidgets.QTableWidgetItem('Path 1'))
        self.tablewidget.setItem(0, 2, QtWidgets.QTableWidgetItem('Path 2'))
        self.tablewidget.setItem(0, 3, QtWidgets.QTableWidgetItem('Path 3'))
        self.tablewidget.setItem(0, 4, QtWidgets.QTableWidgetItem('Path 4'))
        self.tablewidget.setItem(1, 0, QtWidgets.QTableWidgetItem('Total energy cost'))
        self.tablewidget.setItem(2, 0, QtWidgets.QTableWidgetItem('Total risk cost'))
        self.tablewidget.setItem(3, 0, QtWidgets.QTableWidgetItem('Total scientific value'))
        self.tablewidget.setItem(4, 0, QtWidgets.QTableWidgetItem('Total cost'))
        self.tablewidget.setItem(5, 0, QtWidgets.QTableWidgetItem('Distance covered'))

        self.current_map = -1
        self.mapwidget.plot_layer_local(self.current_map)


    def load_and_plot_coordinates(self):
        self.start = (self.startx.value(), self.starty.value())
        self.goal = (self.goalx.value(), self.goaly.value())
        print(self.start, self.goal)
        self.mapwidget.plot_point_on_canvas(self.start, 'start')
        self.mapwidget.plot_point_on_canvas(self.goal, 'goal')


    def plot_layer_with_start_goal_and_path(self):
        '''Plots the current selected layer (self.current_map) and if applicable also the path'''
        self.mapwidget.plot_layer_local(self.current_map)
        self.mapwidget.plot_path_on_canvas(self.wp_sim,'planned_path')
        if self.start:
            self.mapwidget.plot_point_on_canvas(self.start, 'start')
        if self.goal:
            self.mapwidget.plot_point_on_canvas(self.goal, 'goal')


    def calc_and_plot_path(self):
        '''Calculates path from predefined path and plots result on the map'''
        # Load values for alpha, beta and gamma
        self.setup.ALPHA = self.alpha_slider.value()/20
        self.setup.BETA = self.beta_slider.value()/20
        self.setup.GAMMA = self.gamma_slider.value()/20

        # Plan path
        print("Calculation of global path started.")
        self.calc_path(self.start, self.goal)
        print("Global path successfully calculated.")
        self.plot_layer_with_start_goal_and_path()

        # Now that path is calculated it can also be saved
        self.save_path0.setEnabled(True)
        self.save_path1.setEnabled(True)
        self.save_path2.setEnabled(True)
        self.save_path3.setEnabled(True)


    def click_on_map_sets_new_goal(self, event):
        '''Clicking with the right mouse button sets a new goal on the canvas'''
        try:
            input_point = (event.xdata, event.ydata)
            [(index_x, index_y)] = transform.from_sim_to_pixel([input_point], self.setup)
            if self.setup.maps.maps_array[index_x, index_y, 4] != 1:
                if event.button == 1:
                    self.start = input_point
                    self.plot_layer_with_start_goal_and_path()
                elif event.button == 3:
                    self.goal = input_point
                    self.plot_layer_with_start_goal_and_path()
            else:
                print("A point in a banned area was chosen. Please choose a new goal by klicking with the right mouse button on the map.")

        except (ValueError, TypeError):
            print("Goal outside map chosen. Choose a next goal while klicking with the right mouse button on the map.")
       

    def calc_path(self, start, goal):
        '''Runs the A* algorithm'''
        # Run A* algorithm
        [start_pixel, goal_pixel] = transform.from_sim_to_pixel([start, goal], self.setup)
        self.path_pixel, self.stats = astar.astar(self.setup.map_size_in_pixel, start_pixel, goal_pixel, \
                                           self.setup.h_func, self.setup.g_func, allow_diagonal=True)
        if self.path_pixel.any() == -1:
            print("No valid path found! Please check input parameters.")
        # Sampling of waypoints
        n = 1
        last_wp = self.path_pixel[self.path_pixel.shape[0]-1,:]
        self.wp_pixel = np.vstack([self.path_pixel[::n,:], last_wp])

        # Transform in different coordinate systems in save in one .dat file
        self.wp_global = transform.from_pixel_to_globe(self.wp_pixel, self.setup)
        self.wp_sim = transform.from_pixel_to_sim(self.wp_pixel, self.setup)

        wp_all = np.concatenate((self.wp_global, self.wp_sim, self.wp_pixel), axis=1)
        column_names = np.array(['# Longitute', 'Latitude', 'x in sim', 'y in sim', \
                                 'Row in arr', 'Col in arr'])
        wp_header = '\t'.join(['{:<10}'.format(name) for name in column_names])
        np.savetxt('src/globalplanner/data/waypoints.dat', wp_all, \
                   header=wp_header, comments='', delimiter='\t', fmt='%-3f')
        
        # Save the statistics into one .dat file
        path_coordinates = transform.from_pixel_to_globe(self.path_pixel, self.setup)
        stats_header = '\t\t'.join(('LON', 'LAT', 'E_P', 'R_P', 'I_P', 'B_P', 'g_func', 'h_func'))
        stats_with_wp = np.hstack((path_coordinates[1:], np.array(self.stats)))
        stats_with_wp = np.vstack((stats_with_wp, np.sum(stats_with_wp, axis=0, where=[0,0,1,1,1,1,1,1])))
        np.savetxt('src/globalplanner/data/stats.dat', stats_with_wp, \
                   header=stats_header, comments='', delimiter='\t', fmt='%-3f')


    def slider_value_change(self):
        '''Updates the label that shows the value of each slider'''
        self.value_alpha.setText(str(self.alpha_slider.value()/20))
        self.value_beta.setText(str(self.beta_slider.value()/20))
        self.value_gamma.setText(str(self.gamma_slider.value()/20))


    def change_to_next_map(self):
        '''
        Changes background of map one map layer down
        The following numbers define the maps: -1 = satellite picture; 0...n = layers of Maps object
        '''
        self.current_map = self.current_map + 1
        # Enable/ disable button function if on first/ last map
        if self.current_map == self.setup.maps.maps_array.shape[2]-1:
            self.map_up.setEnabled(False)
        elif self.current_map == 0:
            self.map_down.setEnabled(True)
        
        self.plot_layer_with_start_goal_and_path()


    def change_to_previous_map(self):
        '''Changes background of map one map layer up'''
        self.current_map = self.current_map - 1
        # Enable/ disable button function if on first/ last map
        if self.current_map == -1:
            self.map_down.setEnabled(False)
        elif self.current_map == self.setup.maps.maps_array.shape[2]-2:
            self.map_up.setEnabled(True)

        self.plot_layer_with_start_goal_and_path()


    def add_path0(self):
        '''Plots path 0 in the mapwidget cmp'''
        self.add_pathx(0)
        print("Saved as path 1.")

    def add_path1(self):
        '''Plots path 1 in the mapwidget cmp'''
        self.add_pathx(1)
        print("Saved as path 2.")

    def add_path2(self):
        '''Plots path 2 in the mapwidget cmp'''
        self.add_pathx(2)
        print("Saved as path 3.")

    def add_path3(self):
        '''Plots path 3 in the mapwidget cmp'''
        self.add_pathx(3)
        print("Saved as path 4.")

    def add_pathx(self, x):
        '''Adds selected path'''
        # Save calculated values to list
        self.four_wp_pixel[x] = self.wp_pixel
        self.four_wp_global[x] = self.wp_global
        self.four_wp_sim[x] = self.wp_sim
        self.four_goals[x] = self.goal
        # Calculate full distance of path
        path = np.array(self.wp_sim)
        pairwise_distances = np.linalg.norm(path[1:] - path[:-1], axis=1)
        total_length = np.sum(pairwise_distances)
        # Change detailed view
        self.mapwidget_cmp[x].plot_four_layers_with_details()
        self.mapwidget_cmp[x].add_path_to_four_layer_view(self.wp_sim, self.path_pixel)
        # Change satellite view
        self.mapwidget_4images.clear_one_of_four_sat_pics(x)
        self.mapwidget_4images.plot_path_on_one_of_four_sat_pic(self.wp_sim, x)
        # Change table data
        summed_stats = np.sum(self.stats, axis=0)
        self.tablewidget.setItem(1, x+1, QtWidgets.QTableWidgetItem(str(summed_stats[0])))
        self.tablewidget.setItem(2, x+1, QtWidgets.QTableWidgetItem(str(summed_stats[1])))
        self.tablewidget.setItem(3, x+1, QtWidgets.QTableWidgetItem(str(summed_stats[2])))
        self.tablewidget.setItem(4, x+1, QtWidgets.QTableWidgetItem(str(summed_stats[4])))
        self.tablewidget.setItem(5, x+1, QtWidgets.QTableWidgetItem(str(total_length)))
        # Change state of execution button
        self.execute_buttons[x].setEnabled(True)


    def reset_path0(self):
        '''Deletes path 0'''
        self.reset_pathx(0)

    def reset_path1(self):
        '''Deletes path 1'''
        self.reset_pathx(1)

    def reset_path2(self):
        '''Deletes path 2'''
        self.reset_pathx(2)

    def reset_path3(self):
        '''Deletes path 3'''
        self.reset_pathx(3)

    def reset_pathx(self, x):
        '''Deletes chosen path'''
        # Clears both plots
        self.mapwidget_cmp[x].plot_four_layers_with_details()
        self.mapwidget_4images.clear_one_of_four_sat_pics(x)
        # Disenables execution button
        self.execute_buttons[x].setEnabled(False)


    def execute_path0(self):
        '''Chooses path 0 to execute'''
        self.execute_pathx(0)

    def execute_path1(self):
        '''Chooses path 1 to execute'''
        self.execute_pathx(1)

    def execute_path2(self):
        '''Chooses path 2 to execute'''
        self.execute_pathx(2)

    def execute_path3(self):
        '''Chooses path 3 to execute'''
        self.execute_pathx(3)

    def execute_pathx(self, x):
        '''Loads data from path again to be executed by the path following widget'''
        # Load calculated values from list
        print('Path '+str(x+1)+' chosen.')
        self.wp_pixel = self.four_wp_pixel[x]
        self.wp_global = self.four_wp_global[x]
        self.wp_sim = self.four_wp_sim[x]
        self.goal = self.four_goals[x]
        for button in self.execute_buttons:
            button.setEnabled(False)
        self.execute_buttons[x].setStyleSheet("background-color: blue")


    def shutdown_plugin(self):
        # TODO unregister all publishers here
        print("Shutdown Path Planning Widget.")


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
    setup = setup_file.Setup('../mapdata/', 0.5, 0.5, 0, False)  # Make sure to provide appropriate parameters
    path_planning_widget = PathPlanningWidget(setup)
    path_planning_widget.show()
    sys.exit(app.exec_())