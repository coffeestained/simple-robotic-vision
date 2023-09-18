import wmi

class WindowsOS():

    def __init__(self):
        super().__init__()
        self.wmi = wmi.WMI()

    def get_processes(self):
        """
        Get Windows Process list
        """
        for process in self.wmi.Win32_Process():
            print(f"{process.ProcessId:<10} {process.Name}")


