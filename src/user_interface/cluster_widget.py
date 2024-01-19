from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class ClusterWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create a Matplotlib Figure and Axes3D
        self.figure_3d = plt.figure()
        self.figure_3d.tight_layout()
        self.axes_3d = self.figure_3d.add_subplot(111, projection='3d')

        self.axes_3d.set_title("Cost distribution")
        self.axes_3d.set_xlabel('Energy')
        self.axes_3d.set_ylabel('Risk')
        self.axes_3d.set_zlabel('Scientific Interest')

        # Embed the Matplotlib plot into the widget
        self.mpl_canvas = FigureCanvasQTAgg(self.figure_3d)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.mpl_canvas)

    def recalculate_and_plot(self, number_of_clusters):
        # Clear the current 3D plot
        print(number_of_clusters)
        self.plot_3d_data_based_on_clusters(number_of_clusters)
        self.mpl_canvas.draw()

    def plot_3d_data_based_on_clusters(self, number_of_clusters):
        # Add your logic here to plot 3D data based on the number of clusters
        # Replace the following lines with your actual plotting code
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]
        z = [5, 3, 1, 7, 9]
        self.axes_3d.scatter(x, y, z)

