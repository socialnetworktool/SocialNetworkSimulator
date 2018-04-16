import csv
import sys
import numpy
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

def ReadData(filepath):
    data = []
    with open(filepath, "r") as fp:
        reader = csv.reader(fp, dialect=csv.excel)
        for rows in reader:
            data.append(rows)
    return data

path = "C:\\Users\\GISer\\Desktop\\ABM Tool\\Result\\ResultFileB\\"

dataset = ReadData(path + "ResultB.csv")
networkfile = "SmallWorld_0800_2_0.5.txt"
def draw1(dataset):
    y = [[],[],[],[],[],[]]
    for i in range(len(dataset)):
        if dataset[i][0] == networkfile:
            y[int(dataset[i][2])].append(dataset[i][8])

    x = numpy.arange(26)

    plt.gca().set_color_cycle(['red', 'green', 'blue', 'purple', 'DeepSkyBlue'])

    plt.plot(x, y[0])
    plt.plot(x, y[1])
    plt.plot(x, y[2])
    plt.plot(x, y[3])
    plt.plot(x, y[4])

    plt.legend(['Degree', 'Betweenness', 'Closeness', 'Eigenvector', 'Random'], loc='upper left')

    plt.xlabel('# Seed Nodes')
    plt.ylabel('Influence Size')

    plt.show()


def draw2(dataset):
    y = [[], [], [], [], [], []]
    for i in range(len(dataset)):
        if dataset[i][0] == networkfile:
            y[int(dataset[i][2])].append(dataset[i][8])

    x = numpy.arange(1,21)

    plt.gca().set_color_cycle(['red', 'green', 'blue', 'purple', 'DeepSkyBlue'])

    plt.plot(x, y[0])
    plt.plot(x, y[1])
    plt.plot(x, y[2])
    plt.plot(x, y[3])
    plt.plot(x, y[4])

    plt.legend(['Degree', 'Betweenness', 'Closeness', 'Eigenvector', 'Random'], loc='best')

    plt.xlabel('# Percent Opinion Leader(%)')
    plt.ylabel('Influence Size')
    plt.ylim(40, 350)
    plt.show()

draw2(dataset)

