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
    QComboBox,
)

from main.NetizenThread import NetizenThread
from main.Windows import WindowsOS
from main.CV2 import CV2

logging.basicConfig(format="%(message)s", level=logging.INFO)
signal.signal(signal.SIGINT, signal.SIG_DFL)

app = QApplication(sys.argv)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bootstrapThreading()
        self.bootstrapUI()

    def bootstrapThreading(self):
        """
        Initiates thread pool and required bootstrapped threads
        """
        self.bootstrapThreadpool()
        self.bootstrapRunnable(lambda: self.bootstrapWindowsOS())
        self.bootstrapRunnable(lambda: self.bootstrapCV2())

    # Bootstrap Thread
    def bootstrapThreadpool(self):
        """
        Assigns thread pool
        """
        self.threadpool = QThreadPool.globalInstance()

    # Netizen Event Runnable
    def bootstrapRunnable(self, callback = None):
        """
        A custom runnable thread with optional callback.
        """
        if callback:
            thread = NetizenThread(callback)
            self.threadpool.start(thread)
        else:
            print('Skipping event. No callback.')

    # Bootstrap Windows Processes
    def bootstrapWindowsOS(self):
        """
        Utilizes core windows class and gathers required data.
        """
        self.windows = WindowsOS()
        self.windows.get_processes()


        # Show
        self.finishedLoading()

    # Bootstrap CV2 Class
    def bootstrapCV2(self):
        """
        Utilizes core cv2 class and gathers required data.
        """
        self.cv2 = CV2()
        self.cv2.get_sources()

        # Show
        self.finishedLoading()

    # Finished Loading
    def finishedLoading(self):
        self.label.setText("Welcome to Netizen.")

        # # Windows Select Added to Layout
        # self.processes = QComboBox()
        # self.processes.hide()
        # self.processes.addItem('One')
        # self.processes.addItem('Two')
        # self.processes.addItem('Three')
        # self.processes.addItem('Four')
        # self.layout.addWidget(self.processes)

        # # Video Select Added to Layout
        # self.sources = QComboBox()
        # self.sources.hide()
        # self.sources.addItem('One')
        # self.sources.addItem('Two')
        # self.sources.addItem('Three')
        # self.sources.addItem('Four')
        # self.layout.addWidget(self.sources)

        self.startStopButton.show()
        # self.sources.show()
        # self.processes.show()

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
        self.startStopButton.hide()
        self.startStopButton.clicked.connect(lambda: self.bootstrapRunnable(self.toggleStartStop))

        # Create Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)

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

