import logging
import signal
import sys
import time
import random
import pyautogui
import win32api

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
from core.threading.NetizenThread import NetizenThread
from core.ui.NetizenComponents import NetizenSelect
from core.cv.CV2 import CV2
from core.ProgramApi import ProgramAPI

program_api = ProgramAPI()

class DevWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bootstrap_threading()
        self.bootstrap_ui()
        self.bootstrap_listeners()

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

        # Find & Bounding Box Around Clipboard Image Test
        self.find_create = QPushButton("Find, Create Bounding Box and Track / Clipboard Image")
        self.find_create.clicked.connect(lambda: self.bootstrap_runnable(self.track_clipboard_to_object_id))

        # Finds Tracked Object and Clicks
        self.track_and_click = QPushButton("Click Tracked Image")
        self.track_and_click.clicked.connect(lambda: self.bootstrap_runnable(self.move_and_click_tracked_object_id))

        # Create Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mouse_movement)
        self.layout.addWidget(self.find_create)
        self.layout.addWidget(self.track_and_click)

        # Set Layout
        self.central_widget.setLayout(self.layout)

    def do_mouse_movement(self, point = pyautogui.size()):
        """
        Tests Humanized Mouse Movement
        """
        x = random.randint(0, point[0])
        y = random.randint(0, point[1])
        print("Moving to %s x and %s y" %(x, y), )
        program_api.mouse_move((x, y))
        program_api.mouse_click((x, y))

    def track_clipboard_to_object_id(self):
        """
        Tests Computer Vision, Tracks an object if found
        """
        x = random.randint(0, point[0])
        y = random.randint(0, point[1])
        print("Moving to %s x and %s y" %(x, y), )
        program_api.mouse_move((x, y))
        program_api.mouse_click((x, y))

    def move_and_click_tracked_object_id(self):
        """
        Tests moving and clicking tracked object
        """
        x = random.randint(0, point[0])
        y = random.randint(0, point[1])
        print("Moving to %s x and %s y" %(x, y), )
        program_api.mouse_move((x, y))
        program_api.mouse_click((x, y))

    def bootstrap_listeners(self):
        self.bootstrap_runnable(self.listen_for_clicks)

    def listen_for_clicks(self):
        """
        Listeners for clicks & their prints coordinates
        """
        state_left = win32api.GetKeyState(0x01)  # Left button down = 0 or 1. Button up = -127 or -128
        state_right = win32api.GetKeyState(0x02)  # Right button down = 0 or 1. Button up = -127 or -128

        while True:
            a = win32api.GetKeyState(0x01)
            b = win32api.GetKeyState(0x02)

            if a != state_left:  # Button state changed
                state_left = a
                if a < 0:
                    print("Click Down %s x and %s y" %pyautogui.position(), )
                else:
                    print("Click Up %s x and %s y" %pyautogui.position(), )

            time.sleep(0.001)


