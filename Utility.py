import math

__author__ = 'Lanxue Dang'

from PyQt4 import QtCore, QtGui
import re
import GlobalParameters
from math import fabs


def SystemWarning(message, title="Warning"):
    mbox = QtGui.QMessageBox()
    mbox.setWindowTitle(title)
    mbox.setText(message + "\t\t")
    mbox.exec_()


def SystemTipYesNO(message, title="Warning"):
    mbox = QtGui.QMessageBox()
    mbox.setText(message + "\t\t")
    mbox.setWindowTitle(title)
    mbox.addButton(QtGui.QMessageBox.Yes)
    mbox.addButton(QtGui.QMessageBox.No)
    mbox.setDefaultButton(QtGui.QMessageBox.No)
    if mbox.exec_() == QtGui.QMessageBox.Yes:
        return True
    else:
        return False


def InitCombobox(combobox, itemList):
    combobox.addItem("")
    for item in itemList:
        combobox.addItem(item)


def CheckParameter(paramName, paramvalue):
    result = None
    if str(paramName).upper() == "RND":
        return True
    try:
        type = str(paramName).split("(")[1].split(")")[0].upper()
        if type == "INT":
            result = re.search("^[1-9]{1}[0-9]*$", paramvalue)
        elif type == "FLOAT":
            result = re.search("(^0?[.]{1}[0-9]+$)|(^1([.]{1}[0]+){0,1}$)|(^0$)", paramvalue)
        elif type == "FLOAT2":
            result = re.search("^[0-9]+([.]{1}[0-9]+){0,1}$", paramvalue)
    except:
        pass
    if result is None:
        return False
    else:
        return True


def GetLTRB(bbox, GraphicsScene):
    minX, minY, maxX, maxY = bbox
    width = GraphicsScene.width() - GlobalParameters.CanvasMargin[0] - GlobalParameters.CanvasMargin[2]
    height = GraphicsScene.height() - GlobalParameters.CanvasMargin[1] - GlobalParameters.CanvasMargin[3]
    ratioX = width / (maxX - minX)
    ratioY = height / (maxY - minY)
    if ratioX >= ratioY:
        ratio = ratioY
    else:
        ratio = ratioX
    width1 = (maxX - minX) * ratio
    height1 = (maxY - minY) * ratio
    left = GlobalParameters.CanvasMargin[0] + (width - width1) / 2
    top = GlobalParameters.CanvasMargin[1] + (height - height1) / 2
    right = GraphicsScene.width() - GlobalParameters.CanvasMargin[2] - (width - width1) / 2
    bottom = GraphicsScene.height() - GlobalParameters.CanvasMargin[3] - (height - height1) / 2
    return left, top, right, bottom, ratio


def ConvertPostion(point, ratio, left, bottom, minX, minY):
    return (point.x - minX) * ratio + left, bottom - (point.y - minY) * ratio


def ConvertPostion2(x, y, ratio, left, bottom, minX, minY):
    return (x - minX) * ratio + left, bottom - (y - minY) * ratio

def PointInPolygon(x, y, points):
    n = len(points)
    isIn = False

    p1x = points[0][0]
    p1y = points[0][1]

    for i in range(0, n + 1, 1):
        p2x = points[(i % n)][0]
        p2y = points[(i % n)][1]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xx = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xx:
                        isIn = not isIn
        p1x, p1y = p2x, p2y

    return isIn

def DeltaTime(a, b):
        delta = a - b
        return delta.days * 3600 * 24 + delta.seconds

def ComputePolygonArea(points):
    pointNum = len(points)
    if pointNum < 3:
        return 0.0
    s = 0
    for i  in range(0, pointNum):
        s += points[i].x * points[(i+1)%pointNum].y - points[i].y * points[(i+1)%pointNum].x
    return fabs(s/2.0)


# unit mile
def DistancePoints(lat_1, lat_2, long_1, long_2):
    lat1 = Rad(lat_1)
    lat2 = Rad(lat_2)
    long1 = Rad(long_1)
    long2 = Rad(long_2)
    a = lat1 - lat2
    b = long1 - long2
    s = 2 * math.asin(
        math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(b / 2), 2)))
    s *= GlobalParameters.EarthRadius/ 0.621371 # unit:mile
    s = math.floor(s * 1000000) / 1000000
    return s


def Rad(d):
    # print "d:", d
    return float(d) * math.pi / 180.0
