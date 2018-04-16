CITY_X_INDEX = 3
CITY_Y_INDEX = 4

def SaveGraph(graph, path, MADict):
    a = open(path, "w")
    nNodes = graph.GetNodes()
    nEdges = graph.GetEdges()
    seqences = []
    seqences.append(str.format("Nodes#{0}#Edges#{1}\n", nNodes, nEdges))
    for node in graph.Nodes():
        seqences.append(str.format("{0}#{1}#{2}\n", node.GetId(), MADict[str(node.GetId())][0], MADict[str(node.GetId())][1]))
    for EI in graph.Edges():
        seqences.append(str.format("{0},{1}\n", EI.GetSrcNId(), EI.GetDstNId()))
    a.writelines(seqences)
    a.close()

import snap
import csv
def ReadData(filepath):
    data = []
    with open(filepath, "r") as fp:
        reader = csv.reader(fp, dialect=csv.excel)
        for rows in reader:
            data.append(rows)
    return data

path = "C:\\Users\\Zhuo\\Desktop\\Winter_job\\Twitter-Charlottesville-Search-Data-20171206T021003Z-001\\Twitter-Charlottesville-Search-Data\\"

MAData = ReadData(path + "26-city_centroid_radius.csv")
MADict = {}
for i in range(1, len(MAData)):
    print type(MAData[i][0]), [MAData[i][CITY_X_INDEX], MAData[i][CITY_Y_INDEX]]
    MADict[MAData[i][0]] = [MAData[i][CITY_X_INDEX], MAData[i][CITY_Y_INDEX]]



graph = snap.TUNGraph.New()
for i in range(26):
    graph.AddNode(i)
for i in range(26):
    for j in range(26):
        graph.AddEdge(i, j)
SaveGraph(graph, "C:\\Users\\Zhuo\\Desktop\\Winter_job\\Simulator\\SocialNetworkSimulator\\Tweets\\Vaccine\\CityNetwork1.txt", MADict)
