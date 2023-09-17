import logging
import signal
import sys

from main.NetizenThread import NetizenThread
from main.ApplicationState import ApplicationState

import numpy as np

from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5.QtCore import (
    QSize, QThreadPool, Qt
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout
)

application_state = ApplicationState()

class InspectorWindow(QMainWindow):

    def __init__(self, dimensions = (350, 250)):
        super().__init__()
        self.threadpool = QThreadPool.globalInstance()
        self.dimensions = dimensions
        self.setWindowTitle("Inspector")
        self.resize(QSize(*dimensions))
        self.canvas = QTCanvas(self, width=10, height=8, dpi=100)
        self.axe = self.canvas.axes.add_subplot(111, facecolor="none", position=[0, 0, 0, 0])
        self.setCentralWidget(self.canvas)
        self.register_listeners()

    def register_listeners(self):
        application_state.register_callback("active_frame", self.new_frame_receiver)

    def new_frame_receiver(self, frame):
        if isinstance(frame, np.ndarray):
            self.threadpool_event(lambda: self.process_frame(frame))

    # Netizen Event Runnable
    def threadpool_event(self, callback = None):
        """
        A custom runnable thread with optional callback.
        """
        if callback:
            thread = NetizenThread(callback)
            self.threadpool.start(thread)
        else:
            print('Skipping event. No callback.')

    def process_frame(self, frame):
        self.axe.clear()
        self.axe.imshow(frame.astype(np.uint8), alpha=1)
        self.canvas.draw_idle()
        print(frame)


class QTCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        figure = pyplot.Figure(figsize=(width, height), dpi=dpi)
        figure.patch.set_alpha(0.0)
        self.axes = figure
        super(QTCanvas, self).__init__(figure)
        self.setStyleSheet("background-color:transparent;")
