import snap
from datetime import datetime
from xlrd import open_workbook
import math
import GlobalParameters
from PyQt4 import QtCore, QtGui
import Utility
import time


class ReadXLS(QtCore.QThread):
    def __init__(self, filepath, tSpan):
        QtCore.QThread.__init__(self)
        self.filepath = filepath
        self.title = []
        self.tSpan = tSpan
        self.items = []

    def ReadXML(self):
        wb = open_workbook(self.filepath)

        sheet = wb.sheet_by_index(0)
        numberOfRows = sheet.nrows
        numberOfColumns = sheet.ncols
        items = [None] * numberOfRows

        for row in range(numberOfRows):
            values = [None] * numberOfColumns
            for col in range(numberOfColumns):
                values[col] = sheet.cell(row, col).value
            items[row] = values
        if len(items) > 0:
            self.title = list(items.pop(0))
        self.items = items
        return self.items

    def run(self):
        items = self.ReadXML()
        colTimeIndex = self.title.index("CREATED_AT_LOCAL")
        beginTime = datetime.strptime(items[0][colTimeIndex], '%Y-%m-%d %H:%M:%S')

        timeZone = 24 * 3600 / self.tSpan

        tweets = []
        tweetsCount = 0
        for i in range(len(items)):
            t = datetime.strptime(items[i][colTimeIndex], '%Y-%m-%d %H:%M:%S')
            loop = True
            while loop:
                if self.DeltaTime(t, beginTime) <= (len(tweets) + 1) * self.tSpan:
                    tweetsCount += 1
                    loop = False
                else:
                    # if len(tweets) == 0:
                    #     tc = t.hour * 3600 / self.tSpan
                    # else:
                    #     tc = (tweets[len(tweets) -1][1] + 1) % timeZone
                    #tweets.append([len(tweets), tc, tweetsCount])
                    tweets.append(tweetsCount)
                    tweetsCount = 0

        # for i in range(len(tweets)):
        #     print tweets[i][0],tweets[i][1],tweets[i][2]

        return tweets



    def DeltaTime(self, a, b):
        delta = a - b
        return delta.days * 3600 * 24 + delta.seconds




import TimePlot
if __name__ == "__main__":
    network = ReadXLS("C:\Users\ldang\Desktop\San-Diego-GIS-data\wildfire(new)\\fire_new_geo.xlsx", 1800)

    tweets = network.run()
    plot = TimePlot.PlotWindow("Tweets over time")
    plot.show()
    plot.y = tweets
    plot.DrawPlot2()
