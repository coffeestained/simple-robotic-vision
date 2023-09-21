from collections.abc import Callable

class BaseProgram(object):
    """
    Base Program designed to be extended.add()

    A program, basically, orders jobs based on priority.
    Looks for a job that matches the requirements
    """
    _observer_callbacks = {
        'jobs': [],
        'current_index': []
    }
    _jobs = []
    _current_job = 0

    @property
    def jobs(self):
        return self._jobs

    @jobs.setter
    def jobs(
        self,
        args
    ):
        """
        Setter for the Job Object

        Args:
            is_valid (Callable[[], bool]): Is Valid? Returns bool
            callback (Callable[[], bool]): If Valid Trigger Callback
            priority (int): Priority of the job >= 0
        """
        new_job = Job(
            args[0],
            args[1],
            args[2]
        )
        self._jobs.append(
            new_job
        )
        self._jobs.sort(key = lambda x: x.priority)
        self._notify_observers("jobs", new_job)

    def to_job(self, index):
        self._current_job = index

    def previous_job(self):
        self._current_job -= 1
        self._current_job = len(self._jobs) if self._current_job < 0 else self._current_job

    def next_job(self):
        self._current_job += 1
        self._current_job = 0 if len(self._jobs) < self._current_job else self._current_job

    def start_program(self):
        self.continue_program()

    def continue_program(self):
        print(self._current_job)
        print(self._jobs)
        try:
            if len(self._jobs):
                if isinstance(self._jobs[self._current_job], Job):
                    # Check Validity & Do Job
                    if self._jobs[self._current_job].is_valid():
                        self._jobs[self._current_job].callback()
                    else:
                        print('Invalid job, checking next Index.')

                    # Next Job
                    self.continue_program()
                else:
                    print("Invalid job type.")
            else:
                print('No jobs added.')
        except Exception:
            print('Something went wrong.')


    ### Call Back / Observer Section
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

class Job(object):

    def __init__(
        self,
        is_valid: Callable[[], bool],
        callback: Callable[[], bool],
        priority: int = 0,
    ):
        self.priority = priority
        self.is_valid = is_valid
        self.callback = callback
