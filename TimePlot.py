import sys
from PyQt4 import QtGui, QtCore
import numpy
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import GlobalParameters
#import TimeRegession

class PlotWindow(QtGui.QDialog):
    def __init__(self, title, parent=None):
        super(PlotWindow, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure()
        self.setWindowTitle(title)
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.y = []
        self.x = []

        # create an axis
        self.ax = self.figure.add_subplot(111)
        self.isDraw = False

    def DrawPlot2(self):
        if len(self.x) == 0:
            for i in range(len(self.y)):
                self.x.append(i)

        self.ax.clear()
        # remeber the old graph
        self.ax.hold(True)
        self.ax.plot(self.x, self.y, 'o')

        self.canvas.draw()

        self.ax.set_ylabel('Time Nearest Neighbor Ratio')
        self.ax.set_xlabel('Tweets')


        # try:
        #     coefficients = numpy.polyfit(self.x, self.y, 3)
        #     polynomial = numpy.poly1d(coefficients)
        #     ys = polynomial(self.x)
        #     print coefficients
        #     print polynomial
        #
        #     self.ax.plot(self.x, ys)
        #     pstr = r'$' + str(coefficients[0]) + r'x^{3}' + str(coefficients[1]) + r'x^{2}' + str(
        #         coefficients[2]) + r'x +' + str(coefficients[3]) + r'$'
        #     # ax.annotate(pstr,
        #     #             xy=(1, 1), xycoords='axes fraction',
        #     #             xytext=(-300, -50), textcoords='offset points', fontsize=10)
        #     self.canvas.draw()
        # except:
        #     pass

