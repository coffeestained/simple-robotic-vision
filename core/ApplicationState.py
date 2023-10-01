class ApplicationState(object):
    """
    State Store Singleton Pattern
    """
    _observer_callbacks = {
        'source': [],
        'program': [],
        'active_frame': [],
        'previous_frame': [],
        'active_previous_diff': []
    }
    _source = None
    _program = None
    _previous_frame = None
    _active_frame = None
    _active_previous_diff = None

    def __new__(cls):
        """Singleton pattern service
        """
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
    def active_frame(self, frame):
        self._active_frame = frame
        self._notify_observers("active_frame", frame)

    @property
    def previous_frame(self):
        return self._previous_frame

    @previous_frame.setter
    def previous_frame(self, frame):
        self._previous_frame = frame
        self._notify_observers("previous_frame", frame)

    @property
    def active_previous_diff(self):
        return self._active_previous_diff

    @active_previous_diff.setter
    def active_previous_diff(self, diff):
        self._active_previous_diff = diff
        self._notify_observers("active_previous_diff", diff)

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
