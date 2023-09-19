import logging
import signal
import sys
import os
from pynput.keyboard import Key, Listener

# ENV
from dotenv import load_dotenv
load_dotenv()

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
from core.InspectorWindow import InspectorWindow
from core.DevWindow import DevWindow
from core.NetizenThread import NetizenThread
from core.NetizenComponents import NetizenSelect
from core.Windows import WindowsOS
from core.CV2 import CV2
from programs.example_program.main import Program

# Logging
logging.basicConfig(format="%(message)s", level=logging.INFO)

# Closing program
signal.signal(signal.SIGINT, signal.SIG_DFL)
def on_press(key):
    pass
def on_release(key):
    if key == Key.esc:
        os._exit(1)
        return signal.SIGINT

# Env
configuration = os.getenv('CONFIGURATION')

app = QApplication(sys.argv)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bootstrap_threading()
        self.bootstrap_ui()
        Program()

    def bootstrap_threading(self):
        """
        Initiates thread pool and required bootstrapped threads
        """
        self.bootstrap_threadpool()
        self.bootstrap_runnable(lambda: self.bootstrap_cv2())
        self.bootstrap_runnable(lambda: self.bootstrap_listener())
        # Windows processes unneeded for now
        #self.bootstrap_runnable(lambda: self.bootstrap_windows_os())

    # Bootstrap Listener for keys
    def bootstrap_listener(self):
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

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

    # Bootstrap Windows Processes
    def bootstrap_windows_os(self):
        """
        Utilizes core windows class and gathers required data.
        """
        self.windows = WindowsOS()
        self.windows.get_processes()

        # Show
        self.finished_loading()

    # Bootstrap CV2 Class
    def bootstrap_cv2(self):
        """
        Utilizes core cv2 class and gathers required data.
        """
        self.cv2 = CV2()
        self.available_sources = self.cv2.working_sources
        print(self.available_sources)
        # Add Sources to ComboBox
        for source in self.available_sources:
            self.sources.add_select_option("Camera %s" %(source[0]), source[0])

        # Link callback
        self.sources.set_callback(self.set_source)

        # Show
        self.finished_loading()

    # Finished Loading
    def finished_loading(self):
        self.label.setText("Welcome to Netizen.")

        # Show Components
        self.processes.change_visible_state(True)
        self.sources.change_visible_state(True)
        self.start_stop_button.show()

    def bootstrap_ui(self):
        """
        Generates core UI.
        """
        self.setWindowTitle("Netizen")
        self.resize(350, 250)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create Label Widget
        self.label = QLabel("Loading...")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Create Start Stop Button
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.hide()
        self.start_stop_button.clicked.connect(lambda: self.bootstrap_runnable(self.toggle_start_stop))

        # Create Processes Select
        self.processes = NetizenSelect("Select Proccess")
        self.processes.change_visible_state(False)

        # Create Video Sources Select
        self.sources = NetizenSelect("Select Video Source")
        self.sources.change_visible_state(False)

        # Create AI Program Select
        self.programs = NetizenSelect("Select AI Program")
        self.sources.change_visible_state(False)

        # Create Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sources)
        self.layout.addWidget(self.processes)
        self.layout.addWidget(self.start_stop_button)

        # Set Layout
        self.central_widget.setLayout(self.layout)

    def set_source(self, source):
        """
        Set Application State Source (Camera Feed)
        """
        applicationState.source = source

    def toggle_start_stop(self):
        """
        Toggles Start Stop of Loading Program
        """
        if self.start_stop_button.text() == "Start":
            self.start_stop_button.setText("Stop")
        else:
            self.start_stop_button.setText("Start")

applicationState = ApplicationState()

window = Window()
window.show()

inspectorWindow = InspectorWindow()
inspectorWindow.show()

if configuration == "dev":
    devWindow = DevWindow()
    devWindow.show()

sys.exit(app.exec())

