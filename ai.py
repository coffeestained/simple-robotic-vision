## Gui Imports
from PyQt5 import QtCore, QtWidgets, QtGui

## Other Required Imports
import os
import time
import datetime
import threading
from queue import Queue
from functools import reduce
#import math

## Image Processing Imports
import cv2 as cv
import pytesseract # Py OCRs
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PIL import Image
import numpy as np # Scientific Computing

## Windows Imports
import wmi
import win32gui
import win32ui
import ctypes

# ENV
from dotenv import load_dotenv
load_dotenv()

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

# Global And Configurable Variables/Queues
AVAILABLE_FEATURES = os.getenv('AVAILABLE_FEATURES').split(',')
ENABLED_FEATURES = Queue()
ENABLED_FEATURES.join()

# Background process screenshot w11
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

    def __init__(self, fps, process, event, figure, previewWidget, axe, queue):
       threading.Thread.__init__(self)
       self.figure = figure
       self.previewWidget = previewWidget
       self.axe = axe
       self.fps = fps
       self.process = process
       self.active = event
       self.queue = queue
       self.wb = cv.xphoto.createGrayworldWB()
       self.wb.setSaturationThreshold(0.99)
       self.start()

    def enchance_image(self, frame):
        temp_img = frame
        img_wb = self.wb.balanceWhite(temp_img)
        img_lab = cv.cvtColor(img_wb, cv.COLOR_BGR2Lab)
        l, a, b = cv.split(img_lab)
        clahe = cv.createCLAHE(clipLimit=2.0,tileGridSize=(8, 8))
        img_l = clahe.apply(l)
        img_clahe = cv.merge((img_l, a, b))
        return cv.cvtColor(img_clahe, cv.COLOR_Lab2BGR)

    def get_sub_images(image, contours):
        """
        Crop images according to the contour bounding boxes and return them in a
        list.

        Args:
            image: numpy.ndarray
            contours: list

        Returns:
            list
        """
        sub_images = []
        for cnt in contours:
            x, y, w, h = cv.boundingRect(cnt)
            sub_image = image[slice(y, y+h), slice(x, x+w)]
            sub_images.append(sub_image)
        return sub_images

    def run(self):
        # Stuff Variables

        # Features/Layers Enabled
        enabledFeatures = []

        # Babies first steps
        previousFrame = background_screenshot(self.process, 1920, 1080)
        previousFrameGray = cv.cvtColor(np.asarray(previousFrame), cv.COLOR_RGBA2GRAY)
        previousFrameBlurred = cv.GaussianBlur(previousFrameGray, (3,3), 0)
        previousFrameHSV = cv.cvtColor(np.asarray(previousFrame), cv.COLOR_BGR2HSV)

        currentFrame = background_screenshot(self.process, 1920, 1080)
        currentFrameGray = cv.cvtColor(np.asarray(currentFrame), cv.COLOR_RGBA2GRAY)
        currentFrameBlurred = cv.GaussianBlur(currentFrameGray, (3,3), 0)
        currentFrameHSV = cv.cvtColor(np.asarray(currentFrame), cv.COLOR_BGR2HSV)

        #    HOG Descriptors
        # hog = cv.HOGDescriptor()
        # hog.setSVMDetector(cv.CascadeClassifier.detectMultiScale(
        #     currentFrameGray,
        #         scaleFactor=1.3,
        #         minNeighbors=4,
        #         minSize=(30, 30),
        #         flags=cv.CASCADE_SCALE_IMAGE
        # ))

        while True:

            # Stop Watch Init
            beginTime = datetime.datetime.now()

            # Final Image Delcration
            finalImage = []

            # Check for enabled layer changes
            if self.queue.empty() == False:
                enabledFeatures = self.queue.get(block=False)
                self.queue.task_done()

            # Stop Thread Flag Check
            if self.active.is_set():
                    break

            # If Active
            if enabledFeatures:

                # Rotate Frames for diff checks
                previousFrame = currentFrame
                previousFrameGray = currentFrameGray
                previousFrameHSV = currentFrameHSV
                previousFrameBlurred = currentFrameBlurred

                time.sleep(1 / self.fps)

                currentFrame = background_screenshot(self.process, 1920, 1080)
                currentFrameGray = cv.cvtColor(self.enchance_image(np.asarray(currentFrame)), cv.COLOR_RGBA2GRAY)
                currentFrameHSV = cv.cvtColor(self.enchance_image(np.asarray(currentFrame)), cv.COLOR_BGR2HSV)
                currentFrameBlurred = cv.GaussianBlur(currentFrameGray, (3, 3), 0)

                frameDiff = diffImages = cv.absdiff(src1=previousFrameBlurred, src2=currentFrameBlurred)

                # Set Image
                finalImage.append( np.empty( (1080,1920) ) )

            # Loop continues its thing
            # Based on type of class
            if 'Stereo' in enabledFeatures:

                ## Image Processing Stereo
                stereo = cv.StereoBM_create(numDisparities = 128,
                                            blockSize = 5)

                # Calculate Disparity
                finalImage.append(stereo.compute(previousFrameGray, currentFrameGray))

            if 'Motion Detection' in enabledFeatures:
                # Motion Detection Section ##################################

                # Dilute the image a bit to make differences more seeable; more suitable for contour detection
                kernel = np.ones((5, 5))
                diffImages = cv.dilate(frameDiff, kernel, 1)

                # Only take different areas that are different enough (>20 / 255)
                threshImage = cv.threshold(src=diffImages, thresh=20, maxval=255, type=cv.THRESH_BINARY)[1]

                # Draw Countours from Motion Detection to Edges Image
                contours, _ = cv.findContours(image=threshImage, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE)
                drawnContours = cv.drawContours(image=threshImage, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)

                finalImage.append(drawnContours)
                # End Motion Detection ##############################################

            if 'Sobel Edge' in enabledFeatures:
                # Sobel Edge Start

                # Sobel Edge Detection
                edgesx = cv.Sobel(currentFrameBlurred, -1, dx=1, dy=0, ksize=1)
                edgesy = cv.Sobel(currentFrameBlurred, -1, dx=0, dy=1, ksize=1)
                finalImage.append(edgesx)
                finalImage.append(edgesy)

                # Sobel Edge End

            if 'OCR' in enabledFeatures:

                # Text Detection Start

                lower = np.array([0, 0, 218])
                upper = np.array([157, 54, 255])
                mask = cv.inRange(currentFrameHSV, lower, upper)

                # Create horizontal kernel and dilate to connect text characters
                kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,3))
                dilate = cv.dilate(mask, kernel, iterations=5)

                # Find contours and filter using aspect ratio
                # Remove non-text contours by filling in the contour
                cnts = cv.findContours(dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if len(cnts) == 2 else cnts[1]
                for c in cnts:
                    x,y,w,h = cv.boundingRect(c)
                    ar = w / float(h)
                    if ar < 5:
                        cv.drawContours(dilate, [c], -1, (0,0,0), -1)

                # Bitwise dilated image with mask, invert, then OCR
                result = 255 - cv.bitwise_and(dilate, mask)
                data = pytesseract.image_to_string(result, lang='eng', config='--psm 6')
                print(data)

                # Text Detection End

            if 'Biped' in enabledFeatures:
                pass

            # Display
            if finalImage and self.previewWidget.isVisible():
                toBeShown = reduce(lambda a, b: a + b, finalImage)
                self.axe.clear()
                self.axe.imshow(toBeShown, alpha=1)
                self.figure.draw_idle()

            # End Stop Watch
            endTime = datetime.datetime.now()
            stopWatchDiff = (endTime - beginTime)
            # MS Conver
            diff_in_milliseconds = stopWatchDiff.total_seconds() * 1000
            # Round to Nearest Nearest Whole Millisceond
            diff_in_milliseconds = round(diff_in_milliseconds)

            # Print
            diffInMilliseconds = str(diff_in_milliseconds) + " ms"
            print(diffInMilliseconds)



class Overlay(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        ## Active Bool
        self.active = threading.Event()

        ## WMI
        self.f = wmi.WMI()

        ## Get Available Windows
        self.winlist, toplist = [], []

        ## UI Widgets
        self.previewWidget = QtWidgets.QWidget()

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

        ## Feature Selector
        featureSelectorContainer = QtWidgets.QWidget()
        featureSelectorLayout = QtWidgets.QVBoxLayout(featureSelectorContainer)

        featureSelectorLabel = QtWidgets.QLabel('Select Features:')
        featureSelectorLabel.setFont(QtGui.QFont('Arial', 15))
        featureSelectorLabel.setStyleSheet("color : #03c04a; background-color: rgba(0,0,0,.30);")
        featureSelectorLayout.addWidget(featureSelectorLabel)

        self.featureSelector = FeatureCheckBox()

        # Iterating through all the running processes
        for feature in AVAILABLE_FEATURES:
            self.featureSelector.addItem(feature, userData=feature)

        featureSelectorLayout.addWidget(self.featureSelector)
        featureSelectorLayout.addStretch()

        self.layout.addWidget(featureSelectorContainer)
        ## End Feature Selector

        ## Preview Indicator
        previewLayout = QtWidgets.QVBoxLayout(self.previewWidget)

        previewLabel = QtWidgets.QLabel('Preview:')
        previewLabel.setFont(QtGui.QFont('Arial', 15))
        previewLabel.setStyleSheet("color : #03c04a; background-color: rgba(0,0,0,.30);")

        self.preview = QTCanvas(self, width=10, height=8, dpi=100)

        previewLayout.addWidget(previewLabel, alignment = (QtCore.Qt.AlignTop))
        previewLayout.addWidget(self.preview, alignment = (QtCore.Qt.AlignTop))
        previewLayout.addStretch()

        ## Settings Selector
        settingsSelectorContainer = QtWidgets.QWidget()
        settingsSelectorLayout = QtWidgets.QVBoxLayout(settingsSelectorContainer)

        settingsSelectorLabel = QtWidgets.QLabel('Settings:')
        settingsSelectorLabel.setFont(QtGui.QFont('Arial', 15))
        settingsSelectorLabel.setStyleSheet("color : #03c04a; background-color: rgba(0,0,0,.30);")
        settingsSelectorLayout.addWidget(settingsSelectorLabel)

        self.settingsSelector = SettingsCheckBox(previewWidget = self.previewWidget)
        self.settingsSelector.currentIndexChanged.connect(self.onSettingsToggle)

        # Iterating through all the running processes
        self.settingsSelector.addItem('Toggle Preview', userData='Preview')

        settingsSelectorLayout.addWidget(self.settingsSelector)
        settingsSelectorLayout.addStretch()

        self.layout.addWidget(settingsSelectorContainer)
        ## End Settings Selector

        self.layout.addWidget(self.previewWidget)
        ## End Preview

    def onClientSelected(self):
        processID = self.clientSelector.currentData()
        self.active.set()
        time.sleep(3)
        self.active.clear()
        axe = self.preview.axes.add_subplot(111, facecolor="none", position=[0, 0, 0, 0])
        VisionThread(fps=5, process=processID, event=self.active, figure=self.preview, previewWidget=self.previewWidget, axe=axe, queue=ENABLED_FEATURES)
        pyplot.show()

    def onSettingsToggle(self):
        processID = self.settingsSelector.currentData()
        if (processID == 'Preview'):
            if (self.previewWidget.isVisible()):
                self.previewWidget.setVisible(False)
            else:
                self.previewWidget.setVisible(True)

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


# Custom PYQT Classes
class FeatureCheckBox(QtWidgets.QComboBox):

    def __init__(self):
        super(FeatureCheckBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        features = []

        # Handle Item State
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

        # Updated New Features
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == QtCore.Qt.Checked:
                features.append(item.text())

        ENABLED_FEATURES.put(features)

    # Extension of Class Method: addItem
    def addItem(self, item, userData):

        # Add Item
        super().addItem(item, userData=item)

        # TODO: Inefficient. We only need to setCheckState of the added item
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

        # Pass Extension
        pass


class SettingsCheckBox(QtWidgets.QComboBox):

    def __init__(self, previewWidget):
        super(SettingsCheckBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        self.previewWidget = previewWidget

    def handleItemPressed(self, index):
            # Handle Item State
            item = self.model().itemFromIndex(index)
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
                self.previewWidget.setVisible(False)
            else:
                item.setCheckState(QtCore.Qt.Checked)
                self.previewWidget.setVisible(True)

    # Extension of Class Method: addItem
    def addItem(self, item, userData):

        # Add Item
        super().addItem(item, userData=item)

        # TODO: Inefficient. We only need to setCheckState of the added item
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(QtCore.Qt.Checked)

        # Pass Extension
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    form = Overlay()
    app.exec_()
