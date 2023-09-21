from utils.utils import move_mouse

class ProgramAPI():

    def move_mouse(self, target):
        move_mouse(target)

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

    def left_click_tracked_object(self, objectId):
        None
        # Returns bool

    def right_click_tracked_object(self, objectId):
        None
        # Returns bool
