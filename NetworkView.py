from PyQt4 import QtCore, QtGui

import GlobalParameters
import Utility


class NetworkViewer(QtGui.QGraphicsView):
    def __init__(self, parent):
        super(NetworkViewer, self).__init__(parent)
        self._zoom = 0
        self.totalFactor = 1.0
        self.pan = False
        self.parentClass = None
        # self.startX = 0
        # self.startY = 0
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

    def SetParentClass(self, parentClass):
        self.parentClass = parentClass

    def zoomFactor(self):
        return self._zoom

    def wheelEvent(self, event):
        if len(self.scene().items()) > 0:
            if event.delta() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom != 0:
                self.scale(factor, factor)
                self.totalFactor *= factor
            elif self._zoom == 0:pass
                #self.fitInView()
            else:
                self._zoom = 0

    def mouseDoubleClickEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.RightButton:
            self.scale(1/self.totalFactor, 1/self.totalFactor)
            self.totalFactor = 1.0

        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            if self.parentClass is None:
                return

            currentX = QMouseEvent.x()
            currentY = QMouseEvent.y()

            for node in self.parentClass.nodeItemList:
                rect = self.parentClass.nodeItemList[node].rect()
                topLeft = rect.topLeft()
                topRight = rect.topRight()
                bottomLeft = rect.bottomLeft()

                if currentX >= topLeft.x() and currentX <= topRight.x() and currentY <= bottomLeft.y() and currentY >= topLeft.y():
                    item = self.parentClass.nodeItemList[node]
                    brush = QtGui.QBrush(QtGui.QColor(GlobalParameters.SeedNodeBrushColor))
                    item.setBrush(brush)
                    seedText = self.parentClass.textEditSeedNodes.toPlainText()
                    self.parentClass.textEditSeedNodes.setPlainText(str(seedText + ";" + str(node)).lstrip(";"))
                    break

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.pan = True
            self.startX = QtGui.QCursor.pos().x()
            self.startY = QtGui.QCursor.pos().y()
            self.setCursor(QtCore.Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.pan = False
            self.setCursor(QtCore.Qt.ArrowCursor)

    def mouseMoveEvent(self, QMouseEvent):
        if self.pan:
            pos = QtGui.QCursor.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (pos.x() - self.startX))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (pos.y() - self.startY))
            self.startX = pos.x()
            self.startY = pos.y()



