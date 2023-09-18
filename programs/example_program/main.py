from programs.base import BaseProgram

class Program(BaseProgram):
    """
    An example program that adds a priority 0 and 1 job.
    It checks if it's valid and then executes the job.
    """
    def __init__():
        # Register Job One with Higher Prio
        self.jobs = (
            self.job_one_is_valid,
            self.job_one,
            1
        )
        # Register Job Two with Lower Prio
        self.jobs = (
            self.job_two_is_valid,
            self.job_two,
            0
        )
        self.start_program()

    def job_one_is_valid():
        return False

    def job_two_is_valid():
        return True

    def job_one():
        print('One Triggered')

    def job_two():
        print("Two Triggered")
