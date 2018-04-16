__author__ = 'Lanxue Dang'

import random
import time
import os
import math
from PyQt4 import QtCore
import gc
import Utility

class CityDiffusion(QtCore.QThread):
    def __init__(self, _graph, _seed_nodes, _weightMatix, _speed, _step, _position, _emergencyIndexType, _decayedParameters):
        QtCore.QThread.__init__(self)
        self.graph = _graph
        self.seed_nodes = _seed_nodes
        self.originalWeightMatrix = _weightMatix
        self.weightMatrix = []
        self.speed = _speed
        self.step = _step
        self.nodesPostion = _position #latitude, longtitude
        self.emergencyIndexType = _emergencyIndexType
        self.decayedParameters = _decayedParameters
        self.demon = 1
        self.sortedWeight = {}
        self.SortMatrix()

    def __del__(self):
        self.wait()

    def run(self):
        #print "RUN"
        #self.CityDiffusion(self.graph, self.currentStatus, self.weightMatrix, self.speed, self.step)

        self.CityICByEmergencyIndex()
        self.emit(QtCore.SIGNAL("FinishedDiffusion()"))

    def GetSortedID(self, lstValue):
        count = len(lstValue)
        # print listdegree
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
                    #print "P Value:", p
                    self.weightMatrix[i].append(self.originalWeightMatrix[i][j] * pow(self.decayedParameters[1], p))

        #self.weightMatrix = self.originalWeightMatrix
        count = len(self.weightMatrix)
        for i in range(count):
            self.sortedWeight[i] = self.GetSortedID(self.weightMatrix[i])


    def CityICByEmergencyIndex(self):
        currentStep = 0
        activeFrom = {}

        node_to_active = {}
        node_to_active[currentStep] = set(self.seed_nodes.copy())
        while currentStep <= self.step:
            #print "CURRENT, TOACTIVE:", currentStep, node_to_active[currentStep]
            if currentStep not in node_to_active.keys():
                break
            while len(node_to_active[currentStep]) > 0:
                v = node_to_active[currentStep].pop() # v = [CurrentV, parent of V]

                #self.active_nodes.add(v)
                #print(len(self.active_nodes))
                if v not in self.seed_nodes:
                    if self.demon == 1:
                        p = -1
                        if v in activeFrom.keys():
                            p = activeFrom[v]
                        self.Render(v, p, 1)
                        #print "Render:", currentStep, v, p
                        time.sleep(0.01)
                else:
                    #print "Render:", currentStep, v, v
                    self.Render(v, v, 1)
                if currentStep + 1 <= self.step:
                    self.__IC_Active_Neighbor(v, node_to_active, activeFrom, currentStep + 1)
            currentStep += 1

    def __IC_Active_Neighbor(self, v, node_to_active, activeFrom, currentStep):
        # random select pb nodes from neighbors
        # if already in: pass; else: active, add it to actived_node
        # if v in self.Opinion_leader:
        #     pb = self.IC_Pb_o
        # else:
        #     pb = self.IC_Pb_n
        if currentStep not in node_to_active.keys():
            node_to_active[currentStep] = set()
        nbrs = self.graph.GetNI(v).GetOutEdges()
        lstnbrs = []
        for NI in nbrs:
            lstnbrs.append(NI)
        lstnbrs.append(v)
        #k = int(self.pb_IC * len(lstnbrs))

        print self.sortedWeight
        print v
        #if self.emergencyIndexType == "G":
        activeCount = int(math.ceil(len(self.sortedWeight[v]) * self.speed[currentStep -1]))



        for i in range(len(lstnbrs)):
            if lstnbrs[i] in self.sortedWeight[v][0:activeCount]:
            #if 1 - self.speed <= self.weightMatrix[v][lstnbrs[i]]:
                # print "WEIGHT", self.weightMatrix[lstnbrs[i]][v]
                # print lstnbrs[i], v
                #s.append(lstnbrs[i])
                activeFrom[lstnbrs[i]] = v
                #print "Add, CurrentStep:", currentStep, lstnbrs[i], v, self.weightMatrix[lstnbrs[i]][v]
                node_to_active[currentStep].add(lstnbrs[i])

    def Render(self, node, p=-1, increment=1):
        self.emit(QtCore.SIGNAL("ActiveNodeCityDiffusion(int, int, int)"), node, p, increment)

    #def CityLT(self):





