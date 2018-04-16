import os

from PyQt4 import QtCore, QtGui

import Utility

from QTClass import QTCharacteristicForm
class CharacteristicForm(QtGui.QWidget, QTCharacteristicForm.Ui_MainWindow):
    def setupUi(self, MainWindow):
        super(CharacteristicForm, self).setupUi(MainWindow)

    def retranslateUi(self, MainWindow):
        super(CharacteristicForm, self).retranslateUi(MainWindow)
        self.pushButton.clicked.connect(self.SavetoFile)
    def SetOutput(self, listValue):
        self.textEdit.setText("")
        for key in listValue.keys():
            self.textEdit.insertPlainText(str.format("Node {0}: {1}\n", str(key), str(listValue[key])))

    def SavetoFile(self):
        if self.textEdit.toPlainText() != "":
            fileName = QtGui.QFileDialog.getSaveFileName(self, 'Dialog Title', '/path/to/default/centrality_result',
                                                         selectedFilter='*.txt')
            if fileName:
                f = open(fileName, 'w')
                f.write(self.textEdit.toPlainText())
                f.close()
