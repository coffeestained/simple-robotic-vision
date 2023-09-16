import logging
import signal
import sys

import numpy as np

from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5.QtCore import (
    QSize
)
from PyQt5.QtCore import (
    Qt
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout
)

class InspectorWindow(QMainWindow):

    def __init__(self, dimensions = (350, 250)):
        super().__init__()
        self.dimensions = dimensions
        self.setWindowTitle("Inspector")
        self.resize(QSize(*dimensions))
        self.canvas = QTCanvas(self, width=10, height=8, dpi=100)
        self.setCentralWidget(self.canvas)

    def set_source(self, source):
        pass

    def process_frame(self):
        frame = np.empty( self.dimensions )


class QTCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        figure = pyplot.Figure(figsize=(width, height), dpi=dpi)
        figure.patch.set_alpha(0.0)
        self.axes = figure
        super(QTCanvas, self).__init__(figure)
        self.setStyleSheet("background-color:transparent;")
