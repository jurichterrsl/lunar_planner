#!/usr/bin/env python3

'''The basic file for the rqt plugin of the long distance autonomy (LODIA) project'''

import sys
import numpy as np
from python_qt_binding import loadUi, QtWidgets
from mapdata import setup_aristarchus as setup_file
from user_interface.path_planning_widget import PathPlanningWidget


class LunarPathPlanner(QtWidgets.QMainWindow):
    '''
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
    def __init__(self):
        '''Init function for the class'''
        super(LunarPathPlanner, self).__init__()

        # Load parameters from parameters.yaml
        self.setup = setup_file.Setup('src/mapdata/', 0.5, 0.5, 0, False)

        # Create main window and load ui file
        self.mainwindow = QtWidgets.QWidget()
        ui_file = 'src/user_interface/ui/LodiaPlugin.ui'  # Replace with the correct path
        loadUi(ui_file, self.mainwindow)
        self.mainwindow.setWindowTitle('Lunar Path Planner')

        # Init other widget functions
        self.pathplanningwidget = PathPlanningWidget(self.setup)
        QtWidgets.QVBoxLayout(self.mainwindow.plan_path_widget).addWidget(self.pathplanningwidget)

        self.setCentralWidget(self.mainwindow)
        self.show()


    def shutdown_plugin(self):
        # TODO unregister all publishers here
        #self.timer_plot_pos.shutdown()
        pass


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
    standalone_app = LunarPathPlanner()
    sys.exit(app.exec_())