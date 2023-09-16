import logging
import random
import time

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QComboBox,
    QFrame
)

class NetizenSelect(QFrame):
    '''
    NetizenSelect Componentry
    '''
    def __init__(self, label = None):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        if label:
            self.layout.addWidget(QLabel(label))

        self.select = QComboBox()
        self.layout.addWidget(self.select)

    def change_visible_state(self, state):
        if state:
            self.show()
        else:
            self.hide()

    def add_select_option(self, label, user_data = None):
        self.select.addItem(label, userData = user_data)

    def set_callback(self, callback):
        print(callback)
        self.select.currentIndexChanged.connect(callback)

