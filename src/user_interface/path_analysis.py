import sys
from PyQt5 import QtWidgets
from python_qt_binding import loadUi
from user_interface.map_widget import MapWidget
from user_interface.cluster_widget import ClusterWidget
from mapdata import setup_aristarchus as setup_file


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
        QtWidgets.QVBoxLayout(self.analysisplot).addWidget(self.clusterwidget)
        self.recalculatebutton.clicked.connect(self.recalculate_and_plot_clusters)



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
        #self.mapwidget.plot_path_on_canvas(self.path, color)
        # plot paths

    def recalculate_and_plot_clusters(self):
        '''Reads how many clusters user wants and updates cluster plot'''
        number_of_clusters = self.numberofclusters.value()
        # Get the value from the QSpinBox
        self.clusterwidget.recalculate_and_plot(number_of_clusters)

    def show_widget(self):
        self.show()
        sys.exit(app.exec_())

    def open_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_name:
            print(f"Selected file: {file_name}")

# Example usage
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    my_main_window = MyQtMainWindow("src/user_interface/ui/MainWindow.ui")
    my_main_window.show_widget()

