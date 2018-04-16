import PlotWindow

__author__ = 'Lanxue Dang'

import time
import math
from PyQt4 import QtCore
import Utility

class CityDiffusion(QtCore.QThread):
    def __init__(self, _graph, _seed_nodes, _weightMatix, _EmergencyIndex, _step, _coverage, _position, _emergencyIndexType, _decayedParameters):
        QtCore.QThread.__init__(self)
        self.graph = _graph
        self.seed_nodes = _seed_nodes
        self.originalWeightMatrix = _weightMatix
        self.weightMatrix = []
        self.emergencyIndex = _EmergencyIndex
        self.step = _step
        self.coverage = _coverage
        self.nodesPostion = _position #latitude, longtitude
        self.emergencyIndexType = _emergencyIndexType


        self.decayedParameters = _decayedParameters
        self.demon = 1
        self.sortedWeight = {}
        self.SortMatrix()
        self.activeNodes = set()
        self.resultFile = None
        self.stop = False
        self.lastStepRender = 0
        self.stepActiveNodes = {}

    def __del__(self):
        self.wait()

    def SimulatorParameter(self):
        strseedNode = ""
        for node in self.seed_nodes:
            strseedNode += str(node) + ","
        strseedNode = strseedNode.rstrip(",")
        #strParameters = str.format("\nSeed Nodes:{0};", strseedNode)
        #strParameters += str.format("#Step:{0};", str(self.step))
        #strParameters += str.format("#Percent of Coverage:{0};", str(self.coverage))
        strEmergencyIndex = ""
        for i in range(len(self.emergencyIndex)):
            strEmergencyIndex += str(self.emergencyIndex[i]) + ","
        strEmergencyIndex = strEmergencyIndex.rstrip(",")
        #strParameters += str.format("Emergency Index:{0};", strEmergencyIndex)
        strParameters = str.format("{0};", strEmergencyIndex)
        
        # add decayedParameters in to output:  #2/2/2018
        strParameters += str.format("{0};",self.decayedParameters)
        
        #strParameters += str.format("G/L:{0};", self.emergencyIndexType)

        return strParameters

    def run(self):
        self.resultFile = open("RenderNodeList_UshapeDistance.txt","a+")
        strResult = self.SimulatorParameter()
        self.CityICByEmergencyIndex()
        steps = len(self.stepActiveNodes)
        for i in range(steps):
            #strResult += str(len(self.stepActiveNodes[i])) + ";"
            strResult += str(len(self.stepActiveNodes[i])) + ","
            #print str(len(self.stepActiveNodes[i]))
            #print strResult
        #strResult = strResult.rstrip(";") + "\r\n"
        strResult = strResult.rstrip(",") + "\r\n"
        self.resultFile.write(strResult)
        self.resultFile.close()

        y = []

        for i in range(len(self.stepActiveNodes)):
            y.append(len(self.stepActiveNodes[i]))
        if self.step > 0:
            if len(y) < self.step + 1:
                for i in range(len(y), self.step + 1):
                    y.append(0)
            y = y[0:self.step + 1]

        stepActiveResult = ""
        for i in range(len(y)):
            stepActiveResult += str(y[i]) + "_"
        stepActiveResult = stepActiveResult.rstrip("_")
        self.emit(QtCore.SIGNAL("FinishedDiffusion(QString)"), stepActiveResult)


    def GetSortedID(self, lstValue):
        count = len(lstValue)
        lstId = []

        for i in range(count):
            lstId.append(i)

        for i in range(count-1, -1, -1):
            for j in range(i - 1, - 1, -1):
                if lstValue[i] > lstValue[j]:
                    lstValue[i], lstValue[j] = lstValue[j], lstValue[i]
                    lstId[i], lstId[j] = lstId[j], lstId[i]
        return lstId

    #each node has a sorted list to record its neighbors in term of weight
    def SortMatrix(self):
        self.weightMatrix = []
        for i in range(len(self.originalWeightMatrix)):
            self.weightMatrix.append([])
            for j in range(len(self.originalWeightMatrix[0])):
                if self.emergencyIndexType == "G":
                    self.weightMatrix[i].append(self.originalWeightMatrix[i][j])
                else:
                    lat1, long1 = self.nodesPostion[i]
                    lat2, long2 = self.nodesPostion[j]
                    distance = Utility.DistancePoints(lat1, lat2, long1, long2)
                    p = int(distance / self.decayedParameters[0])
                    self.weightMatrix[i].append(self.originalWeightMatrix[i][j] * pow((1.0 -self.decayedParameters[1]/100.0), p))

        count = len(self.weightMatrix)
        for i in range(count):
            self.sortedWeight[i] = self.GetSortedID(self.weightMatrix[i])


    def CityICByEmergencyIndex(self):
        currentStep = 0
        activeFrom = {}

        node_to_active = {}
        node_to_active[currentStep] = set(self.seed_nodes.copy())
        while not self.stop:
            if currentStep not in node_to_active.keys():
                break
            if self.step > 0 and currentStep > self.step:
                break
            while len(node_to_active[currentStep]) > 0:
                if self.stop:
                    break
                v = node_to_active[currentStep].pop() # v = [CurrentV, parent of V]

                #self.active_nodes.add(v)
                #print(len(self.active_nodes))
                # if v not in self.seed_nodes:
                #     if self.demon == 1:
                #         p = -1
                #         if v in activeFrom.keys():
                #             p = activeFrom[v]
                #
                #         if currentStep not in self.stepActiveNodes.keys():
                #             self.stepActiveNodes[currentStep] = []
                #         if v not in self.activeNodes:
                #             self.stepActiveNodes[currentStep].append(v)
                #         self.Render(v, p, 1)
                #
                #         time.sleep(0.4)
                # else:
                    #print "Render:", currentStep, v, v
                if v in self.seed_nodes:
                    if currentStep not in self.stepActiveNodes.keys():
                        self.stepActiveNodes[currentStep] = []
                    if v not in self.activeNodes:
                        self.stepActiveNodes[currentStep].append(v)
                    self.Render(v, v, 1)

                if (currentStep + 1 <= self.step and self.step > 0) or not self.stop:
                    self.__IC_Active_Neighbor(v, node_to_active, activeFrom, currentStep + 1)
            currentStep += 1
            if self.lastStepRender == len(self.activeNodes):
                self.stop = True
            else:
                self.lastStepRender = len(self.activeNodes)
            time.sleep(3)

    def __IC_Active_Neighbor(self, v, node_to_active, activeFrom, currentStep):

        if currentStep > self.step and self.step > 0:
            return
        if currentStep not in node_to_active.keys():
            node_to_active[currentStep] = set()
        currentEmergencyIndex = self.emergencyIndex[0]
        if self.step > 0:
            currentEmergencyIndex = self.emergencyIndex[currentStep - 1]
        activeCount = int(math.ceil(len(self.sortedWeight[v]) * currentEmergencyIndex))
        selectedNodes = self.sortedWeight[v][0:activeCount]
        for i in range(len(selectedNodes)):
            activeFrom[selectedNodes[i]] = v

            if self.coverage > 0 and (len(self.activeNodes) * 1.0 / self.graph.GetNodes()) * 100.0 >= self.coverage:
                self.stop = True
                return

            if currentStep not in self.stepActiveNodes.keys():
                self.stepActiveNodes[currentStep] = []
            if selectedNodes[i] not in self.activeNodes:
                self.stepActiveNodes[currentStep].append(selectedNodes[i])

            self.Render(selectedNodes[i], v, 1)
            node_to_active[currentStep].add(selectedNodes[i])


    def Render(self, node, p=-1, increment=1):
        if node not in self.activeNodes:
            # self.resultFile.write(str.format("{0};", node))
            self.activeNodes.add(node)
            if self.coverage > 0 and (len(self.activeNodes) * 1.0 / self.graph.GetNodes()) * 100.0 >= self.coverage:
                self.stop = True

        self.emit(QtCore.SIGNAL("ActiveNodeCityDiffusion(int, int, int)"), node, p, increment)






