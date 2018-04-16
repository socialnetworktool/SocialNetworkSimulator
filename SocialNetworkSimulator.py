import sys
from PyQt4 import QtGui
from MainForm import UIMainWindow

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QMainWindow()
    UI = UIMainWindow()
    UI.setupUi(Form)
    Form.show()
    Form.showMaximized()

    # Reset UI
    UI.TurnOffAllWindows()
    UI.groupBoxNetworkGenerator.setVisible(True)
    UI.comboBoxBaseMapLayers.setVisible(False)
    UI.comboBoxBaseMapLayersComplex.setVisible(False)
    UI.GraphicsScene.setSceneRect(0,0,UI.FrameCanvas.width()-10,UI.FrameCanvas.height()-10)

    sys.exit(app.exec_())




