import snap
import numpy
import matplotlib.pyplot as plt

mainpath = "C:\\Users\\GISer\\Desktop\\"
filename = "1-1.txt"
f = open(mainpath + filename, "r")
graph = snap.TUNGraph.New()
endofFile = False
line = f.readline()
strs = line.split("#")
numNodes = int(strs[1])
numEdges = int(strs[3])
index = 0
graphLabelToId = {}
for i in range(numNodes):
    line = f.readline().rstrip("\n")
    graph.AddNode(index)
    graphLabelToId[line] = index
    index += 1
for j in range(numEdges):
    line = f.readline().rstrip("\n")
    strs = line.split("#")
    graph.AddEdge(graphLabelToId[strs[0]], graphLabelToId[strs[1]])

snap.PlotInDegDistr(graph, "wikiInDeg", "wiki-vote In Degree")

DegToCntV = snap.TIntPrV()
snap.GetDegCnt(graph, DegToCntV)
x = []
y = []
for item in DegToCntV:
    x.append(item.GetVal1())
    y.append(item.GetVal2())
    print "%d nodes with degree %d" % (item.GetVal2(), item.GetVal1())

width = 0.35
rects = plt.bar(x, y, width)
xticks = numpy.array(x)
plt.xlabel('Degree')
plt.ylabel('The number of nodes')
plt.xticks(xticks + width/2.0, x)

for rect in rects:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width() / 2., height + 2,
                 '%d' % int(height),
                 ha='center', va='bottom')

plt.show()