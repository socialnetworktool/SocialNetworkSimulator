__author__ = 'Zhu Lin'

import snap
from prettytable import PrettyTable

class netBasicDescription:
    def __init__(self,_graph):
        self.graph=_graph
        self.SeedNodes=set()
        self.opinionLeaders=set()

# output the basic description of the network
    def GetBasic(self):
        loopCount=snap.CntSelfEdges(self.graph)
        eMax=self.graph.GetNodes()*(self.graph.GetNodes()-1)/2.0
        networkDensity=round(self.graph.GetEdges()/eMax,3)
        networkAverageDegree=round(2*self.graph.GetEdges()/self.graph.GetNodes(),3)
        table0=PrettyTable(['Nodes','Edges Sum','Loop','Density','Average Degree'])
        table0.add_row([self.graph.GetNodes(),self.graph.GetEdges(),loopCount,networkDensity,networkAverageDegree])
        print table0
        print ""

        table1=PrettyTable(['Nodes','Out Degree','In Degree'])
        if self.graph.Nodes()==0:
            print 'The network is empty'
        else:
            for NI in self.graph.Nodes():
                table1.add_row([NI.GetId(),NI.GetOutDeg(),NI.GetInDeg()])


        print table1
