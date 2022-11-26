## Gui Imports
from PyQt5 import QtCore, QtWidgets, QtGui

## Other Required Imports
import time
import threading

## Image Processing Imports
import win32gui
import cv2 as cv
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import pytesseract
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter

import numpy as np

## Windows Imports
import wmi

## Image Processing Stereo
stereo = cv.StereoBM_create(numDisparities = 128,
                            blockSize = 5)

# A class that extends the Thread class
class VisionThread(threading.Thread):

    def __init__(self, fps, process, event, figure, axe):
       threading.Thread.__init__(self)
       self.type = 'Canny Edge'
       self.figure = figure
       self.axe = axe
       self.fps = fps
       self.process = process
       self.active = event
       self.start()

    def run(self):
        while True:
            if self.type == 'Stereo':
                if self.active.is_set():
                    break

                try:
                    win32gui.SetForegroundWindow(self.process)
                except:
                    pass
                finally:
                    pass

                bbox = win32gui.GetWindowRect(self.process)

                leftEye = cv.cvtColor(np.asarray(ImageGrab.grab(bbox)), cv.COLOR_RGB2GRAY)
                # 1 Second Divided by the Expected Frames Per Second
                time.sleep(1 / self.fps)

                rightEye = cv.cvtColor(np.asarray(ImageGrab.grab(bbox)), cv.COLOR_RGB2GRAY)

                # 1 Second Divided by the Expected Frames Per Second
                time.sleep(1 / self.fps)

                # Calculate Disparity
                disparity = stereo.compute(leftEye, rightEye)

                # DEBUG
                self.axe.clear()
                self.axe.imshow(disparity)
                self.figure.draw_idle()

            if self.type == 'Canny Edge':
                if self.active.is_set():
                    break

                try:
                    win32gui.SetForegroundWindow(self.process)
                except:
                    pass
                finally:
                    pass

                bbox = win32gui.GetWindowRect(self.process)

                eyes = cv.cvtColor(np.asarray(ImageGrab.grab(bbox)), cv.COLOR_RGB2GRAY)
                # 1 Second Divided by the Expected Frames Per Second
                time.sleep(1 / self.fps)

                # Blur the image
                img_blur = cv.GaussianBlur(eyes, (3,3), 0)

                # Canny Edge Detection
                edges = cv.Canny(image=img_blur, threshold1=100, threshold2=200)

                # Display
                self.axe.clear()
                img = self.axe.imshow(edges, alpha=0.6)
                self.figure.draw_idle()

class Overlay(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        ## Active Bool
        self.active = threading.Event()

        ## WMI
        self.f = wmi.WMI()

        ## Get Available Windows
        self.winlist, toplist = [], []

        def enum_cb(hwnd, results):
            self.winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

        win32gui.EnumWindows(enum_cb, toplist)

        ## Overlay Settings
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.showFullScreen()

        ## Netizen Methods
        self.generateLayout()
        self.generateNetizenWidgets()

        self.show()

    def generateLayout(self):
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addStretch()

    def generateNetizenWidgets(self):
        ## Client Selector
        clientSelectorContainer = QtWidgets.QWidget()
        clientSelectorLayout = QtWidgets.QVBoxLayout(clientSelectorContainer)

        clientSelectorLabel = QtWidgets.QLabel('Select Client:')
        clientSelectorLabel.setFont(QtGui.QFont('Arial', 15))
        clientSelectorLabel.setStyleSheet("color : #03c04a; background-color: rgba(0,0,0,.30);")
        clientSelectorLayout.addWidget(clientSelectorLabel)

        self.clientSelector = QtWidgets.QComboBox()

        # Iterating through all the running processes
        for hwnd, title in self.winlist:
            if title:
                self.clientSelector.addItem(title, userData=hwnd)

        # Listen for clientSelector changes
        self.clientSelector.currentIndexChanged.connect(self.onClientSelected)

        clientSelectorLayout.addWidget(self.clientSelector)
        clientSelectorLayout.addStretch()

        self.layout.addWidget(clientSelectorContainer)
        ## End Client Selector

        ## Status Indicator
        statusContainer = QtWidgets.QWidget()
        statusLayout = QtWidgets.QVBoxLayout(statusContainer)

        statusLabel = QtWidgets.QLabel('Status:')
        statusLabel.setFont(QtGui.QFont('Arial', 15))
        statusLabel.setStyleSheet("color : #03c04a; background-color: rgba(0,0,0,.30);")
        status = QtWidgets.QLabel('Active')
        status.setFont(QtGui.QFont('Arial', 15))
        status.setStyleSheet("color : #03c04a; background-color: rgba(0,0,0,.30);")
        statusLayout.addWidget(statusLabel, alignment = (QtCore.Qt.AlignTop))
        statusLayout.addWidget(status, alignment = (QtCore.Qt.AlignTop))
        statusLayout.addStretch()

        self.layout.addWidget(statusContainer)
        ## End Status

        ## Preview Indicator
        previewContainer = QtWidgets.QWidget()
        previewLayout = QtWidgets.QVBoxLayout(previewContainer)

        previewLabel = QtWidgets.QLabel('Preview:')
        previewLabel.setFont(QtGui.QFont('Arial', 15))
        previewLabel.setStyleSheet("color : #03c04a; background-color: rgba(0,0,0,.30);")

        self.preview = QTCanvas(self, width=5, height=4, dpi=100)

        previewLayout.addWidget(previewLabel, alignment = (QtCore.Qt.AlignTop))
        previewLayout.addWidget(self.preview, alignment = (QtCore.Qt.AlignTop))
        previewLayout.addStretch()

        self.layout.addWidget(previewContainer)
        ## End Preview

    def onClientSelected(self):
        processID = self.clientSelector.currentData()
        self.active.set()
        time.sleep(3)
        self.active.clear()
        axe = self.preview.axes.add_subplot(111, facecolor="none")
        VisionThread(fps=5, process=processID, event=self.active, figure=self.preview, axe=axe)
        time.sleep(10)
        pyplot.show()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.active.set()
            self.close()
            quit()

class QTCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=40, height=32, dpi=100):
        figure = pyplot.Figure(figsize=(width, height), dpi=dpi)
        figure.patch.set_alpha(0.33)
        self.axes = figure
        super(QTCanvas, self).__init__(figure)
        self.setStyleSheet("background-color:transparent;")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    form = Overlay()
    app.exec_()
