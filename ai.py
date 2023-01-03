## Gui Imports
from PyQt5 import QtCore, QtWidgets, QtGui

## Other Required Imports
import os
import time
import math
import datetime
import threading
from queue import Queue
from functools import reduce
import asyncio

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

class PreviewImage:

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def add_layer(self, key, val):
        setattr(self, key, val)

    def get_layer(self, key):
        try:
            return getattr(self, key)
        except:
            return False

class GridImage:

    def __init__(self, currentFrame, rowColCount):

        # Get Shape
        (h, w) = currentFrame.shape[:2]

        # declare attributes
        attributes = {}

        # Row rowColCount
        for rowIndex in range(rowColCount):
            for colIndex in range(rowColCount):

                xStartPos = w // rowColCount * ( rowIndex + 0 )
                xEndPos = w // rowColCount * ( rowIndex + 1 )

                yStartPos = h // rowColCount * ( colIndex + 0 )
                yEndPos = h // rowColCount * ( colIndex + 1 )


                key = str(rowIndex) + '.' + str(colIndex)

                #topLeft = image[0:cY, 0:cX]
                #topRight = image[0:cY, cX:w]
                attributes[key] = currentFrame[ yStartPos: yEndPos, xStartPos: xEndPos ]
                if (rowIndex == 0 and colIndex == 0 or rowIndex == rowColCount - 1 and colIndex == rowColCount - 1):

                    print( xStartPos, xEndPos, yStartPos, yEndPos)
                    print(attributes[key])
                    print(h, w)

        for key in attributes:

            setattr(self, key, attributes[key])

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def reset(self, currentFrame, rowColCount):
        # Get Shape
        (h, w) = currentFrame.shape[:2]

        # declare attributes
        attributes = {}

        # Row rowColCount
        for rowIndex in range(rowColCount):
            for colIndex in range(rowColCount):

                xStartPos = w // rowColCount * ( rowIndex + 0 )
                xEndPos = w // rowColCount * ( rowIndex + 1 )

                yStartPos = h // rowColCount * ( colIndex + 0 )
                yEndPos = h // rowColCount * ( colIndex + 1 )

                key = str(rowIndex) + '.' + str(colIndex)

                attributes[key] = currentFrame[ yStartPos: yEndPos, xStartPos: xEndPos ]

        for key in attributes:
            setattr(self, key, attributes[key])

    def update(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])

    def as_view(self):

        # Declare Repsonse
        response = None

        # Opts
        grid_length = len(self.__dict__.items())
        sqRt = math.sqrt(grid_length)
        count = 0

        # Response Structuring
        rows = []
        row =  []
        for attr, value in self.__dict__.items():

            # Increase count
            count = count + 1

            # Value
            x, y, w, h = cv.boundingRect(cv.cvtColor(np.asarray(value), cv.COLOR_RGBA2GRAY))
            value = cv.rectangle(value, (x, y), (x + w, y + h), 255, 1)

            # Append to Row
            row.append(value)

            # If index total square root
            if count % sqRt == 0 or count == 0:
                # Push to final
                rows.append(row)

                # Reset Row
                row = []

        return self.concat_vh(rows)

    def concat_vh(self, as_response):

        # As Concat Verticle and Horizontal
        return cv.hconcat([cv.vconcat(list_h)
                            for list_h in as_response])

    def set_grid(self, key, img):
        setattr(self, key, img)

    def find_anchor_point(self, tile):
        try:
            return getattr(self, tile)
        except:
            return False

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

       # SFM Options
       self.detectedContours = []
       self.previousFrameEdges = None

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

    def findTrackedObjects(self, frame):
        tracked = cv.goodFeaturesToTrack(frame, 12, .05, 350)
        return tracked

    def run(self):
        # Stuff Variables

        # Features/Layers Enabled
        enabledFeatures = []

        # Babies first steps
        currentFrame = self.enchance_image(np.asarray(background_screenshot(self.process, 1920, 1080)))
        currentFrameGray = cv.cvtColor(currentFrame, cv.COLOR_RGBA2GRAY)
        currentFrameHSV = cv.cvtColor(currentFrame, cv.COLOR_BGR2HSV)
        currentFrameBlurred = cv.GaussianBlur(currentFrameGray, (3, 3), 0)

        # Declare Grid
        # superimpose = GridImage(currentFrame, 10)

        # Final Image Delcration
        previewImage = PreviewImage()

        while True:

            # Stop Watch Init
            beginTime = datetime.datetime.now()

            # Check for enabled layer changes
            if self.queue.empty() == False:
                enabledFeatures     = self.queue.get(block=False)
                self.queue.task_done()

            # Stop Thread Flag Check
            if self.active.is_set():
                    break

            # Technically only enforces a minimum fps rather than a true fps.
            # For instance, if 5 fps selected I believe that would return .20 in a sleep
            # However, class computation would then increase the time for a full frame
            # to generate.
            time.sleep(1 / self.fps)

            # If Active
            if enabledFeatures:

                # Rotate Frames for diff checks
                previousFrame = currentFrame
                previousFrameGray = currentFrameGray
                previousFrameHSV = currentFrameHSV
                previousFrameBlurred = currentFrameBlurred

                currentFrame = self.enchance_image(np.asarray(background_screenshot(self.process, 1920, 1080)))
                currentFrameGray = cv.cvtColor(currentFrame, cv.COLOR_RGBA2GRAY)
                currentFrameHSV = cv.cvtColor(currentFrame, cv.COLOR_BGR2HSV)
                currentFrameBlurred = cv.GaussianBlur(currentFrameGray, (3, 3), 0)

                frameDiff = cv.absdiff(src1=previousFrameBlurred, src2=currentFrameBlurred)



            # Loop continues its thing
            # Based on type of class
            if 'Stereo' in enabledFeatures:

                ## Image Processing Stereo
                stereo = cv.StereoBM_create(numDisparities = 128,
                                            blockSize = 5)

                # Calculate Disparity
                previewImage.add_layer('stereo', stereo.compute(previousFrameGray, currentFrameGray))

            if 'Superimpose' in enabledFeatures:

                # Declare Grid
                superimpose = GridImage(currentFrame, 10)

            if 'Motion Detection' in enabledFeatures:
                # Motion Detection Section ##################################

                # Dilute the image a bit to make differences more seeable; more suitable for contour detection
                kernel = np.ones((11, 11))
                frameDiffDilated = cv.dilate(frameDiff, kernel, 1)

                # Only take different areas that are different enough (>20 / 255)
                threshImage = cv.threshold(src=frameDiffDilated, thresh=30, maxval=255, type=cv.THRESH_BINARY)[1]

                # Draw Countours from Motion Detection to Edges Image
                contours, _ = cv.findContours(image=threshImage, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE)
                drawnContours = cv.drawContours(image=threshImage, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)

                # Apply Drawn Blobs/Contour
                previewImage.add_layer('motion_detected', drawnContours)

                if 'Motion Detection Objects' in enabledFeatures:
                    squareLayer = np.empty( (1080,1920) )
                    for c in contours:
                        # get the bounding rect
                        x, y, w, h = cv.boundingRect(c)
                        # draw a white rectangle to visualize the bounding rect
                        cv.rectangle(squareLayer, (x, y), (x + w, y + h), 255, 1)

                    previewImage.add_layer('motion_detected_squares', squareLayer)
                # End Motion Detection ##############################################

            if 'Sobel Edge' in enabledFeatures:
                # Sobel Edge Start

                # Sobel Edge Detection

                edgesx = cv.Sobel(currentFrameBlurred, -1, dx=1, dy=0, ksize=1)
                edgesy = cv.Sobel(currentFrameBlurred, -1, dx=0, dy=1, ksize=1)
                edges = edgesx + edgesy

                # Tresh Edges
                treshedEdges = cv.threshold(src=edges, thresh=150, maxval=255, type=cv.THRESH_BINARY)[1]
                kernel = np.ones((21, 21))
                treshedEdgesDilated = cv.dilate(treshedEdges, kernel, 1)

                # Get Countours of Edges
                contours, _ = cv.findContours(treshedEdgesDilated, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

                # Calculate SFM

                # Declare Feature Layer Utilities
                sfmGradient = np.empty( (1080,1920) )

                # Promisify and process contourDetection
                #loop = asyncio.new_event_loop()
                #loop.run_until_complete(self.main(edges))
                #loop.close()

                featuresTrackedInt0 = self.findTrackedObjects(currentFrameGray)
                previousFeaturesTrackedInt0 = self.findTrackedObjects(previousFrameGray)

                # TODO
                # Figure out why this randomly gets returned as none
                while featuresTrackedInt0 is None:
                    featuresTrackedInt0 = self.findTrackedObjects(currentFrameGray)

                # Transform
                featuresTrackedInt0 = np.int0(featuresTrackedInt0)
                previousFeaturesTrackedInt0 = np.int0(previousFeaturesTrackedInt0)

                for feature in featuresTrackedInt0:
                    x, y = feature.ravel()
                    cv.circle(sfmGradient, (x, y), 50, (255, 0, 255), -1)

                for feature in previousFeaturesTrackedInt0:
                    x, y = feature.ravel()
                    cv.circle(sfmGradient, (x, y), 50, (255, 255, 0), -1)

                previewImage.add_layer('sfm_matrix', sfmGradient)

                # End Calculate SFM

                # Iterate Contours
                extractedContour = np.empty( (1080,1920) )
                for contour in contours:
                        # get the bounding rect
                        x, y, w, h = cv.boundingRect(contour)

                        # Get Image From BB
                        extractedContour[y: y + h, x: x + w] = edges[y: y + h, x: x + w]

                        # draw a white rectangle to visualize the bounding rect
                        cv.rectangle(extractedContour, (x, y), (x + w, y + h), 255, 1)

                # Apply Contours & Edges
                previewImage.add_layer('edges_contours', extractedContour)
                previewImage.add_layer('edges', edges)

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

            if 'Structure from Motion' in enabledFeatures:
                # Structure from Motion Start

                # OPTS
                # Defining the dimensions of checkerboard
                CHECKERBOARD = (6, 9)

                criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

                # Creating vector to store vectors of 3D points for each checkerboard image
                objpoints = []

                # Creating vector to store vectors of 2D points for each checkerboard image
                imgpoints = []

                # Defining the world coordinates for 3D points
                objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
                objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

                #TODO: Replace K with given Intrinsic Matrix
                K = np.array([[518.86, 0., 285.58],
                            [0., 519.47, 213.74],
                            [0.,   0.,   1.]])

                # Structure from Motion Detection
                frames = [previousFrameGray, currentFrameGray]
                for gray in frames:

                    # Find the chess board corners
                    # If desired number of corners are found in the image then ret = true
                    ret, corners = cv.findChessboardCorners(gray, CHECKERBOARD, cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE)

                    """
                    If desired number of corner are detected,
                    we refine the pixel coordinates and display
                    them on the images of checker board
                    """
                    if ret == True:
                        objpoints.append(objp)
                        # refining pixel coordinates for given 2d points.
                        corners2 = cv.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)

                        imgpoints.append(corners2)

                        # Draw and display the corners
                        img = cv.drawChessboardCorners(gray, CHECKERBOARD, corners2, ret)

                # Apply
                previewImage.add_layer('points', imgpoints)

                # Structure from Motion End

            if 'Biped' in enabledFeatures:
                pass

            # Display
            if self.previewWidget.isVisible():

                # Reduce Layers into one
                toBeShown = np.empty( (1080,1920) )

                # Test Grid
                # view = superimpose.as_view()

                # Transform Layers as View
                dictImage = dict(previewImage)
                for key, value in dictImage.items():
                    try:
                        toBeShown = toBeShown + value
                    except Exception as err:
                        msg = key + ' error:'
                        print(msg)
                        print(err)

                # Show layers
                self.axe.clear()
                self.axe.imshow(toBeShown, alpha=1)
                self.figure.draw_idle()

            # End Stop Watch
            endTime = datetime.datetime.now()
            stopWatchDiff = (endTime - beginTime)

            # MS Conversion
            diff_in_milliseconds = stopWatchDiff.total_seconds() * 1000

            # Round to Nearest Nearest Whole Millisceond
            diff_in_milliseconds = round(diff_in_milliseconds)

            # Print
            diffInMilliseconds = str(diff_in_milliseconds) + " ms"
            print(diffInMilliseconds)


## Overlay Application
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
