import logging
import signal
import sys

from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from main.NetizenThread import NetizenThread

from utils.utils import WindowsOS

logging.basicConfig(format="%(message)s", level=logging.INFO)
signal.signal(signal.SIGINT, signal.SIG_DFL)

app = QApplication(sys.argv)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bootstrapThreading()
        self.bootstrapUI()

    def bootstrapThreading(self):
        self.bootstrapThreadpool()
        self.bootstrapRunnable(lambda: self.bootstrapWindowsOS())

    # Bootstrap Thread
    def bootstrapThreadpool(self):
        self.threadpool = QThreadPool.globalInstance()

    # Netizen Event Runnable
    def bootstrapRunnable(self, callback = None):
        if callback:
            thread = NetizenThread(callback)
            self.threadpool.start(thread)
        else:
            print('Skipping event. No callback.')

    # Bootstrap Windows Processes
    def bootstrapWindowsOS(self):
        self.windows = WindowsOS()
        self.windows.get_processes()
        self.finishedLoading()

    # Finished Loading
    def finishedLoading(self):
        self.label.setText("Welcome to Netizen.")

    def bootstrapUI(self):
        self.setWindowTitle("Netizen")
        self.resize(350, 250)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create Label Widget
        self.label = QLabel("Loading...")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Create Start Stop Button
        self.startStopButton = QPushButton("Start")
        self.startStopButton.clicked.connect(lambda: self.bootstrapRunnable(self.toggleStartStop))

        # Create Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.startStopButton)

        # Set Layout
        self.centralWidget.setLayout(self.layout)

    def toggleStartStop(self):
        if self.startStopButton.text() == "Start":
            self.startStopButton.setText("Stop")
        else:
            self.startStopButton.setText("Start")

    def somethingHappened(self):
        print('test')


window = Window()
window.show()
sys.exit(app.exec())

