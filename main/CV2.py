import cv2

from main.ApplicationState import ApplicationState

class CV2():
    application_state = ApplicationState()

    def __init__(self):
        super().__init__()
        self.application_state.register_callback("source", self.set_active_port)
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
                print("Port %s is not working." %dev_port)
            else:
                print(camera)
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                    working_sources.append((dev_port, h, w))
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                    available_sources.append((dev_port, h, w))
            dev_port += 1
        print(available_sources)
        return available_sources, working_sources, non_working_sources

    def set_active_port(self, port):
        print("Active Port Changed %s", port)
        self.active_port = port

