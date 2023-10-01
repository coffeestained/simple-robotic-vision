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
def mouse_move(
    target,
    kwargs = {
       "offset_boundary_x":  random.randint(75, 125),
       "offset_boundary_y":  random.randint(75, 125),
       "knots_count":  random.randint(0, 1),
       "distortion_mean":  (random.randint(900, 1100) / 1000),
       "distortion_stdev":  (random.randint(900, 1100) / 1000),
       "distortion_frequency": (random.randint(900, 1100) / 2000),
       "targetPoints":  random.randint(70, 130),
       "tween": pytweening.easeOutQuad
    },
    speed_random = (random.randint(25000, 38000) / 100000),
    threshold = 60
):
    """
    Human like mouse movement start -- TODO Train model and refactor.
    """
    extra_randomization_trigger = random.randint(random.randint(0, 100), 100) > threshold

    if extra_randomization_trigger == False:
        x_delta = (random.randint(-27, 27))
        y_delta = (random.randint(-27, 27))
        # TODO Scale distance deltas to speeds for consistency
        wrong_target = (target[0] + x_delta, target[1] + y_delta)
        hc.move(wrong_target, (random.randint(69, 249) / 100000), HumanCurve(pyautogui.position(), wrong_target, **kwargs)) # Wrong Move
        time.sleep(random.randint(100, 700) / 1000)
        mouse_move(
            target,
            {
                "offset_boundary_x":  random.randint(75, 125),
                "offset_boundary_y":  random.randint(75, 125),
                "knots_count":  random.randint(0, 1),
                "distortion_mean":  (random.randint(900, 1100) / 1000),
                "distortion_stdev":  (random.randint(900, 1100) / 1000),
                "distortion_frequency": (random.randint(900, 1100) / 2000),
                "targetPoints":  random.randint(70, 130),
                "tween": pytweening.easeOutQuad
            },
            (random.randint(4000, 11000) / 100000),
            threshold - 10
        ) # Try again
    else:
        hc.move(target, speed_random, HumanCurve(pyautogui.position(), target, **kwargs))

'''
    Human Click Utils Below
'''
def mouse_click(
    target,
    button="left",
    kwargs = {
       "offset_boundary_x":  random.randint(2, 4),
       "offset_boundary_y":  random.randint(2, 6),
       "knots_count":  random.randint(0, 1),
       "distortion_mean":  (random.randint(900, 1100) / 10000),
       "distortion_stdev":  (random.randint(900, 1100) / 10000),
       "distortion_frequency": (random.randint(900, 1100) / 20000),
       "targetPoints":  random.randint(2, 11),
       "tween": pytweening.easeOutQuad
    }
):

    """
    Human like mouse movement start -- TODO Train model and refactor.
    """
    pyautogui.mouseDown(button=button)
    extra_randomization_trigger = random.randint(random.randint(0, 100), 100) > 60
    if extra_randomization_trigger:
        new_target = (target[0] + random.randint(-3, 3), target[1] + random.randint(-3, 3))
        hc.move(new_target, (random.randint(69, 249) / 100000), HumanCurve(pyautogui.position(), new_target, **kwargs))
        time.sleep((random.randint(249, 299) / 100000))
    hc.move(target, (random.randint(229, 379) / 100000), HumanCurve(pyautogui.position(), target, **kwargs))
    time.sleep((random.randint(29, 129) / 100000))
    pyautogui.mouseUp(button=button)


"""
Type Utils
"""
def is_numeric(val):
    return isinstance(val, (float, int, np.int32, np.int64, np.float32, np.float64))

def is_list_of_points(l):
    if not isinstance(l, list):
        return False
    try:
        isPoint = lambda p: ((len(p) == 2) and is_numeric(p[0]) and is_numeric(p[1]))
        return all(map(isPoint, l))
    except (KeyError, TypeError) as e:
        return False

class BezierCurve():
    @staticmethod
    def binomial(n, k):
        """Returns the binomial coefficient "n choose k" """
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))

    @staticmethod
    def bernstein_polynomial_point(x, i, n):
        """Calculate the i-th component of a bernstein polynomial of degree n"""
        return BezierCurve.binomial(n, i) * (x ** i) * ((1 - x) ** (n - i))

    @staticmethod
    def bernstein_polynomial(points):
        """
        Given list of control points, returns a function, which given a point [0,1] returns
        a point in the bezier curve described by these points
        """
        def bern(t):
            n = len(points) - 1
            x = y = 0
            for i, point in enumerate(points):
                bern = BezierCurve.bernstein_polynomial_point(t, i, n)
                x += point[0] * bern
                y += point[1] * bern
            return x, y
        return bern

    @staticmethod
    def curve_points(n, points):
        """
        Given list of control points, returns n points in the bezier curve,
        described by these points
        """
        curve_points = []
        bernstein_polynomial = BezierCurve.bernstein_polynomial(points)
        for i in range(n):
            t = i / (n - 1)
            curve_points += bernstein_polynomial(t),
        return curve_points



def setup_pyautogui():
    # Any duration less than this is rounded to 0.0 to instantly move the mouse.
    pyautogui.MINIMUM_DURATION = 0  # Default: 0.1
    # Minimal number of seconds to sleep between mouse moves.
    pyautogui.MINIMUM_SLEEP = 0  # Default: 0.05
    # The number of seconds to pause after EVERY public function call.
    pyautogui.PAUSE = 0.015  # Default: 0.1

setup_pyautogui()

class HumanMovement():
    def __init__(self):
        pass

    def move(self, to_point, duration=2, humanCurve=None):
        from_point = pyautogui.position()
        if not humanCurve:
            humanCurve = HumanCurve(from_point, to_point)

        pyautogui.PAUSE = duration / len(humanCurve.points)
        for point in humanCurve.points:
            pyautogui.moveTo(point)



class HumanCurve():
    """
    Generates a human-like mouse curve starting at given source point,
    and finishing in a given destination point
    """

    def __init__(self, from_point, to_point, **kwargs):
        self.from_point = from_point
        self.to_point = to_point
        self.points = self.generateCurve(**kwargs)

    def generateCurve(self, **kwargs):
        """
        Generates a curve according to the parameters specified below.
        You can override any of the below parameters. If no parameter is
        passed, the default value is used.
        """
        offset_boundary_x = kwargs.get("offset_boundary_x", 100)
        offset_boundary_y = kwargs.get("offset_boundary_y", 100)
        left_boundary = kwargs.get("left_boundary", min(self.from_point[0], self.to_point[0])) - offset_boundary_x
        right_boundary = kwargs.get("right_boundary", max(self.from_point[0], self.to_point[0])) + offset_boundary_x
        down_boundary = kwargs.get("down_boundary", min(self.from_point[1], self.to_point[1])) - offset_boundary_y
        up_boundary = kwargs.get("up_boundary", max(self.from_point[1], self.to_point[1])) + offset_boundary_y
        knots_count = kwargs.get("knots_count", 2)
        distortion_mean = kwargs.get("distortion_mean", 1)
        distortion_stdev = kwargs.get("distortion_stdev", 1)
        distortion_frequency = kwargs.get("distortion_frequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        targetPoints = kwargs.get("targetPoints", 100)

        internalKnots = self.generate_internal_knots(left_boundary,right_boundary, \
            down_boundary, up_boundary, knots_count)
        points = self.generate_points(internalKnots)
        points = self.distory_points(points, distortion_mean, distortion_stdev, distortion_frequency)
        points = self.tween_points(points, tween, targetPoints)
        return points

    def generate_internal_knots(self, \
        left_boundary, right_boundary, \
        down_boundary, up_boundary,\
        knots_count):
        """
        Generates the internal knots used during generation of bezier curve_points
        or any interpolation function. The points are taken at random from
        a surface delimited by given boundaries.
        Exactly knots_count internal knots are randomly generated.
        """
        if not (is_numeric(left_boundary) and is_numeric(right_boundary) and
            is_numeric(down_boundary) and is_numeric(up_boundary)):
            raise ValueError("Boundaries must be numeric")
        if not isinstance(knots_count, int) or knots_count < 0:
            raise ValueError("knots_count must be non-negative integer")
        if left_boundary > right_boundary:
            raise ValueError("left_boundary must be less than or equal to right_boundary")
        if down_boundary > up_boundary:
            raise ValueError("down_boundary must be less than or equal to up_boundary")

        knotsX = np.random.choice(range(left_boundary, right_boundary), size=knots_count)
        knotsY = np.random.choice(range(down_boundary, up_boundary), size=knots_count)
        knots = list(zip(knotsX, knotsY))
        return knots

    def generate_points(self, knots):
        """
        Generates bezier curve points on a curve, according to the internal
        knots passed as parameter.
        """
        if not is_list_of_points(knots):
            raise ValueError("knots must be valid list of points")

        midPtsCnt = max( \
            abs(self.from_point[0] - self.to_point[0]), \
            abs(self.from_point[1] - self.to_point[1]), \
            2)
        knots = [self.from_point] + knots + [self.to_point]
        return BezierCurve.curve_points(midPtsCnt, knots)

    def distory_points(self, points, distortion_mean, distortion_stdev, distortion_frequency):
        """
        Distorts the curve described by (x,y) points, so that the curve is
        not ideally smooth.
        Distortion happens by randomly, according to normal distribution,
        adding an offset to some of the points.
        """
        if not(is_numeric(distortion_mean) and is_numeric(distortion_stdev) and \
               is_numeric(distortion_frequency)):
            raise ValueError("Distortions must be numeric")
        if not is_list_of_points(points):
            raise ValueError("points must be valid list of points")
        if not (0 <= distortion_frequency <= 1):
            raise ValueError("distortion_frequency must be in range [0,1]")

        distorted = []
        for i in range(1, len(points)-1):
            x,y = points[i]
            delta = np.random.normal(distortion_mean, distortion_stdev) if \
                random.random() < distortion_frequency else 0
            distorted += (x,y+delta),
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    def tween_points(self, points, tween, targetPoints):
        """
        Chooses a number of points(targetPoints) from the list(points)
        according to tweening function(tween).
        This function in fact controls the velocity of mouse movement
        """
        if not is_list_of_points(points):
            raise ValueError("points must be valid list of points")
        if not isinstance(targetPoints, int) or targetPoints < 2:
            raise ValueError("targetPoints must be an integer greater or equal to 2")

        # tween is a function that takes a float 0..1 and returns a float 0..1
        res = []
        for i in range(targetPoints):
            index = int(tween(float(i)/(targetPoints-1)) * (len(points)-1))
            res += points[index],
        return res


hc = HumanMovement()

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
