__author__ = 'Lanxue Dang'

import snap, random
import GlobalParameters


class Centrality:
    def __init__(self, _graph):
        self.graph = _graph
        self.seedNodes = set()
        self.opinionLeaders = set()

    def RandHeuristc(self, k):
        self.seedNodes.clear()
        nodes = []
        for NI in self.graph.Nodes():
            nodes.append(NI.GetId())
        if k < 0 or k > self.graph.GetNodes():
            return self.seedNodes
        else:
            random.Random().shuffle(nodes)
            self.seedNodes = set(random.Random().sample(nodes, k))
        return self.seedNodes

    def GetMaxK(self, lstValue, lstId, k):
        count = len(lstValue)
        # print listdegree
        if k < 0 or k > count:
            a = (k < 0)
            b = (k > count)
            print "a,b:", a, b
            print "K,COUNT:", k, count
            return self.seedNodes

        # nodes = range(0, count)
        for i in range(0, count):
            for j in range(i + 1, count):
                if lstValue[i] > lstValue[j]:
                    lstValue[i], lstValue[j] = lstValue[j], lstValue[i]
                    lstId[i], lstId[j] = lstId[j], lstId[i]

        self.seedNodes = set(lstId[count - k:count])
        return self.seedNodes

    def GetMaxKDegree(self, k):
        self.seedNodes.clear()
        resultInDegree = snap.TIntV()
        resultOutDegree = snap.TIntV()
        snap.GetDegSeqV(self.graph, resultInDegree, resultOutDegree)
        count = len(resultOutDegree)
        listDegree = []
        nodesId = []
        for i in range(count):
            listDegree.append(resultOutDegree[i])
            nodesId.append(i)

        # random.Random().shuffle(listDegree)
        return self.GetMaxK(listDegree, nodesId, k)

    def GetMaxKDegreeCentrality(self, k):
        lstDeg = []
        nodesId = []
        for NI in self.graph.Nodes():
            DegCentr = snap.GetDegreeCentr(self.graph, NI.GetId())
            nodesId.append(NI.GetId())
            lstDeg.append(DegCentr)
        print lstDeg, nodesId
        return self.GetMaxK(lstDeg, nodesId, k)

    def GetMaxKBetweennessCentrality(self, k):
        lstNodeBet = []
        nodesId = []

        Nodes = snap.TIntFltH()
        Edges = snap.TIntPrFltH()
        snap.GetBetweennessCentr(self.graph, Nodes, Edges, 1.0)
        for node in Nodes:
            nodesId.append(node)
            lstNodeBet.append(Nodes[node])
        return self.GetMaxK(lstNodeBet, nodesId, k)

    def GetMaxKClosenessCentrality(self, k):
        lstColseness = []
        nodesId = []
        for NI in self.graph.Nodes():
            closecenter = snap.GetClosenessCentr(self.graph, NI.GetId())
            nodesId.append(NI.GetId())
            lstColseness.append(closecenter)
        return self.GetMaxK(lstColseness, nodesId, k)

    def GetMaxKEigenvectorCentrality(self, k):
        lstEigenVector = []
        nodesId = []

        NIdEigenH = snap.TIntFltH()
        snap.GetEigenVectorCentr(self.graph, NIdEigenH)

        for i in NIdEigenH:
            nodesId.append(i)
            lstEigenVector.append(NIdEigenH[i])
        return self.GetMaxK(lstEigenVector, nodesId, k)

    def GetMaxKDegreeDiscount(self, k, p=0.1):
        self.seedNodes.clear()
        dictDv = {}
        dictDdv = {}
        dictTv = {}
        nodes = set()
        for NI in self.graph.Nodes():
            id = NI.GetId()
            dictDv[id] = NI.GetDeg()
            dictDdv[id] = dictDv[id]
            dictTv[id] = 0
            nodes.add(id)
        if len(nodes) < k:
            return self.seedNodes

        for i in range(k):
            max_ddv = -1
            u = None
            for j in nodes:
                if j not in self.seedNodes:
                    if dictDdv[j] > max_ddv:
                        u = j
                        max_ddv = dictDdv[j]
            if u is not None:
                self.seedNodes.add(u)
                nodes.remove(u)
                for v in self.graph.GetNI(u).GetOutEdges():
                    dictTv[v] += 1
                    dictDdv[v] = dictDv[v] - 2 * dictTv[v] - (dictDv[v] - dictTv[v]) * dictTv[v] * p
        return self.seedNodes

    def GetKNodesByAlgorithm(self, k, algorithm): #"Degree", "Betweenness", "Closeness", "Eigenvector", "Random"
        if algorithm == GlobalParameters.RuleforSelectConnectNode[0]:
            return self.GetMaxKDegree(k)
        elif algorithm == GlobalParameters.RuleforSelectConnectNode[1]:
            return self.GetMaxKBetweennessCentrality(k)
        elif algorithm == GlobalParameters.RuleforSelectConnectNode[2]:
            return self.GetMaxKClosenessCentrality(k)
        elif algorithm == GlobalParameters.RuleforSelectConnectNode[3]:
            return self.GetMaxKEigenvectorCentrality(k)
        elif algorithm == GlobalParameters.RuleforSelectConnectNode[4]:
            return self.RandHeuristc(k)
        else:
            return self.seedNodes

    def GetSeedNodes(self, k, algorithm):
        if algorithm == GlobalParameters.AlgrotihmsforSeedNodes[0]:
            return self.GetMaxKDegreeCentrality(k)
        elif algorithm == GlobalParameters.AlgrotihmsforSeedNodes[1]:
            return self.GetMaxKBetweennessCentrality(k)
        elif algorithm == GlobalParameters.AlgrotihmsforSeedNodes[2]:
            return self.GetMaxKClosenessCentrality(k)
        elif algorithm == GlobalParameters.AlgrotihmsforSeedNodes[3]:
            return self.GetMaxKEigenvectorCentrality(k)
        elif algorithm == GlobalParameters.AlgrotihmsforSeedNodes[4]:
            return self.RandHeuristc(k)
        else:
            return self.seedNodes

    def BetweennessCentrality(self):
        lstNodeBet = {}
        Nodes = snap.TIntFltH()
        Edges = snap.TIntPrFltH()
        snap.GetBetweennessCentr(self.graph, Nodes, Edges, 1.0)
        for node in Nodes:
            lstNodeBet[node] = Nodes[node]
        return lstNodeBet

    def DegreeCentrality(self):
        lstDeg = {}
        for NI in self.graph.Nodes():
            DegCentr = snap.GetDegreeCentr(self.graph, NI.GetId())
            lstDeg[NI.GetId()] = DegCentr
        return lstDeg

    def EigenvectorCentrality(self):
        lstEigenVector = {}

        NIdEigenH = snap.TIntFltH()
        snap.GetEigenVectorCentr(self.graph, NIdEigenH)

        for i in NIdEigenH:
            lstEigenVector[i] = NIdEigenH[i]
        return lstEigenVector

    def ClosenessCentrality(self):
        lstColseness = {}
        for NI in self.graph.Nodes():
            closecenter = snap.GetClosenessCentr(self.graph, NI.GetId())
            lstColseness[NI.GetId()] = closecenter
        return lstColseness

    def GetOpinionLeaders(self, method, proportion, communities):
        k = int(self.graph.GetNodes() * proportion)
        if method == "W": # whole network
            self.opinionLeaders = self.GetMaxKDegree(k)
        else: # method = "C": each community
            if not communities:
                return set()
            dictIMN = {}
            dictNodeCommunity = {}
            for i in range(len(communities)):
                dictIMN[i] = [int(len(communities[i]) * proportion), 0]
                for node in communities[i]:
                    dictNodeCommunity[node] = i

            # get whole sorted list
            lstDeg = []
            nodesId = []
            for NI in self.graph.Nodes():
                DegCentr = snap.GetDegreeCentr(self.graph, NI.GetId())
                nodesId.append(NI.GetId())
                lstDeg.append(DegCentr)

            count = len(lstDeg)
            # nodes = range(0, count)
            for i in range(0, count):
                for j in range(i + 1, count):
                    if lstDeg[i] > lstDeg[j]:
                        lstDeg[i], lstDeg[j] = lstDeg[j], lstDeg[i]
                        nodesId[i], nodesId[j] = nodesId[j], nodesId[i]
            print nodesId
            for i in range(count-1,0,-1):
                node = nodesId[i]
                communityindex = dictNodeCommunity[node]
                if dictIMN[communityindex][1] < dictIMN[communityindex][0]:
                    self.opinionLeaders.add(node)
                    dictIMN[communityindex][1] += 1
                if len(self.opinionLeaders) == k:
                    break
        return self.opinionLeaders






