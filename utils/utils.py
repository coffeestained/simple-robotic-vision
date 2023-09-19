import random
import math
import pyautogui
import pytweening
import numpy as np
import random
import time

from pyHM import mouse

'''
    Human Movement Utils Below
'''
def move_mouse(
    target,
    kwargs = {
       "offsetBoundaryX":  random.randint(75, 125),
       "offsetBoundaryY":  random.randint(75, 125),
       "knotsCount":  random.randint(0, 1),
       "distortionMean":  (random.randint(900, 1100) / 1000),
       "distortionStdev":  (random.randint(900, 1100) / 1000),
       "distortionFrequency": (random.randint(900, 1100) / 2000),
       "targetPoints":  random.randint(70, 130),
       "tween": pytweening.easeOutQuad
    },
    speed_random = (random.randint(25000, 38000) / 100000),
    threshold = 60
):
    """
    Human like mouse movement start -- TODO Train Model and refactor.
    """
    extra_randomization_trigger = random.randint(random.randint(0, 100), 100) > threshold
    print(extra_randomization_trigger, random.randint(random.randint(0, 100), 100))

    if extra_randomization_trigger == False:
        wrong_target = (target[0] + (random.randint(-27, 27)), target[1] + (random.randint(-27, 27)))
        hc.move(wrong_target, speed_random, HumanCurve(pyautogui.position(), wrong_target, **kwargs)) # Wrong Move
        time.sleep(random.randint(100, 700) / 1000)
        move_mouse(
            target,
            {
                "offsetBoundaryX":  random.randint(75, 125),
                "offsetBoundaryY":  random.randint(75, 125),
                "knotsCount":  random.randint(0, 1),
                "distortionMean":  (random.randint(900, 1100) / 1000),
                "distortionStdev":  (random.randint(900, 1100) / 1000),
                "distortionFrequency": (random.randint(900, 1100) / 2000),
                "targetPoints":  random.randint(70, 130),
                "tween": pytweening.easeOutQuad
            },
            (random.randint(4000, 11000) / 100000),
            threshold - 10
        ) # Try again
    else:
        hc.move(target, speed_random, HumanCurve(pyautogui.position(), target, **kwargs))

"""
Type Utils
"""
def isNumeric(val):
    return isinstance(val, (float, int, np.int32, np.int64, np.float32, np.float64))

def isListOfPoints(l):
    if not isinstance(l, list):
        return False
    try:
        isPoint = lambda p: ((len(p) == 2) and isNumeric(p[0]) and isNumeric(p[1]))
        return all(map(isPoint, l))
    except (KeyError, TypeError) as e:
        return False

class BezierCurve():
    @staticmethod
    def binomial(n, k):
        """Returns the binomial coefficient "n choose k" """
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))

    @staticmethod
    def bernsteinPolynomialPoint(x, i, n):
        """Calculate the i-th component of a bernstein polynomial of degree n"""
        return BezierCurve.binomial(n, i) * (x ** i) * ((1 - x) ** (n - i))

    @staticmethod
    def bernsteinPolynomial(points):
        """
        Given list of control points, returns a function, which given a point [0,1] returns
        a point in the bezier curve described by these points
        """
        def bern(t):
            n = len(points) - 1
            x = y = 0
            for i, point in enumerate(points):
                bern = BezierCurve.bernsteinPolynomialPoint(t, i, n)
                x += point[0] * bern
                y += point[1] * bern
            return x, y
        return bern

    @staticmethod
    def curvePoints(n, points):
        """
        Given list of control points, returns n points in the bezier curve,
        described by these points
        """
        curvePoints = []
        bernstein_polynomial = BezierCurve.bernsteinPolynomial(points)
        for i in range(n):
            t = i / (n - 1)
            curvePoints += bernstein_polynomial(t),
        return curvePoints



def setup_pyautogui():
    # Any duration less than this is rounded to 0.0 to instantly move the mouse.
    pyautogui.MINIMUM_DURATION = 0  # Default: 0.1
    # Minimal number of seconds to sleep between mouse moves.
    pyautogui.MINIMUM_SLEEP = 0  # Default: 0.05
    # The number of seconds to pause after EVERY public function call.
    pyautogui.PAUSE = 0.015  # Default: 0.1

setup_pyautogui()

class HumanClicker():
    def __init__(self):
        pass

    def move(self, toPoint, duration=2, humanCurve=None):
        fromPoint = pyautogui.position()
        if not humanCurve:
            humanCurve = HumanCurve(fromPoint, toPoint)

        pyautogui.PAUSE = duration / len(humanCurve.points)
        for point in humanCurve.points:
            pyautogui.moveTo(point)

    def click(self):
        pyautogui.click()



class HumanCurve():
    """
    Generates a human-like mouse curve starting at given source point,
    and finishing in a given destination point
    """

    def __init__(self, fromPoint, toPoint, **kwargs):
        self.fromPoint = fromPoint
        self.toPoint = toPoint
        self.points = self.generateCurve(**kwargs)

    def generateCurve(self, **kwargs):
        """
        Generates a curve according to the parameters specified below.
        You can override any of the below parameters. If no parameter is
        passed, the default value is used.
        """
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        leftBoundary = kwargs.get("leftBoundary", min(self.fromPoint[0], self.toPoint[0])) - offsetBoundaryX
        rightBoundary = kwargs.get("rightBoundary", max(self.fromPoint[0], self.toPoint[0])) + offsetBoundaryX
        downBoundary = kwargs.get("downBoundary", min(self.fromPoint[1], self.toPoint[1])) - offsetBoundaryY
        upBoundary = kwargs.get("upBoundary", max(self.fromPoint[1], self.toPoint[1])) + offsetBoundaryY
        knotsCount = kwargs.get("knotsCount", 2)
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        targetPoints = kwargs.get("targetPoints", 100)

        internalKnots = self.generateInternalKnots(leftBoundary,rightBoundary, \
            downBoundary, upBoundary, knotsCount)
        points = self.generatePoints(internalKnots)
        points = self.distortPoints(points, distortionMean, distortionStdev, distortionFrequency)
        points = self.tweenPoints(points, tween, targetPoints)
        return points

    def generateInternalKnots(self, \
        leftBoundary, rightBoundary, \
        downBoundary, upBoundary,\
        knotsCount):
        """
        Generates the internal knots used during generation of bezier curvePoints
        or any interpolation function. The points are taken at random from
        a surface delimited by given boundaries.
        Exactly knotsCount internal knots are randomly generated.
        """
        if not (isNumeric(leftBoundary) and isNumeric(rightBoundary) and
            isNumeric(downBoundary) and isNumeric(upBoundary)):
            raise ValueError("Boundaries must be numeric")
        if not isinstance(knotsCount, int) or knotsCount < 0:
            raise ValueError("knotsCount must be non-negative integer")
        if leftBoundary > rightBoundary:
            raise ValueError("leftBoundary must be less than or equal to rightBoundary")
        if downBoundary > upBoundary:
            raise ValueError("downBoundary must be less than or equal to upBoundary")

        knotsX = np.random.choice(range(leftBoundary, rightBoundary), size=knotsCount)
        knotsY = np.random.choice(range(downBoundary, upBoundary), size=knotsCount)
        knots = list(zip(knotsX, knotsY))
        return knots

    def generatePoints(self, knots):
        """
        Generates bezier curve points on a curve, according to the internal
        knots passed as parameter.
        """
        if not isListOfPoints(knots):
            raise ValueError("knots must be valid list of points")

        midPtsCnt = max( \
            abs(self.fromPoint[0] - self.toPoint[0]), \
            abs(self.fromPoint[1] - self.toPoint[1]), \
            2)
        knots = [self.fromPoint] + knots + [self.toPoint]
        return BezierCurve.curvePoints(midPtsCnt, knots)

    def distortPoints(self, points, distortionMean, distortionStdev, distortionFrequency):
        """
        Distorts the curve described by (x,y) points, so that the curve is
        not ideally smooth.
        Distortion happens by randomly, according to normal distribution,
        adding an offset to some of the points.
        """
        if not(isNumeric(distortionMean) and isNumeric(distortionStdev) and \
               isNumeric(distortionFrequency)):
            raise ValueError("Distortions must be numeric")
        if not isListOfPoints(points):
            raise ValueError("points must be valid list of points")
        if not (0 <= distortionFrequency <= 1):
            raise ValueError("distortionFrequency must be in range [0,1]")

        distorted = []
        for i in range(1, len(points)-1):
            x,y = points[i]
            delta = np.random.normal(distortionMean, distortionStdev) if \
                random.random() < distortionFrequency else 0
            distorted += (x,y+delta),
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    def tweenPoints(self, points, tween, targetPoints):
        """
        Chooses a number of points(targetPoints) from the list(points)
        according to tweening function(tween).
        This function in fact controls the velocity of mouse movement
        """
        if not isListOfPoints(points):
            raise ValueError("points must be valid list of points")
        if not isinstance(targetPoints, int) or targetPoints < 2:
            raise ValueError("targetPoints must be an integer greater or equal to 2")

        # tween is a function that takes a float 0..1 and returns a float 0..1
        res = []
        for i in range(targetPoints):
            index = int(tween(float(i)/(targetPoints-1)) * (len(points)-1))
            res += points[index],
        return res


hc = HumanClicker()

# PYCLICK LICENSE INFO
# Copyright (c) 2018 The Python Packaging Authority

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
