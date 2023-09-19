import logging
import signal
import sys

from core.NetizenThread import NetizenThread
from core.ApplicationState import ApplicationState

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
        self.canvas = QTCanvas(self, width=1, height=1, dpi=50)
        self.axe = self.canvas.axes.add_subplot(111, facecolor="none", position=[0, 0, 0, 0])
        self.axe.axes.get_xaxis().set_visible(False)
        self.axe.axes.get_yaxis().set_visible(False)
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

    def process_frame(self, frame):
        self.axe.clear()
        self.axe.imshow(frame.astype(np.uint8), alpha=1)
        self.canvas.draw_idle()

class QTCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=1, height=1, dpi=100):
        figure = pyplot.Figure(figsize=(width, height), dpi=dpi)
        figure.patch.set_alpha(0.0)
        self.axes = figure
        super(QTCanvas, self).__init__(figure)
        self.setStyleSheet("background-color:transparent;")
