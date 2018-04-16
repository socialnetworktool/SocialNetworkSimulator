__author__ = 'Lanxue Dang'

import csv
import os
import math
import random
import time
import snap
import Centrality
import DbfLoader
import Diffusion
import CityDiffusion
import CityDiffusionForm
import GlobalParameters
import NetworkGenerator
import NetworkView
import PlotWindow
import PrepareDrawThread
import ReadCSV
import ShapefileReader
import SpatialPredict
import Utility
from QTClass import QTMainForm
from PyQt4 import QtCore, QtGui
from CharacteristicForm import CharacteristicForm

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


class UIMainWindow(QtGui.QMainWindow, QTMainForm.Ui_MainWindow):
    def setupUi(self, MainWindow):
        super(UIMainWindow, self).setupUi(MainWindow)
        self.graphicsViewMain = NetworkView.NetworkViewer(self.FrameCanvas)
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
        # self.textInfoWidget = QtGui.QGraphicsItemGroup(None, self.GraphicsScene) #self.GraphicsScene.addText("", QtGui.QFont("Times", 20, QtGui.QFont.Bold))
        # self.textInfoWidget.setPos(QtCore.QPoint(5, 5))
        self.graphicsViewMain.setScene(self.GraphicsScene)

        self.DisableTableWidget(self.tableWidgetNetworkCharacteristics, 0)
        self.DisableTableWidget(self.tableWidgetNetworkCharacteristics, 1)
        self.DisableTableWidget(self.tableWidgetParameter, 0)
        Utility.InitCombobox(self.comboBoxNetworkType, GlobalParameters.NetworkType)
        Utility.InitCombobox(self.comboBoxNetworkTypeforComplex, GlobalParameters.NetworkType)
        Utility.InitCombobox(self.comboBoxAlgorithmsforSeedNode, GlobalParameters.AlgrotihmsforSeedNodes)

    def retranslateUi(self, MainWindow):
        super(UIMainWindow, self).retranslateUi(MainWindow)
        self.networkCount = 0
        self.complexNetworkParameters = []
        self.activedNodes = 0
        self.seedNodes = set()
        self.communities = []
        self.ConnectEvent()
        self.changed = True
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
        self.seedNodes = set()
        self.communities = []
        self.opinionLeaders = set()
        self.InitCentralityForm()
        self.postiveNodesDict = {}
        self.nodesPosition = {}
        self.lineFromTo = {}
        self.aggregate = 0

    def TurnOffAllWindows(self):
        self.groupBoxNetworkAnalysis.setVisible(False)
        self.groupBoxNetworkGenerator.setVisible(False)
        self.groupBoxSimulator.setVisible(False)
        self.groupBoxComplexNetwork.setVisible(False)
        self.groupBoxFindParameters.setVisible(False)
        self.groupBoxCommunity.setVisible(False)

    def DisableTableWidget(self, tabWidget, columNum):
        row = tabWidget.rowCount()
        for i in range(row):
            item = tabWidget.item(i, columNum)
            item.setFlags(QtCore.Qt.ItemIsEnabled)

    def ConnectEvent(self):
        # menu
        QtCore.QObject.connect(self.actionGenerate_Simulated_Network, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DomenuNetwork)
        QtCore.QObject.connect(self.actionNetwork_Analysis, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DomenuAnalysis)
        QtCore.QObject.connect(self.actionUser_Level, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DomenuSimulatorUserLevel)
        QtCore.QObject.connect(self.actionSave_Network, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DoMenuSaveNetwork)
        QtCore.QObject.connect(self.actionCity_Level, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DomenuSimulatorCityLevel)
        QtCore.QObject.connect(self.actionGenerate_Complex_Network, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DomenuComplexNetworkGenerator)
        QtCore.QObject.connect(self.actionDemonstrate_Temporal_Spatial_Process, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.LoadPointFromCSV)
        QtCore.QObject.connect(self.actionPredict_Diffusion, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.PredictDiffusion)
        QtCore.QObject.connect(self.actionFindParameters, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DomenuFindParameters)
        QtCore.QObject.connect(self.actionLoad_Network, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DomenuLoadNetwork)

        QtCore.QObject.connect(self.actionCNM, QtCore.SIGNAL(_fromUtf8("triggered()")), self.DoMenuCNW)
        QtCore.QObject.connect(self.groupBoxLTModel, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.CheckLTCheckBox)
        QtCore.QObject.connect(self.groupBoxICModel, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.CheckICCheckBox)
        QtCore.QObject.connect(self.groupBoxBaseMap, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.CheckBaseMap)
        QtCore.QObject.connect(self.actionExtract_Diffusion_Network,QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DoMenuExtractRetweetNetwork)

        QtCore.QObject.connect(self.actionExtract_Mentioned_Network, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.DoMenuExtractMentionNetwork)

        # ButtonClick
        self.pushButtonGenerateNetwork.clicked.connect(self.ClickGenerateNetwork)
        self.pushButtonRestNetwork.clicked.connect(self.ClickRestNetwork)
        self.pushButtonExpandShrink.clicked.connect(self.ClickExpandShrinkTalbe)
        self.pushButtonOKforNetworkCount.clicked.connect(self.ClickOKforNetworkCount)
        self.pushButtonAddConnect.clicked.connect(self.ClickAddConnect)
        self.pushButtonRemoveConnect.clicked.connect(self.ClickRemoveConnect)
        self.pushButtonGenerateComplexNetwork.clicked.connect(self.ClickGenerateComplexNetwork)
        self.pushButtonSaveComplexNetworkParams.clicked.connect(self.ClickSaveComplexParameters)
        self.pushButtonOverview.clicked.connect(self.ClickOverviewofParameters)
        self.pushButtonNetworkcharacteristic.clicked.connect(self.ClickRunNetworkcharacteristic)
        self.pushButtonDiffusion.clicked.connect(self.ClickDiffusion)
        self.pushButtonGenerateSeedNodes.clicked.connect(self.ClickGenerateSeedNodes)
        self.pushButtonGenerateOpinionLeaders.clicked.connect(self.ClickGenerateOpinionLeaders)
        self.pushButtonSelectBaseMap.clicked.connect(self.LoadFile)
        self.pushButtonViewBaseMap.clicked.connect(self.ViewBaseMap)
        self.pushButtonSelectBaseMapComplex.clicked.connect(self.LoadFile)
        self.pushButtonViewBaseMapComplex.clicked.connect(self.ViewBaseMap)
        self.pushButtonFindParameters.clicked.connect(self.ClickFindParameters)
        self.pushButtonOpenParameter.clicked.connect(self.ClickOpenParameterFile)
        self.pushButtonDrawCounterMap.clicked.connect(self.DrawErrorCounter)
        self.pushButtonBetweennessCentrality.clicked.connect(self.ClickBetweennessCentrality)
        self.pushButtonDegreeCentrality.clicked.connect(self.ClickDegreeCentrality)
        self.pushButtonClosenessCentrality.clicked.connect(self.ClickClosenessCentrality)
        self.pushButtonEigenvCentrality.clicked.connect(self.ClickEigenvectorCentrality)
        #self.pushButtonOpenWeightMatrix.clicked.connect(self.ClickOpenWeightMatrix)

        # checkboxClick
        self.checkBoxEdge.clicked.connect(self.CheckShowEdge)

        # Mouse Event

        # selectedchange
        self.comboBoxNetworkType.currentIndexChanged.connect(self.SelectedChangeComboBoxNetworkType)
        self.comboBoxNetworkTypeforComplex.currentIndexChanged.connect(self.SelChangeCombNetworkTypeforComplex)

    # for menu
    def DomenuAnalysis(self):
        self.TurnOffAllWindows()
        self.groupBoxNetworkAnalysis.setVisible(True)

    def DomenuNetwork(self):
        self.TurnOffAllWindows()
        self.groupBoxNetworkGenerator.setVisible(True)

    def DomenuSimulatorUserLevel(self):
        self.TurnOffAllWindows()
        self.groupBoxSimulator.setVisible(True)
        self.SimulatorPartEnabled("USER")

    def DomenuSimulatorCityLevel(self):

        # form = QtGui.QMainWindow()
        # UI = CityDiffusionForm.CityDiffusionForm()
        # UI.setupUi(form)

        self.cityDiffusionForm.show()
        self.cityDiffusionForm.showMaximized()
        self.cityDiffuiosnUI.GraphicsScene.setSceneRect(0, 0, self.cityDiffuiosnUI.FrameCanvas.width() - 10, self.cityDiffuiosnUI.FrameCanvas.height() - 10)


        # self.TurnOffAllWindows()
        # self.groupBoxSimulator.setVisible(True)
        # self.SimulatorPartEnabled("CITY")

    def SimulatorPartEnabled(self, level):
        # if level == "CITY":
        #     self.groupBoxICModel.setEnabled(False)
        #     self.groupBoxLTModel.setEnabled(False)
        #     self.groupBoxSeedNodes.setEnabled(False)
        #     self.groupBoxOpinionLeaders.setEnabled(False)
        #     self.groupBoxCityLevelDiffusion.setEnabled(True)
        # else:
        self.groupBoxICModel.setEnabled(True)
        self.groupBoxLTModel.setEnabled(True)
        self.groupBoxSeedNodes.setEnabled(True)
        self.groupBoxOpinionLeaders.setEnabled(True)
        #self.groupBoxCityLevelDiffusion.setEnabled(False)

    def DomenuComplexNetworkGenerator(self):
        self.TurnOffAllWindows()
        self.groupBoxComplexNetwork.setVisible(True)

    def DomenuFindParameters(self):
        self.TurnOffAllWindows()
        self.groupBoxFindParameters.setVisible(True)

    def DoMenuSaveNetwork(self):
        if self.graph is None:
            Utility.SystemWarning("There is no network to save!")
            return
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        file = open(name, 'w')
        nNodes = self.graph.GetNodes()
        nEdges = self.graph.GetEdges()
        seqences = []
        seqences.append(str.format("Nodes#{0}#Edges#{1}\n", nNodes, nEdges))
        for node in self.graph.Nodes():
            seqences.append(str.format("{0}\n", node.GetId()))
        for EI in self.graph.Edges():
            seqences.append(str.format("{0}#{1}\n", EI.GetSrcNId(), EI.GetDstNId()))
        file.writelines(seqences)
        file.close()

    def DoMenuCNW(self):
        if self.graph is None:
            Utility.SystemWarning("There is no network!")
            return

        CmtyV = snap.TCnComV()
        snap.CommunityCNM(self.graph, CmtyV)
        colorList = list(GlobalParameters.COLOR_LIST)
        random.shuffle(colorList)
        count = -1

        for i in range(self.tableWidgetCommunity.rowCount()):
            self.tableWidgetCommunity.removeRow(0)

        self.ClearSeedNodes()

        for Cmty in CmtyV:
            if count < len(colorList):
                count += 1
            else:
                count = 0
            brush = QtGui.QBrush(QtGui.QColor(colorList[count]))
            community = []
            for NI in Cmty:
                item = self.nodeItemList[NI]
                item.setBrush(brush)
                community.append(NI)
            self.communities.append(community)
            i = self.tableWidgetCommunity.rowCount()
            self.tableWidgetCommunity.insertRow(i)
            # item = QtGui.QTableWidgetItem()
            # item.setText(str(i))
            # self.tableWidgetCommunity.setItem(i, 0, item)
            item = QtGui.QTableWidgetItem()
            item.setText(str(len(community)))
            item.setTextAlignment(0x0004|0x0080) # center(horizonal | vertical)
            self.tableWidgetCommunity.setItem(i, 0, item)
            item = QtGui.QTableWidgetItem()
            item.setBackgroundColor(brush.color())
            self.tableWidgetCommunity.setItem(i, 1, item)

        # print self.communities
        self.TurnOffAllWindows()
        self.groupBoxCommunity.setVisible(True)
        Utility.SystemWarning(str.format("There are {} communities in this network!", len(CmtyV)))


    def DomenuLoadNetwork(self):
        self.ClickRestNetwork()
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
            if len(line) > 1:
                left, top, right, bottom, ratio = Utility.GetLTRB(self.bbox, self.GraphicsScene)
                point = ShapefileReader.Point(float(line[1]), float(line[2]))
                x, y = Utility.ConvertPostion(point, ratio, left, bottom, self.bbox[0], self.bbox[1])
                self.nodesPosition[index] = (x, y)
            index += 1
        for i in range(numEdges):
            line = f.readline().rstrip("\n")
            strs = line.split("#")
            self.graph.AddEdge(self.graphLabelToId[strs[0]], self.graphLabelToId[strs[1]])
        self.DrawGraph(self.graph, self.nodesPosition)

    # for button
    def ClickGenerateNetwork(self):

        if self.Drawing:
            Utility.SystemWarning("Now you are drawing, Please wait!")
            return

        if self.comboBoxNetworkType.currentText() == "":
            Utility.SystemWarning("Please select a network type!")
            return
        for i in range(self.tableWidgetParameter.rowCount()):
            if not Utility.CheckParameter(self.tableWidgetParameter.item(i, 0).text(),
                                          self.tableWidgetParameter.item(i, 1).text()):
                Utility.SystemWarning(
                    "Please set all parameters in appropriate format! \n (int) means an integer bigger than 0.\n (float) menas a float number between 0 and 1.")
                return

        if len(self.nodeItemList) > 0:
            if not Utility.SystemTipYesNO("Do you want to redraw existing network?"):
                return
            else:
                self.ResetWholeNetwork()

        generator = NetworkGenerator.NetworkGenerator()
        params = [self.comboBoxNetworkType.currentText()]
        for i in range(self.tableWidgetParameter.rowCount()):
            params.append(self.tableWidgetParameter.item(i, 1).text())
        self.graph = generator.SimpleNetworkGenerator(params)
        if self.graph != None:
            self.DrawGraph(self.graph)
        else:
            Utility.SystemWarning("Failed to generate network. Please check your parameters!")


    def ClickGenerateOpinionLeaders(self):
        if self.graph is None:
            Utility.SystemWarning("Please make sure that there is a network before simulating information diffusion!")
            return

        if self.radioButtonEachCommunity.isChecked():
            method = "C" #Community
            if len(self.communities) == 0:
                Utility.SystemWarning("Failed to generate opinion leaders. Please first do community detection!")
                return
        else:
            method = "W" # Whole
        if not Utility.CheckParameter("(FLOAT2)", self.lineEditPropotion.text()):
            Utility.SystemWarning("Please input the propotion of opinion leaders!")
            return
        proportion = float(self.lineEditPropotion.text()) * 0.01
        if proportion < 0 or proportion > 100:
            Utility.SystemWarning("The number of opinion leaders should be between 0 and 100!")
            return
        self.ClearOpinionLeaders()
        centrality = Centrality.Centrality(self.graph)
        self.opinionLeaders = centrality.GetOpinionLeaders(method, proportion, self.communities)

        if not self.seedNodes:
            self.RestoreDiffusionNodes()
        elif not self.activedNodes:
            self.RestoreDiffusionNodes()
            self.ShowSeedNodes()
        self.ShowOpinionLeaders()

    def ShowSeedNodes(self):
        for i in self.seedNodes:
            self.ShowSpecialNodes(i, GlobalParameters.SeedNodeSize, GlobalParameters.SeedNodeBrushColor)

    def ShowOpinionLeaders(self):
        for i in self.opinionLeaders:
            if i not in self.seedNodes:
                self.ShowSpecialNodes(i, GlobalParameters.OpinionLeaderSize, GlobalParameters.OpinionLeaderColor)

    def ClickGenerateComplexNetwork(self):

        if self.Drawing:
            Utility.SystemWarning("Now you are drawing, Please wait!")
            return

        if len(self.nodeItemList) > 0:
            if not Utility.SystemTipYesNO("Are you sure you want to redraw complex network?"):
                return
            else:
                self.ResetNetwork_Scene()
                self.ResetNetwork_Characteristics()
                self.ResetNetwork_Diffusion()

        for i in range(len(self.complexNetworkParameters)):
            if self.complexNetworkParameters[i] is None:
                Utility.SystemWarning("Please set parameters for every network!")
                return

        links = []
        for i in range(self.tableWidgetComplexLinks.rowCount()):
            links.append([self.tableWidgetComplexLinks.cellWidget(i, 0).currentText(),
                          self.tableWidgetComplexLinks.item(i, 1).text(),
                          self.tableWidgetComplexLinks.cellWidget(i, 2).currentText(),
                          self.tableWidgetComplexLinks.cellWidget(i, 3).currentText(),
                          self.tableWidgetComplexLinks.item(i, 4).text(),
                          self.tableWidgetComplexLinks.cellWidget(i, 5).currentText()])

        generator = NetworkGenerator.NetworkGenerator()
        self.graph, graphs = generator.ComplexNetworkGenerator(self.complexNetworkParameters, links)
        self.DrawGraph(self.graph)

        # Draw edges among networks

    def ClickRestNetwork(self):

        if self.Drawing:
            Utility.SystemWarning("Now you are drawing, Please wait!")
            return

        self.ResetWholeNetwork()

    def ClickRunNetworkcharacteristic(self):
        if self.graph is not None:
            self.tableWidgetNetworkCharacteristics.item(0, 1).setText(str(self.graph.GetNodes()))
            self.tableWidgetNetworkCharacteristics.item(1, 1).setText(str(self.graph.GetEdges()))
            Nodes = snap.TIntV()
            for nodeId in range(10):
                Nodes.Add(nodeId)
            self.tableWidgetNetworkCharacteristics.item(2, 1).setText(
                str(snap.GetModularity(self.graph, Nodes, self.graph.GetEdges())))
            self.tableWidgetNetworkCharacteristics.item(3, 1).setText(str(snap.GetBfsEffDiam(self.graph, 10, False)))

    def ClickExpandShrinkTalbe(self):
        if self.pushButtonExpandShrink.text() == "Expand Table":
            self.groupBoxComplexNetwork.setFixedWidth(650)
            self.tableWidgetComplexLinks.setFixedWidth(640)
            self.pushButtonExpandShrink.setText("Shrink Table")
        else:
            self.tableWidgetComplexLinks.setFixedWidth(235)
            self.groupBoxComplexNetwork.setFixedWidth(250)
            self.pushButtonExpandShrink.setText("Expand Table")

    def ClickOKforNetworkCount(self):
        if self.Drawing:
            Utility.SystemWarning("Now you are drawing, Please wait!")
            return

        if self.networkCount > 0 or len(self.nodeItemList) > 0:
            if not Utility.SystemTipYesNO("Are you sure you want to reset complex network?"):
                return
            else:  # reset network
                self.ResetWholeNetwork()

        if not Utility.CheckParameter("(int)", self.lineEditNetworkCount.text()):
            Utility.SystemWarning("Please input an integer that is greater than 0!")
            return
        self.networkCount = (int)(self.lineEditNetworkCount.text())
        self.complexNetworkParameters = [None] * self.networkCount
        itemList = []
        for i in range(self.networkCount):
            itemList.append(str(i))
        Utility.InitCombobox(self.comboBoxNetworkID, itemList)

    def ResetWholeNetwork(self):
        # for secen
        self.ResetNetwork_Scene()
        # for complex network
        self.ResetNetwork_Complex()
        # for characteriscs
        self.ResetNetwork_Characteristics()
        # for community
        self.ResetCommunities()
        # for diffusion
        self.ResetNetwork_Diffusion()

    def ResetNetwork_Scene(self):
        self.GraphicsScene.clear()
        if self.baseMap:
            self.ViewBaseMap()
        self.Drawing = False
        self.nodeItemList.clear()
        self.edgeItemList.clear()
        self.graph = None
        self.graphLabelToId.clear()

    def ResetNetwork_Complex(self):
        self.networkCount = 0
        self.comboBoxNetworkID.clear()
        self.comboBoxNetworkTypeforComplex.setCurrentIndex(0)
        for i in range(self.tableWidgetComplexLinks.rowCount()):
            self.tableWidgetComplexLinks.removeRow(0)

    def ResetNetwork_Characteristics(self):
        self.tableWidgetNetworkCharacteristics.item(0, 1).setText("")
        self.tableWidgetNetworkCharacteristics.item(1, 1).setText("")
        self.tableWidgetNetworkCharacteristics.item(2, 1).setText("")
        self.tableWidgetNetworkCharacteristics.item(3, 1).setText("")

    def ResetNetwork_Diffusion(self):
        self.seedNodes.clear()
        self.opinionLeaders.clear()
        self.lineFromTo.clear()
        self.activedNodes = 0
        self.lineEditNumberofSeedNodes.setText("0")

    def ResetCommunities(self):
        self.communities = []

    def ClickSaveComplexParameters(self):
        if self.comboBoxNetworkID.currentIndex() == 0 or self.comboBoxNetworkTypeforComplex.currentIndex() == 0:
            Utility.SystemWarning("Please select a network ID and a type!")
            return
        paramName = []
        paramValue = []
        for i in range(self.tableWidgetParameterComplexParameters.rowCount()):
            if not Utility.CheckParameter(self.tableWidgetParameterComplexParameters.item(i, 0).text(),
                                          self.tableWidgetParameterComplexParameters.item(i, 1).text()):
                Utility.SystemWarning(
                    "Please set all parameters in appropriate format! \n (int) means an integer bigger than 0.\n (float) menas a float number between 0 and 1.")
                return
            paramName.append(self.tableWidgetParameterComplexParameters.item(i, 0).text())
            paramValue.append(self.tableWidgetParameterComplexParameters.item(i, 1).text())
        self.complexNetworkParameters[int(self.comboBoxNetworkID.currentText())] = [
            self.comboBoxNetworkTypeforComplex.currentText(), paramName, paramValue]
        Utility.SystemWarning(
            "Parameters for network {0} have been saved.".format(int(self.comboBoxNetworkID.currentText())), "OK")

    def ClickOverviewofParameters(self):
        message = ""
        for i in range(len(self.complexNetworkParameters)):
            if self.complexNetworkParameters[i] is not None:
                message += "Network{0}: Network type: {1}\n".format(i, self.complexNetworkParameters[i][0])
                for j in range(len(self.complexNetworkParameters[i][1])):
                    message += "\t{0}:{1}\n".format(self.complexNetworkParameters[i][1][j],
                                                    self.complexNetworkParameters[i][2][j])
            else:
                message += "Network{0}: Network type: None\n".format(i)

        Utility.SystemWarning(message, "Complex Network Parameters")

    def ClickGenerateSeedNodes(self):
        if self.graph is None:
            Utility.SystemWarning("Please make sure that there is a network before simulating information diffusion!")
            return
        if not Utility.CheckParameter("(int)", self.lineEditNumberofSeedNodes.text()):
            Utility.SystemWarning("Please input the number of seed nodes!")
            return
        if self.comboBoxAlgorithmsforSeedNode.currentText() == "":
            Utility.SystemWarning("Please select the algorithm for selecting seed nodes!")
            return
        # print self.graph
        centrality = Centrality.Centrality(self.graph)
        self.ClearSeedNodes()
        # print self.lineEditNumberofSeedNodes.text(), self.comboBoxAlgorithmsforSeedNode.currentText()
        self.seedNodes = centrality.GetSeedNodes(int(self.lineEditNumberofSeedNodes.text()),
                                                 self.comboBoxAlgorithmsforSeedNode.currentText())

        self.RestoreDiffusionNodes()
        self.ShowSeedNodes()
        self.ShowOpinionLeaders()

    def ClickDiffusion(self):
        # if self.groupBoxCityLevelDiffusion.isEnabled():
        #     currentStatus = {}
        #     path1 = "C:\\SocialNetworkSimulator\\Tweets\\Vaccine\\CurrentStatus.txt"
        #     statusFile = open(path1, "r")
        #     lines = statusFile.readlines()
        #     for line in lines:
        #         status = line.rstrip("\r\n").split("#")
        #         if len(status) == 2:
        #             currentStatus[int(status[0])] = int(status[1])
        #     statusFile.close()
        #     weightMatrix = []
        #     path2 = "C:\\SocialNetworkSimulator\\Tweets\\Vaccine\\WeightMatrix.txt"
        #     weightFile = open(path2, "r")
        #     lines = weightFile.readlines()
        #     for line in lines:
        #         weights = line.rstrip("\r\n").split("#")
        #         print len(weights)
        #         if len(weights) == 30:
        #             weightMatrix.append(weights)
        #     weightFile.close()
        #     speed = 0.01
        #     step = 1
        #     print weightMatrix
        #     self.diffusionThread = CityDiffusion.CityDiffusion(self.graph, currentStatus, weightMatrix, speed, step)
        #
        #     self.connect(self.diffusionThread, QtCore.SIGNAL("ActiveNodeCityDiffusion(int, int, int)"),
        #                  self.ActiveNodeCityDiffusion)
        #     self.connect(self.diffusionThread, QtCore.SIGNAL("FinishedDiffusion()"), self.FinishedDiffusion)
        #
        #     self.pushButtonDiffusion.setEnabled(False)
        #     # self.RestoreDiffusionNodes()
        #     self.BeginDiffusion()
        #     time.sleep(0.5)
        #     self.diffusionThread.start()
        #
        # else:
        if len(self.seedNodes) == 0:
            Utility.SystemWarning("Please select seed nodes!")
            return
        if self.groupBoxICModel.isChecked():
            if (not Utility.CheckParameter("(float)", self.lineEditOpinionNodePopagate.text())) or (
                    not Utility.CheckParameter("(float)", self.lineEditNormalNodePopagate.text())):
                Utility.SystemWarning(
                    "Please set all parameters in appropriate format! \n(float) menas a float number between 0 and 1.")
                return
            if not self.opinionLeaders:
                if not Utility.SystemTipYesNO("The set of opinion leaders is null. Do you want to continue?"):
                    return
            self.diffusionThread = Diffusion.Diffusion(self.graph, self.seedNodes, self.opinionLeaders, "IC",
                                                       float(self.lineEditOpinionNodePopagate.text()),
                                                       float(self.lineEditNormalNodePopagate.text()))
        elif self.groupBoxLTModel.isChecked():
            self.diffusionThread = Diffusion.Diffusion(self.graph, self.seedNodes, self.seedNodes, "LT")
            if Utility.CheckParameter("(float)", self.lineEditThreshold.text()):
                self.diffusionThread.SetLTThreshold(float(self.lineEditThreshold.text()))
        else:
            Utility.SystemWarning("Please select a model for diffusion!")
            return
        self.connect(self.diffusionThread, QtCore.SIGNAL("ActiveNodeDiffusion(int, int, int)"),
                     self.ActiveNodeDiffusion)
        self.connect(self.diffusionThread, QtCore.SIGNAL("FinishedDiffusion()"), self.FinishedDiffusion)
        self.pushButtonGenerateSeedNodes.setEnabled(False)
        self.pushButtonGenerateOpinionLeaders.setEnabled(False)
        self.pushButtonDiffusion.setEnabled(False)
        # self.RestoreDiffusionNodes()
        self.BeginDiffusion()
        time.sleep(0.5)
        self.diffusionThread.start()

    def ShowSpecialNodes(self, int, size, color):
        if self.aggregate:
            return
        item = self.nodeItemList[int]
        rect = item.rect()
        item.setRect(rect.x(), rect.y(), size, size)
        item.setZValue(1)
        # self.GraphicsScene.removeItem(item)
        # item.setPos(pos)
        # self.GraphicsScene.addItem(item)
        brush = QtGui.QBrush(QtGui.QColor(color))
        item.setBrush(brush)

    def ShowAllNodes(self):
        for k in self.nodeItemList.keys():
            item = self.nodeItemList[k]
            item.setVisible(True)

    def ClearSeedNodes(self):
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.NodeColor))
        for k in self.seedNodes:
            item = self.nodeItemList[k]
            item.setBrush(brush)
            rect = item.rect()
            item.setRect(rect.x(), rect.y(), GlobalParameters.NodeSize, GlobalParameters.NodeSize)
        self.seedNodes.clear()

    def ClearOpinionLeaders(self):
        for i in self.opinionLeaders:
            if i not in self.seedNodes:
                self.ShowSpecialNodes(i, GlobalParameters.SeedNodeSize, GlobalParameters.NodeColor)
        self.opinionLeaders.clear()

    def RestoreDiffusionNodes(self):
        self.activedNodes = 0
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.NodeColor))
        for k in self.nodeItemList.keys():
            item = self.nodeItemList[k]
            item.setBrush(brush)
            rect = item.rect()
            item.setRect(rect.x(), rect.y(), GlobalParameters.NodeSize, GlobalParameters.NodeSize)
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.SeedNodeBrushColor))
        for k in self.seedNodes:
            item = self.nodeItemList[k]
            item.setBrush(brush)
            rect = item.rect()
            item.setRect(rect.x(), rect.y(), GlobalParameters.SeedNodeSize, GlobalParameters.SeedNodeSize)
        for key in self.postiveNodesDict.keys():
            self.postiveNodesDict[key] = 0
    def BeginDiffusion(self):
        self.RestoreDiffusionNodes()
        for k in self.nodeItemList.keys():
            item = self.nodeItemList[k]
            item.setVisible(False)
        for k in self.edgeItemList.keys():
            item = self.edgeItemList[k]
            item.setVisible(False)
            self.checkBoxEdge.setChecked(False)
        for k in self.seedNodes:
            item = self.nodeItemList[k]
            item.setVisible(True)

    def ResetProb(self, pLeader, pNormal):
        self.label_pleader_value.setText(pLeader)
        self.horizontalSliderPleader.setValue(int(self.horizontalSliderPleader.maximum() * float(pLeader)))
        self.label_padopter_value.setText(pNormal)
        self.horizontalSliderPNormal.setValue(int(self.horizontalSliderPNormal.maximum() * float(pNormal)))

    def ActiveNodeCityDiffusion(self, node, fromNode, incrementValue):
        self.activedNodes += 1
        item = self.nodeItemList[node]
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.ActivedNodeBrushColor))
        item.setBrush(brush)
        item.setVisible(True)
        rect = item.rect()
        center = rect.center()
        (x, y) = self.nodesPosition[node]
        key = str.format("{0}_{1}", x, y)
        if key in self.postiveNodesDict.keys():
            scale = self.postiveNodesDict[key] + incrementValue
        else:
            scale = incrementValue
        self.postiveNodesDict[key] = scale
        rect.setHeight(GlobalParameters.ActiveNodeSize + scale * 0.2)
        rect.setWidth(GlobalParameters.ActiveNodeSize + scale * 0.2)
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
        key = str.format("{0}_{1}", fromNode, node)
        if key in self.lineFromTo.keys():
            r = self.lineFromTo[key]
            pen = QtGui.QPen(QtGui.QColor("Blue"))
            pen.setWidth(r[0] + 1)
            line.setPen(pen)
            self.GraphicsScene.addItem(line)
            self.GraphicsScene.removeItem(r[1])
            self.lineFromTo[key] = [r[0] + 1, line]
        else:
            self.lineFromTo[key] = [1, line]
            self.GraphicsScene.addItem(line)


    def ActiveNodeDiffusion(self, nodeIndex, increment, p):
        self.activedNodes += 1
        item = self.nodeItemList[nodeIndex]
        brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.ActivedNodeBrushColor))
        item.setBrush(brush)
        item.setVisible(True)
        # rect = item.rect()
        # center = rect.center()
        # (x, y) = self.nodesPosition[nodeIndex]
        # key = str.format("{0}_{1}", x, y)
        # if key in self.postiveNodesDict.keys():
        #     scale = self.postiveNodesDict[key] + increment
        # else:
        #     scale = increment
        # self.postiveNodesDict[key] = scale
        # rect.setHeight(GlobalParameters.ActiveNodeSize + scale * 0.2)
        # rect.setWidth(GlobalParameters.ActiveNodeSize + scale * 0.2)
        # rect.moveCenter(center)
        # item.setRect(rect)
        #
        # if p != -1:
        #
        #     rect1 = self.nodeItemList[p].rect()
        #     rect2 = self.nodeItemList[nodeIndex].rect()
        #
        #     line = QtGui.QGraphicsLineItem(
        #         rect1.x() + rect1.height() * 0.5,
        #         rect1.y() + rect1.height() * 0.5,
        #         rect2.x() + rect2.height() * 0.5,
        #         rect2.y() + rect2.height() * 0.5
        #     )
        #     key = str.format("{0}_{1}", p, nodeIndex)
        #     if key in self.lineFromTo.keys():
        #         r = self.lineFromTo[key]
        #         pen = QtGui.QPen(QtGui.QColor("Blue"))
        #         pen.setWidth(r[0] + 1)
        #         line.setPen(pen)
        #         self.GraphicsScene.addItem(line)
        #         self.GraphicsScene.removeItem(r[1])
        #         self.lineFromTo[key] = [r[0] + 1, line]
        #     else:
        #         self.lineFromTo[key] = [1, line]
        #         self.GraphicsScene.addItem(line)

    def FinishedDiffusion(self):
        Utility.SystemWarning("Information diffusion is finished!")
        # self.textInfoWidget.setPlainText("")
        self.pushButtonGenerateSeedNodes.setEnabled(True)
        if not self.aggregate:
            self.ShowAllNodes()
        self.pushButtonDiffusion.setEnabled(True)
        self.pushButtonGenerateOpinionLeaders.setEnabled(True)

        currentPath = os.path.split(os.path.realpath(__file__))[0]
        filePath = currentPath + "//output//diffusion.txt"
        tag = True
        if not os.path.exists(filePath):
            tag = False

        model = ""
        opinionmethod = ""
        params = ""
        if self.groupBoxLTModel.isChecked():
            model = "LT"
            params = self.lineEditThreshold.text()
        if self.groupBoxICModel.isChecked():
            model = "IC"
            params = self.lineEditOpinionNodePopagate.text() + "_" + self.lineEditNormalNodePopagate.text()

        if self.radioButtonEachCommunity.isChecked():
            opinionmethod = "Community"
        else:
            opinionmethod = "Whole"

        f = open(filePath, "a")
        if not tag:
            f.write("#Seed Node,Algorithm, #Opinion Leaders, Scope, Model, Parameters, Influence size\n")
        f.write(str.format("{0},{1},{2},{3},{4},{5},{6}\n",
                           len(self.seedNodes),
                           self.comboBoxAlgorithmsforSeedNode.currentText(),
                           len(self.opinionLeaders),
                           opinionmethod,
                           model,
                           params,
                           self.activedNodes + len(self.seedNodes)
                           ))

    def ClickAddConnect(self):
        itemList = []
        for i in range(self.networkCount):
            itemList.append(str(i))
        if len(itemList) == 0:
            Utility.SystemWarning("There is no network to connecte!")
            return
        Utility.InitCombobox(self.comboBoxNetworkID, itemList)
        i = self.tableWidgetComplexLinks.rowCount()
        self.tableWidgetComplexLinks.insertRow(i)
        tempWidget = QtGui.QComboBox()
        Utility.InitCombobox(tempWidget, itemList)
        self.tableWidgetComplexLinks.setCellWidget(i, 0, tempWidget)
        tempWidget = QtGui.QComboBox()
        Utility.InitCombobox(tempWidget, itemList)
        self.tableWidgetComplexLinks.setCellWidget(i, 3, tempWidget)
        item = QtGui.QTableWidgetItem()
        item.setText(str(GlobalParameters.NumbertoConnected))
        self.tableWidgetComplexLinks.setItem(i, 1, item)
        item = QtGui.QTableWidgetItem()
        item.setText(str(GlobalParameters.NumbertoConnected))
        self.tableWidgetComplexLinks.setItem(i, 4, item)
        tempWidget = QtGui.QComboBox()
        Utility.InitCombobox(tempWidget, GlobalParameters.RuleforSelectConnectNode)
        self.tableWidgetComplexLinks.setCellWidget(i, 2, tempWidget)
        tempWidget = QtGui.QComboBox()
        Utility.InitCombobox(tempWidget, GlobalParameters.RuleforSelectConnectNode)
        self.tableWidgetComplexLinks.setCellWidget(i, 5, tempWidget)

    def ClickRemoveConnect(self):
        index = self.tableWidgetComplexLinks.currentRow()
        if index == -1:
            Utility.SystemWarning("There is not data to delete!")
            return
        else:
            if not Utility.SystemTipYesNO("Are you sure you want to delete row " + str(index + 1)):
                return
        self.tableWidgetComplexLinks.removeRow(index)

    # for select combobox
    def SelectedChangeComboBoxNetworkType(self):
        index = self.comboBoxNetworkType.currentIndex()
        if index == 0:
            return
        for i in range(self.tableWidgetParameter.rowCount()):
            self.tableWidgetParameter.removeRow(0)
        params = GlobalParameters.NetworkTypeParams[index - 1]
        for i in range(len(params)):
            self.tableWidgetParameter.insertRow(i)
            item = QtGui.QTableWidgetItem()
            item.setText(params[i])
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidgetParameter.setItem(i, 0, item)
            item = QtGui.QTableWidgetItem()
            if params[i] == "Rnd":
                item.setText("Random number")
                item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidgetParameter.setItem(i, 1, item)

    def SelChangeCombNetworkTypeforComplex(self):
        index = self.comboBoxNetworkTypeforComplex.currentIndex()
        if index == 0:
            return
        for i in range(self.tableWidgetParameterComplexParameters.rowCount()):
            self.tableWidgetParameterComplexParameters.removeRow(0)
        params = GlobalParameters.NetworkTypeParams[index - 1]
        for i in range(len(params)):
            self.tableWidgetParameterComplexParameters.insertRow(i)
            item = QtGui.QTableWidgetItem()
            item.setText(params[i])
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidgetParameterComplexParameters.setItem(i, 0, item)
            item = QtGui.QTableWidgetItem()
            if params[i] == "Rnd":
                item.setText("Rnd")
                item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidgetParameterComplexParameters.setItem(i, 1, item)

    # for checkbox
    def CheckLTCheckBox(self):
        if self.groupBoxLTModel.isChecked():
            self.groupBoxICModel.setChecked(False)

    def CheckICCheckBox(self):
        if self.groupBoxICModel.isChecked():
            self.groupBoxLTModel.setChecked(False)

    def CheckShowEdge(self):
        tag = self.checkBoxEdge.isChecked()
        for key in self.edgeItemList:
            self.edgeItemList[key].setVisible(tag)

    def CheckBaseMap(self):
        if not self.groupBoxBaseMap.isChecked():
            self.bbox = None
            self.baseMap = False
            self.lineEditPathName.setText("")
            self.comboBoxBaseMapLayers.clear()
            for key in self.polygonItemList.keys():
                self.GraphicsScene.removeItem(self.polygonItemList[key])

    def AddItemToScene(self, item, type, strId):
        if type == "P":
            self.nodeItemList[int(str(strId))] = item
        else:
            self.edgeItemList[strId] = item
            if not self.checkBoxEdge.isChecked():
                item.setVisible(False)
            else:
                item.setVisible(True)

        self.GraphicsScene.addItem(item)

    def DrawTimeRegPlot(self, timeNNRList):
        win = PlotWindow.PlotWindow("Time Nearest Neighbor Ratio Curve Regression")
        win.show()
        win.y = timeNNRList
        win.DrawPlot2()

    def FinshedRun(self, message):
        self.Drawing = False
        Utility.SystemWarning(message, "Congratulations")

    # Draw
    def DrawGraph(self, graph, position=None):
        # Area used: self.GraphicsScene.width(); self.GraphicsScene.height()
        if not self.groupBoxBaseMap.isChecked():
            self.GraphicsScene.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("whitesmoke")))
        self.Drawing = True
        self.getThread = PrepareDrawThread.PrepareDrawThread(graph, self, self.bbox, position)
        self.connect(self.getThread, QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"),
                     self.AddItemToScene)
        self.connect(self.getThread, QtCore.SIGNAL("FinshedRun(QString)"), self.FinshedRun)
        self.getThread.start()

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
            # print variable, len(variable)
            variables[variable] = [record[varNames.index(variable)] for record in t]
        Utility.InitCombobox(self.comboBoxBaseMapLayers, varNames)
        if len(varNames) > 0:
            self.comboBoxBaseMapLayers.setCurrentIndex(1)

        self.dbfdata = variables

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

    def LoadPointFromCSV(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self, "Load Point file", "", "Point file (*.csv)")
        if filePath == "":
            return
        self.pointFile = str(filePath)

        if self.bbox is None:
            Utility.SystemWarning("Please add a base map before demonstrating diffusion on real network.")
            return

        self.NNRThread = ReadCSV.ReadCSV(self.pointFile, 3600, self.bbox, self.GraphicsScene)
        self.connect(self.NNRThread, QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"),
                     self.AddItemToScene)
        win = PlotWindow.PlotWindow("Nearest Neighbor Ratio Curve Regression")
        self.connect(self.NNRThread, QtCore.SIGNAL("Regression(QString)"),
                     win.DrawPlot)
        self.connect(self.NNRThread, QtCore.SIGNAL("DrawTimeRegPlot(PyQt_PyObject)"),
                     self.DrawTimeRegPlot)
        self.connect(self.NNRThread, QtCore.SIGNAL("FinshedRun(QString)"), self.FinshedRun)
        win.show()

        self.NNRThread.start()

    def DrawRegression(self, float):
        pass
        # self.nodeItemList[int(str(strId))] = item
        # self.GraphicsScene.addItem(item)

    def PredictDiffusion(self):
        if len(
                GlobalParameters.RegressionCoefficients) == 0 or GlobalParameters.RegressionArea == 0 or GlobalParameters.RegressiontotalT == 0:
            Utility.SystemWarning("There is no regression curve for simulation!")
            return
        self.PrectThread = SpatialPredict.SpatialPredict(self.pointFile, self.bbox, 0.01, 0.01, 10, self.GraphicsScene)
        self.connect(self.PrectThread, QtCore.SIGNAL("AddItemToScene(PyQt_PyObject, QString, QString)"),
                     self.AddItemToScene)
        self.connect(self.PrectThread, QtCore.SIGNAL("FinshedRun(QString)"), self.FinshedRun)
        self.PrectThread.start()

        self.GraphicsScene.addItem()

    def ClickFindParameters(self):
        if self.graph is None:
            Utility.SystemWarning("There is no network. Please load network from CSV file.")
            return
        seedNodesText = str(self.textEditSeedNodes.toPlainText())
        strlist = seedNodesText.split(";")

        if seedNodesText == "":
            Utility.SystemWarning("Please input early adopters manually!")
        self.seedNodes.clear()
        seedNodesLabel = strlist[0].split(",")
        for i in range(len(seedNodesLabel)):
            self.seedNodes.add(self.graphLabelToId[seedNodesLabel[i]])
        self.ShowSeedNodes()
        centrality = Centrality.Centrality(self.graph)
        opinionLeader = centrality.GetMaxKDegree(int(math.floor(len(self.graphLabelToId) / 10)))

        self.diffusionThread = Diffusion.Diffusion(self.graph, self.seedNodes, opinionLeader, "FP")
        self.diffusionThread.acturalAdopterSize = int(strlist[1])

        self.connect(self.diffusionThread, QtCore.SIGNAL("ActiveNodeDiffusion(int, int)"),
                     self.ActiveNodeDiffusion)
        self.connect(self.diffusionThread, QtCore.SIGNAL("FinishedDiffusion()"), self.FinishedDiffusion)
        self.connect(self.diffusionThread, QtCore.SIGNAL("BeginDiffusion()"), self.BeginDiffusion)
        self.connect(self.diffusionThread, QtCore.SIGNAL("ResetProb(QString, QString)"), self.ResetProb)
        self.connect(self.diffusionThread, QtCore.SIGNAL("ShowAllNodes()"), self.ShowAllNodes)
        self.pushButtonGenerateSeedNodes.setEnabled(False)
        self.pushButtonDiffusion.setEnabled(False)
        self.BeginDiffusion()
        # time.sleep(0.5)

        self.diffusionThread.start()

    def ClickOpenParameterFile(self):
        filePath = QtGui.QFileDialog.getOpenFileName(None, "Load Parameters", "",
                                                     "Parameter file (*.txt)")
        if filePath == "":
            return
        self.lineEditParameterFile.setText(filePath)

    def DrawErrorCounter(self):
        import numpy
        from matplotlib import pyplot
        from matplotlib.mlab import griddata
        from numpy.random import seed

        if str(self.lineEditParameterFile.text()) != "":
            filePath = str(self.lineEditParameterFile.text())
        else:
            Utility.SystemWarning("Please select a file!")
            return
        data = numpy.loadtxt(filePath)
        seed(0)

        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 3]
        # define grid.
        xi = numpy.linspace(x.min(), x.max(), 100)
        yi = numpy.linspace(y.min(), y.max(), 100)
        # grid the data.
        zi = griddata(x, y, z, xi, yi, interp='linear')
        # contour the gridded data, plotting dots at the nonuniform data points.
        cs = pyplot.contour(xi, yi, zi, 15, linewidths=0.01, colors='k')
        cs = pyplot.contourf(xi, yi, zi, 15, cmap=pyplot.cm.rainbow,
                             vmax=abs(zi).max(), vmin=-abs(zi).max())
        pyplot.colorbar()  # draw colorbar
        # plot data points.
        # plt.scatter(x, y, marker='o', c='b', s=5, zorder=10)
        # plt.xlim(0.2, 0.3)
        # plt.ylim(0, 0.3)
        pyplot.xlabel('$p_o$$_p$')
        pyplot.ylabel('$p_n$')
        pyplot.axis([x.min(), x.max(), y.min(), y.max()])
        title = str(self.lineEditMapTitle.text())
        if title == "":
            title = "Error Counter Map"
        pyplot.title(title)

        # zero_data = np.loadtxt('zero4.txt')
        # x1 = zero_data[:, 0]
        # y1 = zero_data[:, 1]
        #
        # fit = np.polyfit(x1,y1,1)
        # fit_fn = np.poly1d(fit)
        #
        # plt.plot(x1,y1,'bo', ms=4.0, label='optimal parameters location')
        # #plt.plot(x1,  fit_fn(x1), '--k', label='linear model fitting')

        pyplot.legend(loc='upper left', shadow=False, fontsize='medium')

        pyplot.show()

    ###Centrality###
    def InitCentralityForm(self):
        self.centralityForm = QtGui.QMainWindow()
        self.centralityUI = CharacteristicForm()
        self.centralityUI.setupUi(self.centralityForm)

        self.cityDiffusionForm = QtGui.QMainWindow()
        self.cityDiffuiosnUI = CityDiffusionForm.CityDiffusionForm()
        self.cityDiffuiosnUI.setupUi(self.cityDiffusionForm)


    def ClickBetweennessCentrality(self):
        if self.graph is None:
            Utility.SystemWarning("There is no network!")
            return
        centrality = Centrality.Centrality(self.graph)
        listValue = centrality.BetweennessCentrality()
        self.centralityUI.SetOutput(listValue)
        self.centralityForm.setWindowTitle("Betweenness Centrality")
        self.centralityForm.show()

    def ClickDegreeCentrality(self):
        if self.graph is None:
            Utility.SystemWarning("There is no network!")
            return
        centrality = Centrality.Centrality(self.graph)
        listValue = centrality.DegreeCentrality()
        self.centralityUI.SetOutput(listValue)
        self.centralityForm.setWindowTitle("Degree Centrality")
        self.centralityForm.show()

    def ClickClosenessCentrality(self):
        if self.graph is None:
            Utility.SystemWarning("There is no network!")
            return
        centrality = Centrality.Centrality(self.graph)
        listValue = centrality.ClosenessCentrality()
        self.centralityUI.SetOutput(listValue)
        self.centralityForm.setWindowTitle("Closeness Centrality")
        self.centralityForm.show()

    def ClickEigenvectorCentrality(self):
        if self.graph is None:
            Utility.SystemWarning("There is no network!")
            return
        centrality = Centrality.Centrality(self.graph)
        listValue = centrality.EigenvectorCentrality()
        self.centralityUI.SetOutput(listValue)
        self.centralityForm.setWindowTitle("Eigenvector Centrality")
        self.centralityForm.show()

    def ClickOpenWeightMatrix(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self, "Load Weight Matrix", "",
                                                     "Weight Matrix (*.txt)")
        if filePath == "":
            return
        self.lineEditWeightMatrix.setText(filePath)
        try:
            f = open(filePath)
        except:
            f = open(filePath)
            return False

    def DoMenuExtractRetweetNetwork(self):
        fileName = QtGui.QFileDialog.getOpenFileNameAndFilter(self, 'Open a CSV File', '*.csv')
        #fileName = open(name, 'w')

        data = []  # network data to write

        with open(fileName[0], "r") as fp:
            reader = csv.reader(fp, dialect=csv.excel)
            for rows in reader:
                data.append(rows)

        USER_NAME_Index = data[0].index("USER_NAME")
        CREATE_TIME_Index = data[0].index("CREATE_TIME")
        TEXT_Index = data[0].index("TEXT")

        def extract_network(text):
            if text.startswith("RT"):
                return text.split(" ")[1][1:]
            else:
                return ""

        # Open File and create list of the target column
        result = []
        for i in range(1,len(data)):
            rows = data[i]
            target_col = []
            target_col.append(rows[USER_NAME_Index])
            retweetfrom = extract_network(rows[TEXT_Index])
            adpotTime = rows[CREATE_TIME_Index]
            target_col.append(retweetfrom)
            target_col.append(adpotTime)

            result.append(target_col)

            # write desired columns to new csv file
        name2 = QtGui.QFileDialog.getSaveFileNameAndFilter(self, 'Save to a CSV File', '*.csv')
            #fileName2 = open(name, 'w')
        with open(name2[0], 'wb') as test:
            writer = csv.writer(test, delimiter=',')
            writer.writerows([["USER_NAME", "RETWEET_FROM", "RETWEET_TIME"]])
            writer.writerows(result)

    def DoMenuExtractMentionNetwork(self):
        fileName = QtGui.QFileDialog.getOpenFileNameAndFilter(self, 'Open a CSV File', '*.csv')
        #fileName = open(name, 'w')

        data = []  # network data to write

        with open(fileName[0], "r") as fp:
            reader = csv.reader(fp, dialect=csv.excel)
            for rows in reader:
                data.append(rows)

        USER_NAME_Index = data[0].index("USER_NAME")
        CREATE_TIME_Index = data[0].index("CREATE_TIME")
        TEXT_Index = data[0].index("TEXT")

        def extract_network(text):
            words = text.split(" ")
            mentionUsers = []
            for i in range(len(words)):
                if words[i].startswith("@"):
                    mentionUsers.append(words[i][1:])
            return mentionUsers

        # Open File and create list of the target column
        result = []
        for i in range(1,len(data)):
            rows = data[i]
            target_col = []
            target_col.append(rows[USER_NAME_Index])
            mentionUsers = extract_network(rows[TEXT_Index])
            friends = []

            mentionTime = rows[CREATE_TIME_Index]
            target_col.append(mentionUsers)
            target_col.append(mentionTime)

            result.append(target_col)

            # write desired columns to new csv file
        name2 = QtGui.QFileDialog.getSaveFileNameAndFilter(self, 'Save to a CSV File', '*.csv')
            #fileName2 = open(name, 'w')
        with open(name2[0], 'wb') as test:
            writer = csv.writer(test, delimiter=',')
            writer.writerows([["USER_NAME", "MENTION_USERS", "MENTION_TIME"]])
            writer.writerows(result)
