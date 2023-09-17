
class ApplicationState(object):
    """
    State Store Singleton Pattern
    """
    _observer_callbacks = {
        'source': [],
        'program': [],
        'active_frame': []
    }
    _source = None
    _program = None
    _active_frame = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ApplicationState, cls).__new__(cls)
        return cls.instance

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, current):
        self._source = current
        self._notify_observers("source", current)

    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, current):
        self._program = current
        self._notify_observers("program", current)

    @property
    def active_frame(self):
        return self._active_frame

    @active_frame.setter
    def active_frame(self, current):
        self._active_frame = current
        self._notify_observers("active_frame", current)

    def _notify_observers(self, prop, current):
        """
        Notify Observer Callbacks
        """
        if prop in self._observer_callbacks:
            observers = self._observer_callbacks[prop]
            if isinstance(observers, list):
                for callback in observers:
                    callback(current)

    def register_callback(self, prop, callback):
        """
        Register Observer Callbacks
        """
        if prop in self._observer_callbacks:
            observers = self._observer_callbacks[prop]
            if isinstance(observers, list):
                observers.append(callback)