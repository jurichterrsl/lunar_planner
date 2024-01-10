#!/usr/bin/env python3

'''The basic file for the rqt plugin of the long distance autonomy (LODIA) project'''

import sys
import rospkg
path_root = rospkg.RosPack().get_path('lodia_planner')
sys.path.append(str(path_root))

import numpy as np
import os
from python_qt_binding import loadUi, QtWidgets
from lodia_planner.src.mapdata import setup_aristarchus as setup_file
# setup_allmend setup_allmend_small setup_wells_extended
from lodia_planner.src.rqt.path_planning_widget import PathPlanningWidget

class LodiaPlugin():
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
    REALLIFE = True

    def __init__(self, context):
        '''Init function for the class'''
        super().__init__(context)
        # # Process standalone plugin command-line arguments
        # from argparse import ArgumentParser
        # parser = ArgumentParser()
        # # Add argument(s) to the parser.
        # parser.add_argument("-q", "--quiet", action="store_true",
        #                     dest="quiet",
        #                     help="Put plugin in silent mode")
        # args, unknowns = parser.parse_known_args(context.argv())
        # if not args.quiet:
        #   print('arguments: ', args)
        #   print('unknowns: ', unknowns)
        # Load parameters from parameters.yaml

        # Create QWidget and load ui file
        self.mainwindow = QtWidgets.QWidget()
        self.path_to_root = rospkg.RosPack().get_path('lodia_planner')
        ui_file = os.path.join(self.path_to_root, 'ui', 'LodiaPlugin.ui')
        loadUi(ui_file, self.mainwindow)
        self.mainwindow.setWindowTitle('Lodia Planner')
        context.add_widget(self.mainwindow)

        # Init other widget functions
        self.setup = setup_file.Setup('../mapdata/', 0.5, 0.5, 0, False)
        self.pathplanningwidget = PathPlanningWidget(context, self.setup)
        QtWidgets.QVBoxLayout(self.mainwindow.plan_path_widget).addWidget(self.pathplanningwidget)
        self.mainwindow.save_button.clicked.connect(self.save_path)
        self.mainwindow.return2_button.clicked.connect(self.return_to_following)

        # Init stacked widget
        self.mainwindow.stackedwidget.setCurrentWidget(self.mainwindow.plan_path_tab)


    def save_path(self):
        '''Loads the path from path planning widget and sends it to path following widget'''
        # Load results from pathplanningwidget
        print('This function is not included yet.')


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
    from rqt_gui.main import Main
    plugin = 'lodia_plugin.LodiaPlugin'  # Replace with the correct package name and class
    main = Main(filename=plugin)
    sys.exit(main.main(standalone=plugin))