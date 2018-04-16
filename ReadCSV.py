import snap
from datetime import datetime

from matplotlib.axes._base import _AxesBase
import csv
import math
import GlobalParameters
from PyQt4 import QtCore, QtGui
import Utility
import time


class ReadCSV(QtCore.QThread):
    def __init__(self, filepath, tSpan, box, GraphicScene = None):
        QtCore.QThread.__init__(self)
        self.filepath = filepath
        self.title = []
        self.bbox = box
        self.scene = GraphicScene
        self.tSpan = tSpan
        self.items = []
        self.DoNNR = True
        self.GEOTitle = "GEO"
        self.TIMETitle = "CREATED_AT"

    def ReadCSV(self):

        items = []
        with open(self.filepath, "r") as fp:
            reader = csv.reader(fp, dialect=csv.excel)
            for rows in reader:
                items.append(rows)


        if len(items) > 0:
            self.title = list(items.pop(0))
        self.items = items
        return self.items
        #
        #
        # wb = open_workbook(self.filepath)
        #
        # sheet = wb.sheet_by_index(0)
        # numberOfRows = sheet.nrows
        # numberOfColumns = sheet.ncols
        # items = [None] * numberOfRows
        #
        # for row in range(numberOfRows):
        #     values = [None] * numberOfColumns
        #     for col in range(numberOfColumns):
        #         values[col] = sheet.cell(row, col).value
        #     items[row] = values
        # if len(items) > 0:
        #     self.title = list(items.pop(0))
        # self.items = items
        # return self.items


    def run(self):
        timeSpan = self.tSpan
        items = self.ReadCSV()

        min = 0
        max = 0

        colTimeIndex = self.title.index("CREATED_AT_LOCAL")
        beginTime = datetime.strptime(items[min][colTimeIndex], '%Y-%m-%d %H:%M:%S')

        ODMatrix = []
        nearestDict = {}
        TimeList = []
        TimeNearest = {}
        TimeNNR = []
        for i in range(0, len(items)):
            nearestDict[i] = [-1, -1]
        GlobalParameters.RegressionArea = self.DistributeArea(40.0)  # circle's radius is 40 miles

        Old_NNR = 0
        colPositionIndex = self.title.index("GEO")
        left, top, right, bottom, ratio = Utility.GetLTRB(self.bbox, self.scene)
        RList = []
        pen = QtGui.QPen(QtGui.QColor(GlobalParameters.NodeColor))
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.NodeBrushColor))
        while (min < len(items)):
            # deal with period that has no tweets$
            if timeSpan > 0:
                while self.DeltaTime(datetime.strptime(items[min][colTimeIndex], '%Y-%m-%d %H:%M:%S'),
                                     beginTime) >= (len(RList) + 1) * timeSpan:
                    RList.append(RList[len(RList) - 1])
                    self.emit(QtCore.SIGNAL("Regression(QString)"), str(Old_NNR))
                for i in range(min, len(items)):
                    t = datetime.strptime(items[i][colTimeIndex], '%Y-%m-%d %H:%M:%S')
                    TimeList.append(t)
                    deltaT = (len(RList) + 1) * timeSpan
                    if self.DeltaTime(t, beginTime) < deltaT:
                        max = i
                        pointY, pointX = items[i][colPositionIndex].split(",")
                        X, Y = Utility.ConvertPostion2(float(pointX), float(pointY), ratio, left, bottom,
                                                       self.bbox[0], self.bbox[1])
                        point = QtGui.QGraphicsEllipseItem(X, Y, GlobalParameters.NodeSize,
                                                           GlobalParameters.NodeSize)
                        point.setBrush(brush)
                        point.setPen(pen)
                        self.emit(QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"), point, "P",
                                  str(i))
                        time.sleep(0.01)
                    else:
                        break
            else:
                t = datetime.strptime(items[min][colTimeIndex], '%Y-%m-%d %H:%M:%S')
                TimeList.append(t)
                pointY, pointX = items[min][colPositionIndex].split(",")
                X, Y = Utility.ConvertPostion2(float(pointX), float(pointY), ratio, left, bottom, self.bbox[0],
                                               self.bbox[1])
                point = QtGui.QGraphicsEllipseItem(X, Y, GlobalParameters.NodeSize, GlobalParameters.NodeSize)
                point.setBrush(brush)
                point.setPen(pen)
                self.emit(QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"), point, "P", str(min))
                time.sleep(0.01)
            self.ConstructODMatrix(items, ODMatrix, nearestDict, min, max + 1)
            NNR = self.NearestNeighborRatio(ODMatrix, nearestDict, GlobalParameters.RegressionArea)
            RList.append(NNR)
            self.emit(QtCore.SIGNAL("Regression(QString)"), str(NNR))
            min = max + 1
            max = min
            Old_NNR = NNR

        # return RList, ODMatrix, nearestDict
        GlobalParameters.RegressiontotalT = len(RList)

        tListLen = len(TimeList)
        if tListLen > 2:
            deltaT = self.DeltaTime(TimeList[1], TimeList[0])
            TimeNearest[0] = deltaT
            TimeNearest[1] = deltaT

        for i in range(2, tListLen):
            TimeNearest[i] = self.DeltaTime(TimeList[i], TimeList[i - 1])
            if TimeNearest[i - 1] > TimeNearest[i]:
                TimeNearest[i - 1] = TimeNearest[i]
        totalTimeDistance = TimeNearest[0]
        for i in range(1, tListLen):
            totalTimeDistance += TimeNearest[i]
            TimeNNR.append(2 * totalTimeDistance / math.sqrt(
                (i + 1) * (self.DeltaTime(TimeList[i], TimeList[0])) * (self.DeltaTime(TimeList[i], TimeList[0]))))

        print TimeNNR

        self.emit(QtCore.SIGNAL("DrawTimeRegPlot(PyQt_PyObject)"), TimeNNR)

        print "Here is OK"
        self.emit(QtCore.SIGNAL("FinshedRun(QString)"), "Diffusion is finished!")

    def DeltaTime(self, a, b):
        delta = a - b
        return delta.days * 3600 * 24 + delta.seconds

    def ConstructODMatrix(self, items, ODMatrix, nearestDict, min, max):
        longColIndex = self.title.index("Long")
        latColIndex = self.title.index("Lat")

        oldLen = len(ODMatrix)
        for i in range(min, max):
            ODMatrix.append([])

        for i in range(oldLen):
            for j in range(min, max):
                distance = self.DistanceItem(items, i, j, longColIndex, latColIndex)
                ODMatrix[i].append(distance)
                ODMatrix[j].append(distance)
                if nearestDict[i][0] == -1 or distance < nearestDict[i][0]:
                    nearestDict[i] = [distance, j]
                if nearestDict[j][0] == -1 or distance < nearestDict[j][0]:
                    nearestDict[j] = [distance, i]
        # print min, max
        ODMatrix[min].append(0.0)
        if min + 1 != max:
            for i in range(min, max - 1):
                for j in range(min + 1, max):
                    if i > j:
                        continue
                    distance = self.DistanceItem(items, i, j, longColIndex, latColIndex)
                    ODMatrix[i].append(distance)
                    if i != j:
                        ODMatrix[j].append(distance)
                        # if i == j, it is not it's neighborhood
                        if nearestDict[i][0] == -1 or distance < nearestDict[i][0]:
                            nearestDict[i] = [distance, j]
                        if nearestDict[j][0] == -1 or distance < nearestDict[j][0]:
                            nearestDict[j] = [distance, i]
            ODMatrix[max - 1].append(0.0)

        return ODMatrix, nearestDict

    def DistanceItem(self, items, i, j, longColIndex, latColIndex):  # return mile
        # items don't contain title row
        return self.DistancePoints(float(items[i][latColIndex]), float(items[j][latColIndex]), float(items[i][longColIndex]),
                                   float(items[j][longColIndex]))

    def DistancePoints(self, lat_1, lat_2, long_1, long_2):
        lat1 = self.Rad(lat_1)
        lat2 = self.Rad(lat_2)
        long1 = self.Rad(long_1)
        long2 = self.Rad(long_2)
        a = lat1 - lat2
        b = long1 - long2
        s = 2 * math.asin(
            math.sqrt(
                math.pow(math.sin(a / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(b / 2), 2)))
        s *= GlobalParameters.EarthRadius * 1000  # unit:m
        s = math.floor(s * 10000) / 10000
        return s

    def Rad(self, d):
        print "D:", d
        return d * math.pi / 180.0

    def NearestNeighborRatio(self, ODMatrix, nearestDict, area):
        # print "NNR:",self.AverageNearestDistance(ODMatrix, nearestDict), math.sqrt(area/len(ODMatrix)), len(ODMatrix)
        return 2 * self.AverageNearestDistance(ODMatrix, nearestDict) / math.sqrt(area / len(ODMatrix))

    def AverageNearestDistance(self, ODMatrix, nearestDict):
        leng = len(ODMatrix)
        if leng <= 0:
            return 0
        if leng < 2:
            return 0
        sum = 0.0
        for i in range(leng):
            sum += nearestDict[i][0]
        return sum / leng

    def DistributeArea(self, radius):
        return math.pi * math.pow(radius * GlobalParameters.MileToKilo * 1000, 2)

    # def run(self):
    #     timeSpan = self.tSpan
    #     items = self.ReadCSV()
    #
    #     min = 0
    #     max = 0
    #
    #     colTimeIndex = self.title.index(self.TIMETitle)
    #     print str(items[min][colTimeIndex])
    #
    #     beginTime = datetime.strptime(items[min][colTimeIndex].replace(".000Z", "").replace("T"," "), '%Y-%m-%d %H:%M:%S')
    #
    #     ODMatrix = []
    #     nearestDict = {}
    #     TimeList = []
    #     TimeNearest = {}
    #     TimeNNR = []
    #     for i in range(0, len(items)):
    #         nearestDict[i] = [-1, -1]
    #     GlobalParameters.RegressionArea = self.DistributeArea(40.0) # circle's radius is 40 miles
    #
    #     Old_NNR = 0
    #     colPositionIndex = self.title.index(self.GEOTitle)
    #
    #     left, top, right, bottom, ratio = Utility.GetLTRB(self.bbox, self.scene)
    #     RList = []
    #     pen = QtGui.QPen(QtGui.QColor(GlobalParameters.NodeColor))
    #     brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.NodeBrushColor))
    #     while (min < len(items)):
    #         # deal with period that has no tweets$
    #         if timeSpan > 0:
    #             while self.DeltaTime(datetime.strptime(items[min][colTimeIndex].replace(".000Z", "").replace("T"," "), '%Y-%m-%d %H:%M:%S'), beginTime) >= (len(RList) + 1) * timeSpan:
    #                 if self.DoNNR:
    #                     RList.append(RList[len(RList) - 1])
    #                     self.emit(QtCore.SIGNAL("Regression(QString)"), str(Old_NNR))
    #             for i in range(min, len(items)):
    #                 t = datetime.strptime(items[i][colTimeIndex].replace(".000Z", "").replace("T"," "), '%Y-%m-%d %H:%M:%S')
    #                 TimeList.append(t)
    #                 deltaT = (len(RList) + 1) * timeSpan
    #                 if self.DeltaTime(t, beginTime) < deltaT:
    #                     max = i
    #                     pointX, pointY = items[i][colPositionIndex].split(",")
    #                     pointX = pointX.lstrip("[")
    #                     pointY = pointY.rstrip("]")
    #                     X, Y = Utility.ConvertPostion2(float(pointX), float(pointY), ratio, left, bottom, self.bbox[0], self.bbox[1])
    #                     print "pointX, pointY:",pointX, pointY
    #                     print "X, Y:", X, Y
    #                     point = QtGui.QGraphicsEllipseItem(X, Y, GlobalParameters.NodeSize, GlobalParameters.NodeSize)
    #                     point.setBrush(brush)
    #                     point.setPen(pen)
    #                     self.emit(QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"), point, "P", str(i))
    #                     time.sleep(0.01)
    #                 else:
    #                     break
    #         else:
    #             t = datetime.strptime(items[min][colTimeIndex].replace(".000Z", "").replace("T"," "), '%Y-%m-%d %H:%M:%S')
    #             TimeList.append(t)
    #             pointX, pointY = items[min][colPositionIndex].split(",")
    #             pointX = pointX.lstrip("[")
    #             pointY = pointY.rstrip("]")
    #             X, Y = Utility.ConvertPostion2(float(pointX), float(pointY), ratio, left, bottom, self.bbox[0], self.bbox[1])
    #             point = QtGui.QGraphicsEllipseItem(X, Y, GlobalParameters.NodeSize, GlobalParameters.NodeSize)
    #             point.setBrush(brush)
    #             point.setPen(pen)
    #             print pointX, pointY
    #             self.emit(QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"), point, "P", str(min))
    #             time.sleep(0.1)
    #         if self.DoNNR:
    #             self.ConstructODMatrix(items, ODMatrix, nearestDict, min, max + 1)
    #             NNR = self.NearestNeighborRatio(ODMatrix, nearestDict, GlobalParameters.RegressionArea)
    #             RList.append(NNR)
    #             self.emit(QtCore.SIGNAL("Regression(QString)"), str(NNR))
    #             Old_NNR = NNR
    #         min = max + 1
    #         max = min
    #
    #
    #     #return RList, ODMatrix, nearestDict
    #
    #     if self.DoNNR:
    #         GlobalParameters.RegressiontotalT = len(RList)
    #
    #         tListLen = len(TimeList)
    #         if tListLen > 2:
    #             deltaT = self.DeltaTime(TimeList[1], TimeList[0])
    #             TimeNearest[0] = deltaT
    #             TimeNearest[1] = deltaT
    #
    #         for i in range(2, tListLen):
    #             TimeNearest[i] = self.DeltaTime(TimeList[i], TimeList[i - 1])
    #             if TimeNearest[i -1] > TimeNearest[i]:
    #                 TimeNearest[i -1] = TimeNearest[i]
    #         totalTimeDistance = TimeNearest[0]
    #         for i in range(1, tListLen):
    #             totalTimeDistance += TimeNearest[i]
    #             TimeNNR.append(2 * totalTimeDistance/math.sqrt((i + 1)*(self.DeltaTime(TimeList[i], TimeList[0])) *(self.DeltaTime(TimeList[i], TimeList[0])) ))
    #
    #         print TimeNNR
    #
    #         self.emit(QtCore.SIGNAL("DrawTimeRegPlot(PyQt_PyObject)"),TimeNNR)
    #
    #     print "Here is OK"
    #     self.emit(QtCore.SIGNAL("FinshedRun(QString)"), "Diffusion is finished!")
    # def DeltaTime(self, a, b):
    #     delta = a - b
    #     return delta.days * 3600 * 24 + delta.seconds
    #
    # def ConstructODMatrix(self, items, ODMatrix, nearestDict, min, max):
    #     colPositionIndex = self.title.index(self.GEOTitle)
    #
    #     oldLen = len(ODMatrix)
    #     for i in range(min, max):
    #         ODMatrix.append([])
    #
    #     for i in range(oldLen):
    #         for j in range(min, max):
    #             distance = self.DistanceItem(items, i, j, colPositionIndex)
    #             ODMatrix[i].append(distance)
    #             ODMatrix[j].append(distance)
    #             if nearestDict[i][0] == -1 or distance < nearestDict[i][0]:
    #                 nearestDict[i] = [distance, j]
    #             if nearestDict[j][0] == -1 or distance < nearestDict[j][0]:
    #                 nearestDict[j] = [distance, i]
    #     #print min, max
    #     ODMatrix[min].append(0.0)
    #     if min + 1 != max:
    #         for i in range(min, max - 1):
    #             for j in range(min + 1, max):
    #                 if i > j:
    #                     continue
    #                 distance = self.DistanceItem(items, i, j, colPositionIndex)
    #                 ODMatrix[i].append(distance)
    #                 if i != j:
    #                     ODMatrix[j].append(distance)
    #                     # if i == j, it is not it's neighborhood
    #                     if nearestDict[i][0] == -1 or distance < nearestDict[i][0]:
    #                         nearestDict[i] = [distance, j]
    #                     if nearestDict[j][0] == -1 or distance < nearestDict[j][0]:
    #                         nearestDict[j] = [distance, i]
    #         ODMatrix[max - 1].append(0.0)
    #
    #     return ODMatrix, nearestDict
    #
    # def DistanceItem(self, items, i, j, colPositionIndex):  # return mile
    #     # items don't contain title row
    #
    #     return self.DistancePoints(items[i][colPositionIndex].split(",")[1].rstrip("]"), items[j][colPositionIndex].split(",")[0].lstrip("["), items[i][colPositionIndex].split(",")[1].rstrip("]"),
    #                                items[j][colPositionIndex].split(",")[0].lstrip("["))
    #
    # def DistancePoints(self, lat_1, lat_2, long_1, long_2):
    #     lat1 = self.Rad(lat_1)
    #     lat2 = self.Rad(lat_2)
    #     long1 = self.Rad(long_1)
    #     long2 = self.Rad(long_2)
    #     a = lat1 - lat2
    #     b = long1 - long2
    #     s = 2 * math.asin(
    #         math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(b / 2), 2)))
    #     s *= GlobalParameters.EarthRadius * 1000  # unit:m
    #     s = math.floor(s * 10000) / 10000
    #     return s
    #
    # def Rad(self, d):
    #     # print "d:", d
    #     return float(d) * math.pi / 180.0
    #
    # def NearestNeighborRatio(self, ODMatrix, nearestDict, area):
    #     #print "NNR:",self.AverageNearestDistance(ODMatrix, nearestDict), math.sqrt(area/len(ODMatrix)), len(ODMatrix)
    #     return 2 * self.AverageNearestDistance(ODMatrix, nearestDict) / math.sqrt(area/len(ODMatrix))
    #
    # def AverageNearestDistance(self, ODMatrix, nearestDict):
    #     leng = len(ODMatrix)
    #     if leng <= 0:
    #         return 0
    #     if leng < 2:
    #         return 0
    #     sum = 0.0
    #     for i in range(leng):
    #         sum += nearestDict[i][0]
    #     return sum / leng
    #
    # def DistributeArea(self, radius):
    #     return math.pi * math.pow(radius * GlobalParameters.MileToKilo * 1000, 2)
    #
    #
    #

if __name__ == "__main__":
    network = ReadCSV("C:\\SocialNetworkSimulator\\Twettesvaccine_SB277_05252015_05312016_GPS_XY.xlsx")

    Rlist1, ODMatrix1, neigh1 = network.NearestNeighborRatioList(0)


    for i in range(len(ODMatrix1)):
        min = 80*1.7*10000
        index = -1
        for j in range(len(ODMatrix1[i])):
            if i != j and ODMatrix1[i][j] < min:
                min = ODMatrix1[i][j]
                index = j
        if min != neigh1[i][0]:
            print "ERROR", i, min, j, neigh1[i]

    for i in range(len(Rlist1)):
        print Rlist1[i] ,",", i
