__author__ = 'Lanxue Dang'

import snap
import random
import time
import os
import math
from PyQt4 import QtCore
import gc

class Diffusion(QtCore.QThread):
    def __init__(self, _graph, S, leader, type, IC_Pb_o = 0.2, IC_Pb_n = 0.1):
        QtCore.QThread.__init__(self)
        self.graph = _graph
        self.seed_nodes = S
        self.Opinion_leader = leader
        self.DiffusionModel = type
        self.active_nodes = set()
        self.node_to_active = set()
        self.buv = {}
        self.thieta_v = {}
        self.IC_Pb_o = IC_Pb_o
        self.IC_Pb_n = IC_Pb_n
        self.threshold = -1
        self.thieta_v.clear()

        self.demon = 1

        self.acturalAdopterSize = 0

        for NI in self.graph.Nodes():
            self.thieta_v[NI.GetId()] = random.uniform(0, 1)
        self._uv = {}
        for NI in self.graph.Nodes():
            total = 0
            for nbr in NI.GetInEdges():
                key = str(nbr) + "_" + str(NI.GetId())
                self._uv[key] = 1.0 #random.uniform(0, 1)
                total += self._uv[key]
            if total > 1:
                for nbr in NI.GetInEdges():
                    key = str(nbr) + "_" + str(NI.GetId())
                    self._uv[key] /= total

    def __del__(self):
        self.wait()

    def SetLTThreshold(self, threshold):
        self.threshold = threshold

    def run(self):
        if self.DiffusionModel == "IC":
            self.IC()
        elif self.DiffusionModel == "LT":
            self.LT()
        elif self.DiffusionModel == "FP":
            self.FindParameter()
        self.emit(QtCore.SIGNAL("FinishedDiffusion()"))

    def __LT_UND_Init(self):
        self.active_nodes.clear()
        self.node_to_active.clear()
        self.buv.clear()
        for node in self.seed_nodes:
            self.__LT_Active_v(node)

    def __LT_Active_v(self, v):
        self.active_nodes.add(v)
        for nbr in self.graph.GetNI(v).GetOutEdges():
            if nbr not in self.active_nodes:
                key = str(v) + "_" + str(nbr)
                if self.buv.has_key(nbr):
                    self.buv[nbr] += self._uv[key]
                else:
                    self.buv[nbr] = self._uv[key]
                if nbr not in self.node_to_active:
                    self.node_to_active.add(nbr)
    def LT(self):
        self.__LT_UND_Init()
        while len(self.node_to_active) > 0:
            v = self.node_to_active.pop()
            t = self.thieta_v[v]
            if self.threshold >= 0:
                t = self.threshold
            if self.buv[v] >= t:
                self.__LT_Active_v(v)
                # send signal to change color
                self.Render(v)
                time.sleep(0.1)
        return self.active_nodes


    def __IC_Active_Neighbor(self, v, node_to_active, activeFrom):
        # random select pb nodes from neighbors
        # if already in: pass; else: active, add it to actived_node
        if v in self.Opinion_leader:
            pb = self.IC_Pb_o
        else:
            pb = self.IC_Pb_n
        nbrs = self.graph.GetNI(v).GetOutEdges()
        lstnbrs = []
        for NI in nbrs:
            lstnbrs.append(NI)
        #k = int(self.pb_IC * len(lstnbrs))
        s = []

        for i in range(len(lstnbrs)):
            if random.Random().uniform(0,1) <= pb:
                s.append(lstnbrs[i])
        #random.Random().sample(lstnbrs, k)
        for i in range(len(s)):
            if s[i] not in self.active_nodes:
                activeFrom[s[i]] = v
                node_to_active.add(s[i])
    def IC(self):
        activeFrom = {}
        self.active_nodes.clear()
        node_to_active = set(self.seed_nodes.copy())
        while len(node_to_active) > 0:
            v = node_to_active.pop() # v = [CurrentV, parent of V]
            self.active_nodes.add(v)
            print(len(self.active_nodes))
            if v not in self.seed_nodes:
                if self.demon == 1:
                    p = -1
                    if v in activeFrom.keys():
                        p = activeFrom[v]
                    self.Render(v, 1, p)
                    time.sleep(0.01)
            self.__IC_Active_Neighbor(v, node_to_active, activeFrom)
        return self.active_nodes

    def __FP_Active_Neighbor(self, v, node_to_active):
        # random select pb nodes from neighbors
        # if already in: pass; else: active, add it to actived_node
        if v in self.Opinion_leader:
            pb = self.IC_Pb_o
        else:
            pb = self.IC_Pb_n
        nbrs = self.graph.GetNI(v).GetOutEdges()
        lstnbrs = []
        for NI in nbrs:
            #print NI
            lstnbrs.append(NI)
        #k = int(self.pb_IC * len(lstnbrs))
        s = []

        for i in range(len(lstnbrs)):
            adoptedLeader = []
            adoptedNormal = []
            inDegree = self.graph.GetNI(lstnbrs[i]).GetInDeg()
            #print "INDegree", inDegree
            for j in range(inDegree):
                NI = self.graph.GetNI(lstnbrs[i]).GetInNId(j)
                #print "NI", NI
                if NI in self.active_nodes:
                    if NI in self.Opinion_leader:
                        adoptedLeader.append(NI)
                    else:
                        adoptedNormal.append(NI)
            # outDegree = self.graph.GetNI(lstnbrs[i]).GetOutDeg()
            # for j in range(outDegree):
            #     NI = self.graph.GetNI(lstnbrs[i]).GetOutNId(j)
            #     if NI in self.active_nodes:
            #         if NI in self.Opinion_leader:
            #             adoptedLeader.append(NI)
            #         else:
            #             adoptedNormal.append(NI)
            if random.Random().uniform(0,1) < (len(adoptedLeader) * self.IC_Pb_o + len(adoptedNormal) * self.IC_Pb_n)/(len(adoptedLeader) + len(adoptedNormal)):
                s.append(lstnbrs[i])
            #if random.Random().uniform(0,1) <= pb:
                #s.append(lstnbrs[i])
        #random.Random().sample(lstnbrs, k)
        for i in range(len(s)):
            if s[i] not in self.active_nodes:
                node_to_active.add(s[i])

    def FP(self):
        self.active_nodes.clear()
        node_to_active = set(self.seed_nodes.copy())
        while len(node_to_active) > 0:
            v = node_to_active.pop()
            self.active_nodes.add(v)
            #print(len(self.active_nodes))
            if v not in self.seed_nodes:
                if self.demon == 1:
                    self.Render(v)
                    time.sleep(0.000001)
            self.__FP_Active_Neighbor(v, node_to_active)
        del node_to_active
        gc.collect()
        return self.active_nodes

    def Render(self, node, increment=1, p=-1):
        self.emit(QtCore.SIGNAL("ActiveNodeDiffusion(int, int, int)"), node, increment, p)

    def FindParameter(self):
        #self.demon = 0
        filePath = "parameters\\paramter"
        i = 1
        while os.path.exists(filePath + str(i) + ".txt"):
            i = i + 1
        f = open(filePath + str(i) + ".txt", "w")

        probOpinion = 0.2
        probNormal = 0
        increment = 0.001
        adopterSize = 0
        loops = 1
        # findOpinionLeader
        while probOpinion < 0.3:
            while probNormal < probOpinion:
                for k in range(loops):
                    self.IC_Pb_o = probOpinion
                    self.IC_Pb_n = probNormal
                    self.emit(QtCore.SIGNAL("ResetProb(QString, QString)"), str(probOpinion), str(probNormal))
                    self.emit(QtCore.SIGNAL("BeginDiffusion()"))
                    adopterSize += len(self.FP())
                    self.emit(QtCore.SIGNAL("ShowAllNodes()"))
                    #time.sleep(0.01)
                    print "Diffusion:", len(self.active_nodes)

                f.write(str(probOpinion) + "\t" + str(probNormal) + "\t" + str(adopterSize/(loops*1.0)) + "\t" + str(math.fabs((self.acturalAdopterSize-adopterSize/(loops*1.0))/self.acturalAdopterSize)) + "\n")
                adopterSize = 0
                probNormal += increment
            probNormal = 0
            probOpinion += increment
        f.close()
        self.demon = 0

    # def GroupDiffusion(self, graph, currentValue, weightMatrix, speed):
    #     for i in range(len(speed)):
    #         incrementMatrix = [[0] * graph.GetNodes()] * graph.GetNodes()
    #         incrementValue = {}
    #         for currentNode in graph.Nodes():
    #             incrementValue[currentNode] = 0
    #             for otherNode in graph.Nodes():
    #                 incrementMatrix[currentNode][otherNode] = currentValue[otherNode] * weightMatrix[currentValue][otherNode] * speed[i]
    #                 incrementValue[currentNode] += incrementMatrix[currentNode][otherNode]
    #
    #         for node in graph.Nodes():
    #             currentValue[node] += incrementValue[node]
    #
    #













