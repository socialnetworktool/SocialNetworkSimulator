import math, ReadCSV
from PyQt4 import QtCore, QtGui
from datetime import datetime
import GlobalParameters
import Utility
import random

class SpatialPredict(QtCore.QThread):
    def __init__(self, path, box, spanx, spany, begin, GraphicScene = None):
        QtCore.QThread.__init__(self)
        self.filePath = path
        self.bbox = box
        self.params = GlobalParameters.RegressionCoefficients
        self.spanX = spanx
        self.spanY = spany
        self.b = begin
        self.scene = GraphicScene

    def Grid(self, bbox, span_x, span_y, items, long_index, lat_index):
        minX, minY, maxX, maxY = bbox
        rows = int(math.ceil((maxX - minX) / span_x))
        cols = int(math.ceil((maxY - minY) / span_y))
        self.fullGrid = {}
        self.fillGrid = {}

        print rows, cols
        for i in range(rows - 1):
            for j in range(cols - 1):
                self.fullGrid[str.format("{0}_{1}", i, j)] = (
                (2*minX +  (2 * i + 1) * span_x) / 2, (2 * minY + ( 2 * j + 1) * span_y) / 2)
                self.fillGrid[str.format("{0}_{1}", i, j)] = 0
        for i in range(rows - 1):
            self.fullGrid[str.format("{0}_{1}", i, cols - 1)] = (
            (2 * minX + (2 * i + 1) * span_x) / 2, (2 * minY + (cols - 1 + cols) * span_y) / 2)
            self.fillGrid[str.format("{0}_{1}", i, cols - 1)] = 0
        for j in range(cols - 1):
            self.fullGrid[str.format("{0}_{1}", rows - 1, j)] = (
            (2 * minX + (rows -1 + rows) * span_x) / 2, (2 * minY + (2 * j + 1) * span_y) / 2)
            self.fillGrid[str.format("{0}_{1}", rows - 1, j)] = 0
        self.fullGrid[str.format("{0}_{1}", rows - 1, cols - 1)] = (
        (2 * minX + (rows - 1 + rows) * span_x) / 2, (2 * minY + (cols -1 + cols) * span_y) / 2)
        self.fillGrid[str.format("{0}_{1}", rows - 1, cols - 1)] = 0

        for item in items:
            x = item[long_index]
            y = item[lat_index]
            row = int(math.ceil((x - minX) / span_x)) - 1
            col = int(math.ceil((y - minY) / span_y)) - 1
            if row > rows or row < 0 or col < 0 or col > cols:
                item.append(0)
                item.append(0)
                continue
            self.fillGrid[str.format("{0}_{1}", row, col)] = 1
            item.append(row)
            item.append(col)
        for key in self.fullGrid.keys():
            if self.fillGrid[key] == 0:
                del self.fillGrid[key]

    def run(self):
        CSVFile = ReadCSV.ReadCSV(self.filePath, 3600, self.bbox)
        CSVFile.ReadCSV()
        items = CSVFile.items
        longIndex = CSVFile.title.index("Long")
        latIndex = CSVFile.title.index("Lat")
        colTimeIndex = CSVFile.title.index("CREATED_AT_LOCAL")
        beginTime = datetime.strptime(items[0][colTimeIndex], '%Y-%m-%d %H:%M:%S')
        endTime = datetime.strptime(items[len(items) - 1][colTimeIndex], '%Y-%m-%d %H:%M:%S')
        self.Grid(self.bbox, self.spanX, self.spanY,items, longIndex, latIndex)

        # for i in range(10):
        #     print items[i]
        # print longIndex, latIndex
        # return

        ODMatrix = []
        neigh = {}
        for i in range(0, len(items)):
            neigh[i] = [-1, -1]
        tempItems = list(items[0:self.b])
        ODMatrix, neigh = CSVFile.ConstructODMatrix(tempItems, ODMatrix, neigh, 0, self.b)
        left, top, right, bottom, ratio = Utility.GetLTRB(self.bbox, self.scene)
        pen = QtGui.QPen(QtGui.QColor(GlobalParameters.PredictNodeBrushColor))
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.PredictNodeBrushColor))

        for i in range(0, self.b):
            x, y = items[i][longIndex], items[i][latIndex]
            X, Y = Utility.ConvertPostion2(float(x), float(y), ratio, left, bottom, self.bbox[0], self.bbox[1])
            point = QtGui.QGraphicsEllipseItem(X, Y, GlobalParameters.NodeSize, GlobalParameters.NodeSize)
            point.setBrush(brush)
            point.setPen(pen)
            self.emit(QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"), point, "P", str(len(items) + i))


        for i in range(self.b, len(items)):
            # current NNR
            t = datetime.strptime(items[i][colTimeIndex], '%Y-%m-%d %H:%M:%S')
            t = GlobalParameters.RegressiontotalT * Utility.DeltaTime(t, beginTime) / Utility.DeltaTime(endTime, beginTime)
            currentNNR = self.params[0] * pow(t, 3) + self.params[1] * pow(t, 2) + self.params[2] * t + self.params[3] # call function to get this value

            minDiff = GlobalParameters.Infinite
            minDiffKey = None
            # select best position for next record
            if i % 10 == 0:
                minDiffKey = random.choice(self.fillGrid.keys())
            else:
                for key in self.fillGrid.keys():
                    tempODMatrix = list(ODMatrix)
                    tempNeigh = dict(neigh)
                    record = list(items[i])
                    record[longIndex], record[latIndex] = self.fullGrid[key]
                    tempItems.append(record)
                    tempODMatrix, tempNeigh = CSVFile.ConstructODMatrix(tempItems, tempODMatrix, tempNeigh, i, i + 1)
                    tempItems.pop(len(tempItems) - 1)
                    NNR = CSVFile.NearestNeighborRatio(tempODMatrix, tempNeigh, GlobalParameters.RegressionArea)
                    v = abs(NNR - currentNNR)
                    if  v < minDiff:
                        minDiff = abs(NNR - currentNNR)
                        minDiffKey = key
                        if v < 0.0001:
                            break
            record = list(items[i])

            record[longIndex], record[latIndex] = self.fullGrid[minDiffKey]
            print "Position1:",record[len(record)-2], record[len(record)-1]
            record[len(record)-2], record[len(record)-1] = minDiffKey.split("_")
            print "Position2:",record[len(record)-2], record[len(record)-1]
            #print tempItems[len(tempItems) -1]
            tempItems.append(record)
            #print tempItems[len(tempItems) -1]
            ODMatrix, neigh = CSVFile.ConstructODMatrix(tempItems, ODMatrix, neigh, i, i + 1)

            print record[longIndex], record[latIndex]
            # output new point on the map
            x, y = record[longIndex], record[latIndex]
            x = x + (random.random() - 0.5) * self.spanX
            y = y + (random.random() - 0.5) * self.spanY
            X, Y = Utility.ConvertPostion2(x, y, ratio, left, bottom, self.bbox[0], self.bbox[1])
            point = QtGui.QGraphicsEllipseItem(X, Y, GlobalParameters.NodeSize, GlobalParameters.NodeSize)
            point.setBrush(brush)
            point.setPen(pen)
            self.emit(QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"), point, "P", str(len(items) + i))

        k1 = len(items[0])
        k2 = len(tempItems[0])
        # print items[0], tempItems[0]
        # k3 = len(items)
        # k4 = len(tempItems)
        #print "K1,2,3,4:", k1, k2, k3, k4
        count = 0
        for i in range(len(items)):
            print items[i][k1-2], tempItems[i][k2-2], items[i][k1-1], tempItems[i][k2-1]
            if items[i][k1-2] == tempItems[i][k2-2] and items[i][k1-1] == tempItems[i][k2-1]:
                count += 1
        print count
            ##########      ^&&*  ##############
        self.emit(QtCore.SIGNAL("FinshedRun(QString)"), "Simulation is finished!")




