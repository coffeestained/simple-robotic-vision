
class ApplicationState(object):
    """
    State Store Singleton Pattern
    """
    source = None
    program = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ApplicationState, cls).__new__(cls)
        return cls.instance
