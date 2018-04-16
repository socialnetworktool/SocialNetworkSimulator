import time
from PyQt4 import QtCore, QtGui
import GlobalParameters
import PlotWindow
import ShapefileReader
import DbfLoader
import Utility
import NetworkView
import snap
import PrepareDrawThread
import CityDiffusion2
from itertools import product

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)



from QTClass import QTCityDiffusion_test
class CityDiffusionForm(QtGui.QWidget, QTCityDiffusion_test.Ui_CityDiffusionWindow):
    def setupUi(self, MainWindow):
        super(CityDiffusionForm, self).setupUi(MainWindow)
        self.graphicsViewMain = NetworkView.NetworkViewer(self.FrameCanvas)
        #self.graphicsViewMain = NetworkView.NetworkViewer(self)
        self.graphicsViewMain.SetParentClass(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsViewMain.sizePolicy().hasHeightForWidth())
        self.graphicsViewMain.setSizePolicy(sizePolicy)
        self.graphicsViewMain.setStyleSheet("background: transparent")
        self.graphicsViewMain.setObjectName(_fromUtf8("graphicsViewMain"))
        self.gridLayout.addWidget(self.graphicsViewMain, 0, 0, 1, 1)

        self.GraphicsScene = QtGui.QGraphicsScene()
        self.GraphicsScene.setSceneRect(0, 0, self.FrameCanvas.width(), self.FrameCanvas.height())

        self.graphicsViewMain.setScene(self.GraphicsScene)

    def retranslateUi(self, MainWindow):
        super(CityDiffusionForm, self).retranslateUi(MainWindow)
        self.pushButtonOpenNetwork.clicked.connect(self.LoadNetworkFile)
        self.pushButtonWeightMatrix.clicked.connect(self.LoadMatrixFile)
        self.pushButtonSelectBaseMap.clicked.connect(self.LoadFile)
        self.pushButtonOpenNetwork.clicked.connect(self.ClickOpenNetwork)
        self.pushButtonDiffusion.clicked.connect(self.ClickDiffusion)
        self.pushButtonSimulation.clicked.connect(self.ClickSimulation)
        self.pushButtonSetting.clicked.connect(self.ClickSetting)
        self.pushButtonClear.clicked.connect(self.ClickClear)
        self.pushButtonDifferentValue.clicked.connect(self.ClickDifferentValue)
        QtCore.QObject.connect(self.radioButtonGlobal, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.CheckRadioButtonGlobal)
        QtCore.QObject.connect(self.radioButtonRegional, QtCore.SIGNAL(_fromUtf8("toggled(bool)")),
                               self.CheckRadioButtonRegional)
        QtCore.QObject.connect(self.radioButtonPercentage, QtCore.SIGNAL(_fromUtf8("toggled(bool)")),
                               self.CheckRadioButtonPercentage)
        QtCore.QObject.connect(self.radioButtonSteps, QtCore.SIGNAL(_fromUtf8("toggled(bool)")),
                               self.CheckRadioButtonSteps)
        self.Initialize()

    def Initialize(self):
        self.graph = None
        self.graphLabelToId = {}
        self.nodeItemList = {}
        self.edgeItemList = {}
        self.polygonItemList = {}
        self.Drawing = False
        self.bbox = None
        self.shapes = None
        self.baseMap = False
        self.nodesLatLonPostion = {}
        self.nodesPosition = {}
        self.positionNodesDict = {}
        self.lineFromTo = {}
        self.weightMatrix = []
        self.numNodes = 0

    def ClickOpenNetwork(self):
        pass

    def ClickOpenWeightMatrix(self):
        pass

    def CheckBaseMap(self):
        if not self.groupBoxBaseMap.isChecked():
            self.bbox = None
            self.baseMap = False
            self.lineEditPathName.setText("")
            self.comboBoxBaseMapLayers.clear()
            for key in self.polygonItemList.keys():
                self.GraphicsScene.removeItem(self.polygonItemList[key])

    def LoadFile(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self, "Load Basemap(Shapefile)", "",
                                                     "Shapefile data files (*.shp)")
        if filePath == "":
            return
        self.lineEditPathName.setText(filePath.split("/")[-1])
        self.shapes, self.shp_type, self.bbox = ShapefileReader.read_shp(filePath)

        # read corresponding dbf data
        dbfFile = DbfLoader.DbfLoader(filePath[:-3] + "dbf")

        t = dbfFile.table2list()
        varNames = dbfFile.get_field_names()
        variables = {}
        for variable in varNames:
            variables[variable] = [record[varNames.index(variable)] for record in t]

        self.dbfdata = variables
        if self.bbox is not None:
            self.ViewBaseMap()

    def ViewBaseMap(self):
        if self.bbox is None:
            Utility.SystemWarning("Please select basemap shapefile before clicking this button!")
            return
        left, top, right, bottom, ratio = Utility.GetLTRB(self.bbox, self.GraphicsScene)
        self.polyBorderDict = {}

        for polygon in self.shapes:
            for i in range(polygon.partsNum):
                points = []
                xList = []
                yList = []
                ployF = QtGui.QPolygonF()
                startIndex = polygon.partsIndex[i]
                if i == polygon.partsNum - 1:
                    endIndex = len(polygon.points)
                else:
                    endIndex = polygon.partsIndex[i + 1]
                for point in polygon.points[startIndex:endIndex]:
                    x, y = Utility.ConvertPostion(point, ratio, left, bottom, self.bbox[0], self.bbox[1])
                    ployF.append(QtCore.QPointF(x, y))
                    points.append([x, y])
                    xList.append(x)
                    yList.append(y)
                self.polyBorderDict[polygon] = [[min(xList), max(xList)]]
                self.polyBorderDict[polygon].append([min(yList), max(yList)])
                self.polyBorderDict[polygon].append(points)
                polylineItem = QtGui.QGraphicsPolygonItem(ployF)
                polylineItem.setBrush(QtGui.QBrush(QtGui.QColor("skyblue")))
                self.GraphicsScene.addItem(polylineItem)
                self.polygonItemList[polygon] = polylineItem
        if len(self.shapes) > 0:
            self.baseMap = True


    def ResetNetwork_Scene(self):
        self.GraphicsScene.clear()
        if self.baseMap:
            self.ViewBaseMap()
        self.Drawing = False
        self.nodeItemList.clear()
        self.edgeItemList.clear()
        self.graph = None
        self.graphLabelToId.clear()

    def LoadWeightMatrix(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self, "Load Network", "",
                                                     "Networkfile data files (*.txt)")
        if filePath == "":
            return
        try:
            f = open(filePath)
        except:
            f = open(filePath)
            return False
        self.graph = snap.TUNGraph.New()
        endofFile = False
        line = f.readline()
        strs = line.split("#")
        numNodes = int(strs[1])
        numEdges = int(strs[3])
        index = 0

        for i in range(numNodes):
            line = f.readline().rstrip("\n").split("#")
            self.graph.AddNode(index)
            self.graphLabelToId[line[0]] = index
            self.nodesLatLonPostion[index] = [line[1], line[2]]
            if len(line) > 1:
                left, top, right, bottom, ratio = Utility.GetLTRB(self.bbox, self.GraphicsScene)
                point = ShapefileReader.Point(float(line[1]), float(line[2]))
                x, y = Utility.ConvertPostion(point, ratio, left, bottom, self.bbox[0], self.bbox[1])
                self.nodesPosition[index] = (x, y)
            index += 1
        for i in range(numEdges):
            line = f.readline().rstrip("\n")
            strs = line.split(",")
            self.graph.AddEdge(self.graphLabelToId[strs[0]], self.graphLabelToId[strs[1]])
        self.DrawGraph(self.graph, self.nodesPosition)



    def LoadNetworkFile(self):
        self.ResetNetwork_Scene()
        filePath = QtGui.QFileDialog.getOpenFileName(self, "Load Network", "",
                                                     "Networkfile data files (*.txt)")
        if filePath == "":
            return
        try:
            f = open(filePath)
        except:
            f = open(filePath)
            return False
        self.graph = snap.TUNGraph.New()
        endofFile = False
        line = f.readline()
        strs = line.split("#")
        self.numNodes = int(strs[1])
        numEdges = int(strs[3])
        index = 0

        for i in range(self.numNodes):
            line = f.readline().rstrip("\n").split("#")
            self.graph.AddNode(index)
            self.graphLabelToId[line[0]] = index
            self.nodesLatLonPostion[index] = [line[1], line[2]]
            if len(line) > 1:
                left, top, right, bottom, ratio = Utility.GetLTRB(self.bbox, self.GraphicsScene)
                point = ShapefileReader.Point(float(line[1]), float(line[2]))
                x, y = Utility.ConvertPostion(point, ratio, left, bottom, self.bbox[0], self.bbox[1])
                self.nodesPosition[index] = (x, y)
            index += 1
        for i in range(numEdges):
            line = f.readline().rstrip("\n")
            strs = line.split(",")
            self.graph.AddEdge(self.graphLabelToId[strs[0]], self.graphLabelToId[strs[1]])
        self.DrawGraph(self.graph, self.nodesPosition)


    def LoadMatrixFile(self):
        self.weightMatrix = []

        filePath = QtGui.QFileDialog.getOpenFileName(self, "Load WeightMatrix", "",
                                                     "WeightMatrix data files (*.txt)")
        if filePath == "":
            return
        try:
            f = open(filePath)
        except:
            f = open(filePath)
            return False

        weightFile = open(filePath, "r")
        lines = weightFile.readlines()
        for line in lines:
            weights = line.rstrip("\r\n").split("#")
            if len(weights) == self.numNodes:
                self.weightMatrix.append(weights)
        if self.weightMatrix:
            for i in range(len(self.weightMatrix)):
                for j in range(len(self.weightMatrix[0])):
                    self.weightMatrix[i][j] = float(self.weightMatrix[i][j])
        else:
            Utility.SystemWarning("weighted matrix does not match with the city network!")
        weightFile.close()

    def DrawGraph(self, graph, position=None):
        # Area used: self.GraphicsScene.width(); self.GraphicsScene.height()
        self.Drawing = True
        self.getThread = PrepareDrawThread.PrepareDrawThread(graph, self, self.bbox, position)
        self.connect(self.getThread, QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"),
                     self.AddItemToScene)
        self.connect(self.getThread, QtCore.SIGNAL("FinshedRun(QString)"), self.FinshedRun)
        self.getThread.start()

    def AddItemToScene(self, item, type, strId):
        if type == "P":
            self.nodeItemList[int(str(strId))] = item
        else:
            self.edgeItemList[strId] = item

            item.setVisible(False)

        self.GraphicsScene.addItem(item)

    def FinshedRun(self, message):
        self.Drawing = False
        Utility.SystemWarning(message, "Congratulations")

    def ClickDiffusion(self):
        self.lastLine = None


        step = 0
        coverage = 0
        if self.radioButtonSteps.isChecked():
            if not Utility.CheckParameter("(INT)", self.lineEditStep.text()):
                Utility.SystemWarning("Please make sure you input a positive integer in the textbox for step ")
                return
            step = int(self.lineEditStep.text())
        elif self.radioButtonPercentage.isChecked():
            if not Utility.CheckParameter("(FLOAT2)", self.lineEditPercentage.text()):
                Utility.SystemWarning("Please make sure you input a positive float in the textbox for coverage ")
                return
            coverage = int(self.lineEditPercentage.text())

        speed = []
        rowCount = self.tableWidgetEmergencyIndex.rowCount()

        if self.radioButtonSteps.isChecked():
            if rowCount != step:
                Utility.SystemWarning("Please set urgency index (0~1) for each step!")
                return
            else:
                for i in range(step):
                    if not Utility.CheckParameter("(FLOAT)", self.tableWidgetEmergencyIndex.item(i,0).text()):
                        Utility.SystemWarning("Please set urgency index (0~1) for each step!")
                        return
                    currentSpeed = float(self.tableWidgetEmergencyIndex.item(i,0).text())
                    speed.append(currentSpeed)
        elif self.radioButtonPercentage.isChecked():
            if rowCount != 1:
                Utility.SystemWarning("Please set urgency index (0~1)!")
                return
            else:
                for i in range(1):
                    if not Utility.CheckParameter("(FLOAT)", self.tableWidgetEmergencyIndex.item(i,0).text()):
                        Utility.SystemWarning("Please set urgency index (0~1) for each step!")
                        return
                    currentSpeed = float(self.tableWidgetEmergencyIndex.item(i,0).text())
                    speed.append(currentSpeed)

        emergencyIndexType = "G"
        decayedCircle = 0.0
        decayedRatio = 0.0
        if self.radioButtonRegional.isChecked():
            emergencyIndexType = "R"
            if not Utility.CheckParameter("(FLOAT2)", self.lineEditDecayedRadius.text()):
                Utility.SystemWarning("Please make sure you input a positive float in the textbox for decayed circle ")
                return
            decayedCircle = float(self.lineEditDecayedRadius.text())

            if not Utility.CheckParameter("(FLOAT2)", self.lineEditDecayedRatio.text()):
                Utility.SystemWarning("Please make sure you input a positive float (0~100) in the textbox for decayed ratio ")
                return
            else:
                ratio = float(self.lineEditDecayedRatio.text())
                if ratio < 0 or ratio > 100:
                    Utility.SystemWarning(
                        "Please make sure you input a positive float (0~100) in the textbox for decayed ratio ")
                    return
            decayedRatio = float(self.lineEditDecayedRatio.text())

        seedNodes = set()
        if self.textEditSeedNodes.toPlainText() == "":
            Utility.SystemWarning("Please make sure you input the ID of seed nodes!")
            return
        seedNodesList = self.textEditSeedNodes.toPlainText().split(";")
        for i in range(len(seedNodesList)):
            try:
                seedNodes.add(int(seedNodesList[i]))
            except:
                Utility.SystemWarning("Please make sure you input the ID of seed nodes that are separated by semicolon!")
                return
        if len(self.weightMatrix) == 0:
            Utility.SystemWarning("Please make sure you load weight matrix file!")
            return


        self.diffusionThread = CityDiffusion2.CityDiffusion(self.graph, seedNodes, self.weightMatrix, speed, step, coverage, self.nodesLatLonPostion, emergencyIndexType, [decayedCircle, decayedRatio])

        self.connect(self.diffusionThread, QtCore.SIGNAL("ActiveNodeCityDiffusion(int, int, int)"),
                     self.ActiveNodeCityDiffusion)
        self.connect(self.diffusionThread, QtCore.SIGNAL("FinishedDiffusion(QString)"), self.FinishedDiffusion)

        self.pushButtonDiffusion.setEnabled(False)
        # self.RestoreDiffusionNodes()
        self.BeginDiffusion()
        time.sleep(0.5)
        self.diffusionThread.start()
        
    def ClickSimulation(self):
        step = 0
        coverage = 0
        if self.radioButtonSteps.isChecked():
            if not Utility.CheckParameter("(INT)", self.lineEditStep.text()):
                Utility.SystemWarning("Please make sure you input a positive integer in the textbox for step ")
                return
            step = int(self.lineEditStep.text())
        elif self.radioButtonPercentage.isChecked():
            if not Utility.CheckParameter("(FLOAT2)", self.lineEditPercentage.text()):
                Utility.SystemWarning("Please make sure you input a positive float in the textbox for coverage ")
                return
            coverage = int(self.lineEditPercentage.text())
            
        # increment = 0.025
        
        # simulationSpeeds = []
        # speeds = [round(i*increment,3) for i in range(int(1/increment*0.35))]
        # simulationSpeeds = list(product(speeds, repeat=step))
        
        # simulationSpeeds = []
        # for i in range(100):
            # speeds = []
            # for j in range(4):
                # speeds.append((i+1)/100.0)
            # simulationSpeeds.append(speeds)
            
        tem_speeds = [0.1,0.2,0.2,0.1]
        simulationSpeeds = []
        for j in range(1,50):
            speeds = []
            for i in range(4):
                speed = tem_speeds[i]*j/10
                speeds.append(round(speed,3))
            simulationSpeeds.append(speeds)
        
        # for j in range(10):
            # speeds = []
            # for i in range(10):
                # if i > 4:
                    # speeds.append(((10/(j+1.0))-(i+1.0)/(j+1))/10+0.2)
                # else:
                    # speeds.append(((i+1.0)/(j+1))/10+0.2)
            # simulationSpeeds.append(speeds)
            
        
        for speed in simulationSpeeds:
            self.lastLine = None

            # step = 0
            # coverage = 0
            # if self.radioButtonSteps.isChecked():
                # if not Utility.CheckParameter("(INT)", self.lineEditStep.text()):
                    # Utility.SystemWarning("Please make sure you input a positive integer in the textbox for step ")
                    # return
                # step = int(self.lineEditStep.text())
            # elif self.radioButtonPercentage.isChecked():
                # if not Utility.CheckParameter("(FLOAT2)", self.lineEditPercentage.text()):
                    # Utility.SystemWarning("Please make sure you input a positive float in the textbox for coverage ")
                    # return
                # coverage = int(self.lineEditPercentage.text())
            
            emergencyIndexType = "G"
            decayedCircle = 0.0
            decayedRatio = 0.0
            if self.radioButtonRegional.isChecked():
                emergencyIndexType = "R"
                if not Utility.CheckParameter("(FLOAT2)", self.lineEditDecayedRadius.text()):
                    Utility.SystemWarning("Please make sure you input a positive float in the textbox for decayed circle ")
                    return
                decayedCircle = float(self.lineEditDecayedRadius.text())

                if not Utility.CheckParameter("(FLOAT2)", self.lineEditDecayedRatio.text()):
                    Utility.SystemWarning("Please make sure you input a positive float (0~100) in the textbox for decayed ratio ")
                    return
                else:
                    ratio = float(self.lineEditDecayedRatio.text())
                    if ratio < 0 or ratio > 100:
                        Utility.SystemWarning(
                            "Please make sure you input a positive float (0~100) in the textbox for decayed ratio ")
                        return
                decayedRatio = float(self.lineEditDecayedRatio.text())
                
            # simulation purpose only, hard-coded.
            
            emergencyIndexType = "R"
            decayedCircle_list = [50,100,150,200,250,300,350,400]
            for dc in decayedCircle_list:
                decayedRatio_list = [5,15,25,35,45,55,65,75,85,95]
                for dr in decayedRatio_list:
                    decayedCircle = dc
                    decayedRatio = dr

                    seedNodes = set()
                    if self.textEditSeedNodes.toPlainText() == "":
                        Utility.SystemWarning("Please make sure you input the ID of seed nodes!")
                        return
                    seedNodesList = self.textEditSeedNodes.toPlainText().split(";")
                    for i in range(len(seedNodesList)):
                        try:
                            seedNodes.add(int(seedNodesList[i]))
                        except:
                            Utility.SystemWarning("Please make sure you input the ID of seed nodes that are separated by semicolon!")
                            return
                    if len(self.weightMatrix) == 0:
                        Utility.SystemWarning("Please make sure you load weight matrix file!")
                        return

                    self.diffusionThread = CityDiffusion2.CityDiffusion(self.graph, seedNodes, self.weightMatrix, speed, step, coverage, self.nodesLatLonPostion, emergencyIndexType, [decayedCircle, decayedRatio])

                    #self.connect(self.diffusionThread, QtCore.SIGNAL("ActiveNodeCityDiffusion(int, int, int)"),
                    #             self.ActiveNodeCityDiffusion)
                    #self.connect(self.diffusionThread, QtCore.SIGNAL("FinishedDiffusion(QString)"), self.FinishedDiffusion)

                    self.pushButtonSimulation.setEnabled(False)
                    # self.RestoreDiffusionNodes()
                    self.BeginDiffusion()
                    time.sleep(0.5)
                    self.diffusionThread.start()
                    i += 1
                    
              
            """
            seedNodes = set()
            if self.textEditSeedNodes.toPlainText() == "":
                Utility.SystemWarning("Please make sure you input the ID of seed nodes!")
                return
            seedNodesList = self.textEditSeedNodes.toPlainText().split(";")
            for i in range(len(seedNodesList)):
                try:
                    seedNodes.add(int(seedNodesList[i]))
                except:
                    Utility.SystemWarning("Please make sure you input the ID of seed nodes that are separated by semicolon!")
                    return
            if len(self.weightMatrix) == 0:
                Utility.SystemWarning("Please make sure you load weight matrix file!")
                return


            self.diffusionThread = CityDiffusion2.CityDiffusion(self.graph, seedNodes, self.weightMatrix, speed, step, coverage, self.nodesLatLonPostion, emergencyIndexType, [decayedCircle, decayedRatio])

            # self.connect(self.diffusionThread, QtCore.SIGNAL("ActiveNodeCityDiffusion(int, int, int)"),
                         # self.ActiveNodeCityDiffusion)
            # self.connect(self.diffusionThread, QtCore.SIGNAL("FinishedDiffusion(QString)"), self.FinishedDiffusion)

            self.pushButtonDiffusion.setEnabled(False)
            # self.RestoreDiffusionNodes()
            self.BeginDiffusion()
            time.sleep(0.5)
            self.diffusionThread.start()
            """
        self.pushButtonSimulation.setEnabled(True)

    def ShowAllNodes(self):
        for k in self.nodeItemList.keys():
            item = self.nodeItemList[k]
            item.setVisible(True)

    def ActiveNodeCityDiffusion(self, node, fromNode, incrementValue):
        item = self.nodeItemList[node]
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.ActivedNodeBrushColor))
        item.setBrush(brush)
        item.setVisible(True)
        rect = item.rect()
        center = rect.center()
        (x, y) = self.nodesPosition[node]
        key = str.format("{0}_{1}", x, y)
        if key in self.positionNodesDict.keys():
            scale = self.positionNodesDict[key] + incrementValue
        else:
            scale = incrementValue
        self.positionNodesDict[key] = scale
        rect.setHeight(GlobalParameters.ActiveNodeSize + scale * 0.02)
        rect.setWidth(GlobalParameters.ActiveNodeSize + scale * 0.02)
        rect.moveCenter(center)
        item.setRect(rect)

        rect1 = self.nodeItemList[fromNode].rect()
        rect2 = self.nodeItemList[node].rect()

        line = QtGui.QGraphicsLineItem(
            rect1.x() + rect1.height() * 0.5,
            rect1.y() + rect1.height() * 0.5,
            rect2.x() + rect2.height() * 0.5,
            rect2.y() + rect2.height() * 0.5
        )
        pen = QtGui.QPen(QtGui.QColor("Red"))
        if self.lastLine:
            self.lastLine.setPen(QtGui.QPen(QtGui.QColor("Blue")))
        key = str.format("{0}_{1}", fromNode, node)
        if key in self.lineFromTo.keys():
            r = self.lineFromTo[key]
            #pen.setWidth(r[0]*0.005 + 1)
            line.setPen(pen)
            self.GraphicsScene.removeItem(r[1])
            self.GraphicsScene.addItem(line)

            self.lineFromTo[key] = [r[0] + 1, line]
        else:
            self.lineFromTo[key] = [1, line]
            line.setPen(pen)
            self.GraphicsScene.addItem(line)
        self.lastLine = line

    def FinishedDiffusion(self, stepActiveNodes):
        if self.lastLine:

            self.lastLine.setPen(QtGui.QPen(QtGui.QColor("Blue")))
        #Utility.SystemWarning("Information diffusion is finished!")
        # self.textInfoWidget.setPlainText("")
        self.ShowAllNodes()
        self.pushButtonDiffusion.setEnabled(True)

        # show result (Figure)
        win = PlotWindow.PlotWindow("The number of active cities in each step")
        win.show()
        y = str(stepActiveNodes).split("_")
        yy = []
        for i in range(len(y)):
            yy.append(int(y[i]))
        win.y = yy
        win.DrawPlot3()

        win = PlotWindow.PlotWindow("Percentage of active cities")
        win.show()
        nodesCount = self.graph.GetNodes()
        totalActive = 0
        for i in range(len(yy)):
            totalActive += yy[i]
            yy[i] = totalActive * 100.0 / nodesCount
        win.y = yy
        win.DrawPlot4()



    def BeginDiffusion(self):
        self.RestoreDiffusionNodes()
        for k in self.nodeItemList.keys():
            item = self.nodeItemList[k]
            item.setVisible(False)
        for k in self.edgeItemList.keys():
            item = self.edgeItemList[k]
            item.setVisible(False)
            #self.checkBoxEdge.setChecked(False)

    def RestoreDiffusionNodes(self):
        self.activedNodes = 0
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.NodeColor))
        for k in self.nodeItemList.keys():
            item = self.nodeItemList[k]
            item.setBrush(brush)
            rect = item.rect()
            item.setRect(rect.x(), rect.y(), GlobalParameters.NodeSize, GlobalParameters.NodeSize)
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.SeedNodeBrushColor))
        # for k in self.seedNodes:
        #     item = self.nodeItemList[k]
        #     item.setBrush(brush)
        #     rect = item.rect()
        #     item.setRect(rect.x(), rect.y(), GlobalParameters.SeedNodeSize, GlobalParameters.SeedNodeSize)
        for key in self.positionNodesDict.keys():
            self.positionNodesDict[key] = 0

        for k in self.lineFromTo.keys():
            line = self.lineFromTo[k][1]
            self.GraphicsScene.removeItem(line)
            self.lineFromTo.pop(k)

    def ClickDifferentValue(self):
        if self.lineEditStep.text() == "":
            Utility.SystemWarning("Please input the number of simulation steps!")
            return
        while self.tableWidgetEmergencyIndex.rowCount() < int(self.lineEditStep.text()) :
            print self.tableWidgetEmergencyIndex.rowCount()
            print self.lineEditStep.text()
            i = self.tableWidgetEmergencyIndex.rowCount()
            self.tableWidgetEmergencyIndex.insertRow(i)
            item = QtGui.QTableWidgetItem()
            item.setText("")
            self.tableWidgetEmergencyIndex.setItem(i, 0, item)

    def ClickClear(self):
        while self.tableWidgetEmergencyIndex.rowCount() > 0:
            self.tableWidgetEmergencyIndex.removeRow(0)

    def ClickSetting(self):
        setStep = 0
        if self.radioButtonSteps.isChecked():
            if self.lineEditStep.text() == "":
                Utility.SystemWarning("Please input the number of simulation steps!")
                return
            if self.lineEditEmergencyIndexValue.text() == "":
                Utility.SystemWarning("Please input the default value of emergency index!")
                return
            if not Utility.CheckParameter("(FLOAT)", self.lineEditEmergencyIndexValue.text()):
                Utility.SystemWarning("Please set urgency index (0~1) for each step!")
                return
            setStep = int(self.lineEditStep.text())
        elif self.radioButtonPercentage.isChecked():
            setStep = 1

        while self.tableWidgetEmergencyIndex.rowCount() < setStep:
            print self.tableWidgetEmergencyIndex.rowCount()
            print self.lineEditStep.text()
            i = self.tableWidgetEmergencyIndex.rowCount()
            self.tableWidgetEmergencyIndex.insertRow(i)
            item = QtGui.QTableWidgetItem()
            item.setText(self.lineEditEmergencyIndexValue.text())
            self.tableWidgetEmergencyIndex.setItem(i, 0, item)
        while self.tableWidgetEmergencyIndex.rowCount() > setStep:
            self.tableWidgetEmergencyIndex.removeRow(setStep)

        for i in range(setStep):
            item = QtGui.QTableWidgetItem()
            item.setText(self.lineEditEmergencyIndexValue.text())
            self.tableWidgetEmergencyIndex.setItem(i, 0, item)

    def CheckRadioButtonRegional(self):
        T_F = self.radioButtonRegional.isChecked()
        self.lineEditDecayedRadius.setEnabled(T_F)
        self.lineEditDecayedRatio.setEnabled(T_F)
        self.label_5.setEnabled(T_F)
        self.label_6.setEnabled(T_F)
        self.radioButtonGlobal.setChecked(not T_F)

    def CheckRadioButtonGlobal(self):
        T_F = self.radioButtonGlobal.isChecked()
        self.radioButtonRegional.setChecked(not T_F)
        self.lineEditDecayedRadius.setEnabled(not T_F)
        self.lineEditDecayedRatio.setEnabled(not T_F)
        self.label_5.setEnabled(not T_F)
        self.label_6.setEnabled(not T_F)

    def CheckRadioButtonPercentage(self):
        while self.tableWidgetEmergencyIndex.rowCount() > 1:
            self.tableWidgetEmergencyIndex.removeRow(1)
        self.pushButtonDifferentValue.setEnabled(False)

    def CheckRadioButtonSteps(self):
        self.pushButtonDifferentValue.setEnabled(True)





