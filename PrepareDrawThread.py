import Utility

__Author__ = "Lanxue Dang"

from PyQt4 import QtCore, QtGui
import GlobalParameters
import random

class PrepareDrawThread(QtCore.QThread):
    def __init__(self, g, UIMainWindow, box, pos=None):
        QtCore.QThread.__init__(self)
        self.graph = g
        self.position = pos
        if self.position is None:
            self.position = {}
        self.bbox = box
        self.UI = UIMainWindow
        self.nodeItemList = {}
        self.postionItemDict = {}

    def __del__(self):
        self.wait()

    def run(self):
        if self.bbox is None:
            minX = GlobalParameters.CanvasMargin[0]
            minY = GlobalParameters.CanvasMargin[1]
            maxX = self.UI.GraphicsScene.width() - GlobalParameters.CanvasMargin[2]
            maxY = self.UI.GraphicsScene.height() - GlobalParameters.CanvasMargin[3]
        else:
            minX, minY, maxX, maxY = self.bbox

        pen = QtGui.QPen(QtGui.QColor(GlobalParameters.NodeColor))
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.NodeBrushColor))
        for node in self.graph.Nodes():
            if len(self.position) > 0:
                # print node.GetId()
                pointX, pointY = self.position[node.GetId()]
            else:
                if not self.UI.baseMap:
                    pointX, pointY = random.randrange(minX, maxX), random.randrange(minY, maxY)
                else:
                    polygonIndex = random.randint(0, len(self.UI.shapes) -1)
                    direction = self.UI.polyBorderDict[self.UI.shapes[polygonIndex]]
                    #print direction
                    if direction[0][0] == direction[0][1]:
                        direction[0][0] = direction[0][0] - 1
                    if (direction[1][0] == direction[1][1]):
                        direction[1][0] = direction[1][0] - 1

                    tempVar = False
                    i = 1
                    while not tempVar:
                        pointX = random.randrange(int(direction[0][0]), int(direction[0][1]))
                        pointY = random.randrange(int(direction[1][0]), int(direction[1][1]))
                        tempVar = Utility.PointInPolygon(pointX, pointY, direction[2])
                        i = i + 1
                        if i > 25:
                            break

            key = str.format("{0}_{1}", pointX, pointY)
            if key in self.postionItemDict.keys():
                point = self.postionItemDict[key]
            else:
                point = QtGui.QGraphicsEllipseItem(pointX - 0.5 * GlobalParameters.NodeSize, pointY - 0.5 * GlobalParameters.NodeSize, GlobalParameters.NodeSize, GlobalParameters.NodeSize)
                point.setZValue(1)
                point.setBrush(brush)
                point.setPen(pen)
                self.postionItemDict[key] = point
            # self.GraphicsScene.addItem(point)
            self.emit(QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"), point, "P", str(node.GetId()))
            self.nodeItemList[node.GetId()] = [point, pointX, pointY]
            # time.sleep(1)

        EIDict = {}
        for EI in self.graph.Edges():
            srcPoint = self.nodeItemList[EI.GetSrcNId()]
            dstPoint = self.nodeItemList[EI.GetDstNId()]

            key = str(srcPoint[0]) + "_" + str(dstPoint[0])
            if key not in EIDict.keys():
            # self.GraphicsScene.addItem(line)
                delta = 0.5 * GlobalParameters.NodeSize
                pen = QtGui.QPen(QtGui.QColor(GlobalParameters.LineColor))
                line = QtGui.QGraphicsLineItem(
                    srcPoint[1] + delta,
                    srcPoint[2] + delta,
                    dstPoint[1] + delta,
                    dstPoint[2] + delta
                )
                line.setPen(pen)
                line.setZValue(0)
                EIDict[key] = line
            else:
                line = EIDict[key]
            self.emit(QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"), line, "L",
                          key)
        self.emit(QtCore.SIGNAL("FinshedRun(QString)"), "Finish Drawing")
