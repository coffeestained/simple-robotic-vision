import logging
import random
import time

from PyQt5.QtCore import QRunnable, pyqtSlot

class NetizenThread(QRunnable):
    '''
    Worker thread w/ callback
    '''
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @pyqtSlot()
    def run(self):
        '''
        Work thread run
        '''
        self.callback()
