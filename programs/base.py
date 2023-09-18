from collections.abc import Callable

class BaseProgram(object):
    """
    Base Program designed to be extended.add()

    A program, basically, orders jobs based on priority.
    Looks for a job that matches the requirements
    """
    _jobs = []
    _current_index = 0

    @property
    def jobs(self):
        return self._jobs

    @jobs.setter
    def jobs(
        self,
        is_valid: Callable[[], bool],
        callback: Callable[[], bool],
        priority: int = 0,
    ):
        """
        Setter for the Job Object

        Args:
            is_valid (Callable[[], bool]): Is Valid? Returns bool
            callback (Callable[[], bool]): If Valid Trigger Callback
            priority (int): Priority of the job >= 0
        """
        self._jobs.append(
            Job(
                is_valid,
                callback,
                priority
            )
        )
        self._jobs.sort(key = lambda x: x["priority"])
        self._notify_observers("jobs", current)

    def start_program():
        self.continue_program()

    def continue_program():
        if len(self._jobs):
            if isinstance(self._jobs[self._current_index], Job):
                if self._jobs[self._current_index].is_valid():
                    self._jobs[self._current_index].callback()
                else:
                    print('Invalid job, checking next Index.')

                # Next Job
                self._current_index = self._current_index + 1
                self.run_program()
            else:
                print("Invalid job type.")
        else:
            print('No jobs added.')


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
