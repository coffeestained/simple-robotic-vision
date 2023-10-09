import cv2, time, numpy as np, copy
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from core.ApplicationState import ApplicationState
from core.threading.NetizenThread import NetizenThread

from utils.cv2 import format_image

application_state = ApplicationState()

class CV2():
    """
    CV2 State Store
    """
    tracked_objects = []
    tracked_text = []
    active_actions = []

    def __new__(cls):
        """Singleton pattern service
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(CV2, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()
        application_state.register_callback("source", self.set_active_port)
        application_state.register_callback("active_frame", self.do_actions)
        (
            self.available_sources,
            self.working_sources,
            self.non_working_sources,
        ) = self.get_sources()

    def get_sources(self):
        """
        Test the ports and returns a tuple with the available ports and the ones that are working.
        """
        non_working_sources = []
        dev_port = 0
        working_sources = []
        available_sources = []
        while len(non_working_sources) < 6: # if there are more than 5 non working ports stop the testing.
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                non_working_sources.append(dev_port)
            else:
                is_reading, _ = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    working_sources.append((dev_port, h, w))
                else:
                    available_sources.append((dev_port, h, w))
            dev_port += 1
        return available_sources, working_sources, non_working_sources

    def set_active_port(self, port):
        """
        Is triggered when ApplicationState webcam selection changes
        """
        self.active_port = port

        # Update Source If Already Running
        if getattr(self, "current_vision_worker", None):
            self.current_vision_worker.source = self.active_port
            self.current_vision_worker.load_capture_source()
        else:
            # Generate New Thread & Worker
            self.current_vision_thread = QThread()
            self.current_vision_worker = VisionWorker()
            self.current_vision_worker.source = self.active_port
            self.current_vision_worker.load_capture_source()
            self.current_vision_worker.moveToThread(self.current_vision_thread)
            self.current_vision_thread.started.connect(self.current_vision_worker.vision_task)
            self.current_vision_thread.start()

    def set_active_program(self, program):
        """
        Sets the active program & loads the program .. must have source loaded
        """
        if getattr(self, "current_vision_worker", None):
            self.current_vision_worker.program = program

    def toggle_layer(self, label, layer):
        if getattr(self, "current_vision_worker", None):
            self.current_vision_worker.toggle_layer({
                "label": label,
                "expression": layer
            })

    def do_actions(self, frame):
        """
        Active frame changed, checking active actions
        """
        if getattr(self, "current_vision_worker", None):
            for action in self.active_actions:
                print(action)

# Step 1: Create a worker class
class VisionWorker(QObject):
    source = None
    _layers = []
    active = True

    def toggle_layer(self, layer):
        if not any(l['label'] == layer['label'] for l in self._layers):
            self._layers.append(layer)
        else:
            self._layers = list(filter(lambda l: l['label'] == layer, self._layers))

    def load_capture_source(self):
        self.cap = cv2.VideoCapture(self.source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def load_program(self):
        self.cap = cv2.VideoCapture(self.source)

    def vision_task(self):
        """continuous-running task."""
        while self.active:
            time.sleep((1/10)) # quarter of a second
            _, frame = self.cap.read()
            frame = format_image(frame)
            if isinstance(application_state.previous_frame, np.ndarray):
                application_state.active_previous_diff = cv2.absdiff(src1=application_state.previous_frame, src2=application_state.active_frame)
            application_state.previous_frame = application_state.active_frame
            application_state.active_frame = frame
            inspector_frame = copy.deepcopy(frame)
            for layer in self._layers:
                inspector_frame += layer["expression"](application_state.active_previous_diff)
            application_state.inspector_frame = inspector_frame

        self.cap.release()


