import sys
from PyQt4 import QtGui, QtCore
import numpy
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import GlobalParameters



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
        self.maxY = 0
        # create an axis
        self.ax = plt.subplot()
        self.isDraw = False

    def DrawPlot(self, NNR):
        ''' plot some random stuff '''
        # random data
        self.y.append(float(NNR))
        self.x.append(len(self.y))

        self.ax.clear()
        # remeber the old graph
        self.ax.hold(True)
        self.ax.plot(self.x, self.y, 'o')

        self.canvas.draw()

        self.ax.set_ylabel('Nearest Neighbor Ratio')
        self.ax.set_xlabel('Time')


        try:
            coefficients = numpy.polyfit(self.x, self.y, 3)
            polynomial = numpy.poly1d(coefficients)
            ys = polynomial(self.x)
            print coefficients

            GlobalParameters.RegressionCoefficients = coefficients
            print polynomial

            self.ax.plot(self.x, ys)
            pstr = r'$' + str(coefficients[0]) + r'x^{3}' + str(coefficients[1]) + r'x^{2}' + str(
                coefficients[2]) + r'x +' + str(coefficients[3]) + r'$'
            # ax.annotate(pstr,
            #             xy=(1, 1), xycoords='axes fraction',
            #             xytext=(-300, -50), textcoords='offset points', fontsize=10)
            self.canvas.draw()
        except:
            pass

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


        try:
            coefficients = numpy.polyfit(self.x, self.y, 3)
            polynomial = numpy.poly1d(coefficients)
            ys = polynomial(self.x)
            print coefficients
            print polynomial

            self.ax.plot(self.x, ys)
            pstr = r'$' + str(coefficients[0]) + r'x^{3}' + str(coefficients[1]) + r'x^{2}' + str(
                coefficients[2]) + r'x +' + str(coefficients[3]) + r'$'
            # ax.annotate(pstr,
            #             xy=(1, 1), xycoords='axes fraction',
            #             xytext=(-300, -50), textcoords='offset points', fontsize=10)
            self.canvas.draw()
        except:
            pass

    def DrawPlot3(self):
        if len(self.x) == 0:
            for i in range(len(self.y)):
                self.x.append(i)

        self.ax.clear()
        # remeber the old graph
        self.ax.hold(True)
        self.ax.plot(self.x, self.y)
        self.ax.plot(self.x, self.y, 'go')
        self.canvas.draw()
        self.ax.xaxis.set_ticks(numpy.arange(0, len(self.x), 1))
        #self.ax.set_xlim(1, len(self.x), 1)  # set axis limits
        #self.ax.ylim(0, 30.)
        maxy = max(self.y)
        #print "MAXY", maxy
        self.maxY = (5 - maxy % 5) + maxy
        #print "MAXY", maxy
        self.ax.set_ylim(0, self.maxY)

        self.ax.set_ylabel('# Active Nodes')
        self.ax.set_xlabel('Step')

    def DrawPlot4(self):
        self.x = numpy.arange(len(self.y))

        self.ax.clear()
        # remeber the old graph
        self.ax.hold(True)
        width = 0.35
        rects = self.ax.bar(self.x, self.y, width, color='r')
        self.canvas.draw()

        self.ax.set_xticks(self.x + width / 2)
        #self.ax.set_xticklabels(("1","1","1","1","1"))
        self.ax.set_xticklabels(numpy.arange(0, len(self.x), 1))
        #self.ax.xaxis.set_ticks(numpy.arange(0, len(self.x), 1))
        #self.ax.set_xlim(1, len(self.x), 1)  # set axis limits
        #self.ax.ylim(0, 30.)
        #print "MAXY", maxy
        self.maxY = 100
        self.ax.set_ylim(0, self.maxY)

        self.ax.set_ylabel('Percentage of active cities(%)')
        self.ax.set_xlabel('Step')

        for rect in rects:
            height = rect.get_height()
            self.ax.text(rect.get_x() + rect.get_width() / 2., height + 2,
                    '%d' % int(height),
                    ha='center', va='bottom')

