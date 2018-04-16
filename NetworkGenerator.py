__author__ = 'Lanxue Dang'

import snap
import GlobalParameters
import Centrality
import Utility

class NetworkGenerator:
    # params[0] is network type
    # params[1] is the number of nodes
    def SimpleNetworkGenerator(self, params):
        #print params
        Rnd = snap.TRnd(1, 0)
        G = None
        try:
            if params[0] == GlobalParameters.NetworkType[0]:
                G = snap.GenSmallWorld(int(params[1]), int(params[2]), float(params[3]), Rnd)
            if params[0] == GlobalParameters.NetworkType[1]:
                G = snap.GenPrefAttach(int(params[1]), int(params[2]), Rnd)
            if params[0] == GlobalParameters.NetworkType[2]:
                G = snap.GenForestFire(int(params[1]), float(params[2]), float(params[3]))
            if params[0] == GlobalParameters.NetworkType[3]:
                G = snap.GenRndGnm(snap.PUNGraph, int(params[1]), int(params[2]), False, Rnd)
            if params[0] == GlobalParameters.NetworkType[4]:
                G = snap.GenCircle(snap.PUNGraph, int(params[1]), int(params[2]), False)
            if params[0] == GlobalParameters.NetworkType[5]:
                G = snap.GenFull(snap.PUNGraph, int(params[1]))
            return G
        except:
            return None

    def ComplexNetworkGenerator(self, paramList, connections):
        gList = []
        graphs = []
        for i in range(len(paramList)):
            if paramList[i] is not None:
                params = [paramList[i][0]]
                for j in range(len(paramList[i][2])):
                    params.append(paramList[i][2][j])
                gList.append(self.SimpleNetworkGenerator(params))
            else:
                return None, None
        graphs.append(gList[0])
        currentNumberofNodes = gList[0].GetNodes()
        for i in range(1, len(gList)):
            g = snap.TUNGraph.New()
            for Node in gList[i].Nodes():
                g.AddNode(Node.GetId() + currentNumberofNodes)
            for EI in gList[i].Edges():
                g.AddEdge(EI.GetSrcNId() + currentNumberofNodes, EI.GetDstNId() + currentNumberofNodes)
            graphs.append(g)
            currentNumberofNodes += g.GetNodes()
        G = snap.TUNGraph.New()
        for i in range(len(graphs)):
            for Node in graphs[i].Nodes():
                G.AddNode(Node.GetId())
            for EI in graphs[i].Edges():
                G.AddEdge(EI.GetSrcNId(), EI.GetDstNId())
        #print G.GetNodes(), G.GetEdges()
        G = self.ConnectGraphs(graphs, G, connections)
        #print G.GetNodes(), G.GetEdges()
        return G, graphs

    def GetCount(self, graph, num):
        nodeCount = graph.GetNodes()
        number = str(num)
        if number.find("%"):
            number = number.strip("%")
            if Utility.CheckParameter("(FLOAT2)", number):
                return int(float(number) * nodeCount / 100.0)
        else:
            if Utility.CheckParameter("(FLOAT2)", number):
                if number <= nodeCount:
                    return number
                else:
                    return nodeCount
    def ConnectGraphs(self, graphs, G, connectionList):
        # connection: graph from; the number of nodes; rule; ....
        for i in range(len(connectionList)):
            #print connectionList[i]
            connection = connectionList[i]
            centralityFrom = Centrality.Centrality(graphs[int(connection[0])]).GetKNodesByAlgorithm(self.GetCount(graphs[int(connection[0])],connection[1]), connection[2])
            centralityTo = Centrality.Centrality(graphs[int(connection[3])]).GetKNodesByAlgorithm(self.GetCount(graphs[int(connection[3])],connection[4]), connection[5])
            #print centralityFrom, centralityTo
            for src in centralityFrom:
                for dst in centralityTo:
                    G.AddEdge(src, dst)
        return G




