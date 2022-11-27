## Gui Imports
from PyQt5 import QtCore, QtWidgets, QtGui

## Other Required Imports
import os
import time
import threading
#import math

## Image Processing Imports
import cv2 as cv
from dotenv import load_dotenv
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
#import pytesseract
from PIL import ImageGrab, Image

import numpy as np

## Windows Imports
import wmi
import win32gui
import win32ui
import win32con
import ctypes

# ENV
load_dotenv()

WINDOW = os.getenv('WINDOW')

# Def Function Works, but only once for some reason
def background_screenshot(hwnd, width, height):
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return im

# A class that extends the Thread class
class VisionThread(threading.Thread):

    def __init__(self, fps, process, event, figure, axe):
       threading.Thread.__init__(self)
       self.type = 'Sobel Edge with Motion & Camera Movement detection'
       self.figure = figure
       self.axe = axe
       self.fps = fps
       self.process = process
       self.active = event
       self.start()

    def run(self):
        previousBlurredImage = None

        bbox = win32gui.GetWindowRect(self.process)

        # Requirements
        stereo = None
        if self.type == 'Stereo':
            ## Image Processing Stereo
            stereo = cv.StereoBM_create(numDisparities = 128,
                                        blockSize = 5)
        if self.type == 'Sobel Edge with Motion & Camera Movement detection':
            blink = background_screenshot(self.process, 1920, 1080)
            image = cv.cvtColor(np.asarray(blink), cv.COLOR_RGBA2GRAY)
            # Blur the image
            previousBlurredImage = cv.GaussianBlur(image, (3,3), 0)
        # # DEBUG WHILE
        # while True:
        #     time.sleep(100 / self.fps)
        #     image = ImageGrab.grab(bbox)
        #     print(image)
        #     newImage = background_screenshot(self.process, 1920, 1080)
        #     print(newImage)

        while True:
            # Stop Thread Flag Check
            if self.active.is_set():
                    break

            # Loop continues its thing
            # Based on type of class
            if self.type == 'Stereo':

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

            if self.type == 'Sobel Edge with Motion Detection':

                image = cv.cvtColor(np.asarray(ImageGrab.grab(bbox)), cv.COLOR_RGB2GRAY)
                # Blur the image
                blurredImage = cv.GaussianBlur(image, (3,3), 0)

                # Motion Detection Section
                if previousBlurredImage is None:
                    # First frame; there is no previous one yet
                    previousBlurredImage = blurredImage
                    continue

                # calculate difference and update previous frame
                diffImages = cv.absdiff(src1=previousBlurredImage, src2=blurredImage)
                previousBlurredImage = blurredImage

                # Dilute the image a bit to make differences more seeable; more suitable for contour detection
                kernel = np.ones((5, 5))
                diffImages = cv.dilate(diffImages, kernel, 1)

                # Only take different areas that are different enough (>20 / 255)
                threshImage = cv.threshold(src=diffImages, thresh=20, maxval=255, type=cv.THRESH_BINARY)[1]
                # End Motion Detection

                # 1 Second Divided by the Expected Frames Per Second
                time.sleep(1 / self.fps)

                # Sobel Edge Detection
                edgesx = cv.Sobel(blurredImage, -1, dx=1, dy=0, ksize=1)
                edgesy = cv.Sobel(blurredImage, -1, dx=0, dy=1, ksize=1)

                # Draw Countours from Motion Detection to Edges Image
                contours, _ = cv.findContours(image=threshImage, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE)
                drawnCountours = cv.drawContours(image=threshImage, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)

                # Finalize Image
                edges = edgesx + edgesy + drawnCountours

                # Display
                self.axe.clear()
                self.axe.imshow(edges, alpha=.8)
                self.figure.draw_idle()

            if self.type == 'Sobel Edge with Motion & Camera Movement detection':
                blink = background_screenshot(self.process, 1920, 1080)
                image = cv.cvtColor(np.asarray(blink), cv.COLOR_RGBA2GRAY)
                # Blur the image
                blurredImage = cv.GaussianBlur(image, (3,3), 0)

                # Motion Detection Section
                if previousBlurredImage is None:
                    # First frame; there is no previous one yet
                    previousBlurredImage = blurredImage
                    continue

                # calculate difference and update previous frame
                diffImages = cv.absdiff(src1=previousBlurredImage, src2=blurredImage)
                previousBlurredImage = blurredImage

                # Dilute the image a bit to make differences more seeable; more suitable for contour detection
                kernel = np.ones((5, 5))
                diffImages = cv.dilate(diffImages, kernel, 1)

                # Only take different areas that are different enough (>20 / 255)
                threshImage = cv.threshold(src=diffImages, thresh=20, maxval=255, type=cv.THRESH_BINARY)[1]
                # End Motion Detection

                # 1 Second Divided by the Expected Frames Per Second
                time.sleep(1 / self.fps)

                # Sobel Edge Detection
                edgesx = cv.Sobel(blurredImage, -1, dx=1, dy=0, ksize=1)
                edgesy = cv.Sobel(blurredImage, -1, dx=0, dy=1, ksize=1)

                # Draw Countours from Motion Detection to Edges Image
                contours, _ = cv.findContours(image=threshImage, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE)
                drawnCountours = cv.drawContours(image=threshImage, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)

                # Finalize Image
                edges = edgesx + edgesy + drawnCountours

                # Display
                self.axe.clear()
                self.axe.imshow(edges, alpha=.8)
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

        self.preview = QTCanvas(self, width=10, height=8, dpi=100)

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
        axe = self.preview.axes.add_subplot(111, facecolor="none", position=[0, 0, 0, 0])
        VisionThread(fps=5, process=processID, event=self.active, figure=self.preview, axe=axe)
        pyplot.show()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.active.set()
            self.close()
            quit()


class QTCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        figure = pyplot.Figure(figsize=(width, height), dpi=dpi)
        figure.patch.set_alpha(0.0)
        self.axes = figure
        super(QTCanvas, self).__init__(figure)
        self.setStyleSheet("background-color:transparent;")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    form = Overlay()
    app.exec_()
