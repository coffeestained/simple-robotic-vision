import time
import random

from PyQt5.QtCore import QThreadPool

from core.threading.NetizenThread import NetizenThread
from core.cv.CV2 import CV2
from core.ApplicationState import ApplicationState

from utils.mouse import mouse_move, mouse_click
from utils.cv2 import motion_detection, match_template

cv2 = CV2()
application_state = ApplicationState()

class ActionQueue(list):

    def __setitem__(self, key, value):
        super(ActionQueue, self).__setitem__(key, value)
        print("Item added to queue.")

    def __delitem__(self, value):
        super(ActionQueue, self).__delitem__(value)
        print("Item removed from queue.")

    def __add__(self, value):
        super(ActionQueue, self).__add__(value)
        print("Item added to queue.")

    def __iadd__(self, value):
        super(ActionQueue, self).__iadd__(value)
        print("Item added to queue.")

    def append(self, value):
        super(ActionQueue, self).append(value)
        print("Item added to queue.")

    def remove(self, value):
        super(ActionQueue, self).remove(value)
        print("Item removed from queue.")

class ProgramAPI(object):

    _action_queue = ActionQueue()

    def __new__(cls):
        """Singleton pattern service
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProgramAPI, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.bootstrap_threadpool()
        self.bootstrap_action_listener(self.action_listener)

    # Bootstrap Thread
    def bootstrap_threadpool(self):
        """
        Creates thread pool
        """
        self.threadpool = QThreadPool.globalInstance()

    # Netizen Event Runnable
    def bootstrap_action_listener(self, callback = None):
        """
        A custom runnable thread with optional callback.
        """
        if callback:
            thread = NetizenThread(callback)
            self.threadpool.start(thread)
        else:
            print('Skipping event. No callback.')

    def action_listener(self):
        """
        While action queue has length, do action and pop.
        """
        while True:
            time.sleep(.1)
            if len(self._action_queue) > 0:
                print('Do received action')
                self._action_queue.pop(0)["expression"]()

    def mouse_move(self, target, speed=(random.randint(25000, 38000) / 100000), callback = None):
        self._action_queue.append({
            "expression": lambda: mouse_move(target=target, speed_random=speed),
            "callback": callback
        })

    def mouse_click(self, target, callback = None):
        self._action_queue.append({
            "expression": lambda: mouse_click(target=target),
            "callback": callback
        })

    def object_track(self, template):
        # CV2 Start Tracking An Object
        None
        # returns object id

    def object_exists(self, template, callback = None, dev_mode = None):
        # Bool if object in frame
        self._action_queue.append({
            "expression": lambda: match_template(application_state.active_frame, template, dev_mode),
            "callback": callback
        })


    def text_track(self, text):
        # CV2 + Tesseract
        None
        # returns object id

    def text_exists(self, text):
        # Bool if text exist in frame
        None
        # Returns Bool

    def left_click_object_id(self, object_id):
        None
        # Returns Bool

    def right_click_object_id(self, object_id):
        None
        # Returns Bool

    def toggle_motion_detection(self):
        self._action_queue.append(
            lambda: cv2.toggle_layer("Motion Detection", motion_detection)
        )

        # Returns Bool
        return True

