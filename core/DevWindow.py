import logging
import signal
import sys
import random
import pyautogui

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

from core.ApplicationState import ApplicationState
from core.NetizenThread import NetizenThread
from core.NetizenComponents import NetizenSelect
from core.CV2 import CV2
from utils.utils import move_mouse

class DevWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bootstrap_threading()
        self.bootstrap_ui()

    def bootstrap_threading(self):
        """
        Initiates thread pool and required bootstrapped threads
        """
        self.bootstrap_threadpool()

    # Bootstrap Thread
    def bootstrap_threadpool(self):
        """
        Creates thread pool
        """
        self.threadpool = QThreadPool.globalInstance()

    # Netizen Event Runnable
    def bootstrap_runnable(self, callback = None):
        """
        A custom runnable thread with optional callback.
        """
        if callback:
            thread = NetizenThread(callback)
            self.threadpool.start(thread)
        else:
            print('Skipping event. No callback.')

    def bootstrap_ui(self):
        """
        Generates core UI.
        """
        self.setWindowTitle("Netizen")
        self.resize(350, 250)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create Label Widget
        self.label = QLabel("Dev Tools")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Create Mouse Movement Test
        self.mouse_movement = QPushButton("Random Human Mouse Movement")
        self.mouse_movement.clicked.connect(lambda: self.bootstrap_runnable(self.do_mouse_movement))

        # Create Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mouse_movement)

        # Set Layout
        self.central_widget.setLayout(self.layout)

    def do_mouse_movement(self):
        """
        Tests Humanized Mouse Movement
        """
        x = random.randint(0, pyautogui.size()[0])
        y = random.randint(0, pyautogui.size()[1])
        print("Moving to %s x and %s y" %(x, y), )
        move_mouse((x, y))



