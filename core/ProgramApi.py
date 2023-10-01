import time
import random

from PyQt5.QtCore import QThreadPool

from core.threading.NetizenThread import NetizenThread

from utils.mouse import mouse_move, mouse_click

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
                self._action_queue.pop(0)()

    def mouse_move(self, target, speed=(random.randint(25000, 38000) / 100000)):
        self._action_queue.append(lambda: mouse_move(target=target, speed_random=speed))

    def mouse_click(self, target):
        self._action_queue.append(lambda: mouse_click(target=target))

    def track_object(self, object):
        # CV2 Start Tracking An Object
        None
        # returns object id

    def look_for_objects(self, list_of_objects):
        # Bool if objects exist in camera frame
        None
        # Returns tf

    def track_text_as_object(self, text):
        # CV2 + Tesseract
        None
        # returns object id

    def look_for_text(self, look_for_text):
        # Bool if text exist in camera frame
        None
        # Returns tf

    def left_click_tracked_object(self, object_id):
        None
        # Returns bool

    def right_click_tracked_object(self, object_id):
        None
        # Returns bool

