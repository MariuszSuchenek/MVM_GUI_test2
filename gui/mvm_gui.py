'''
Runs the MVM GUI
'''

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

from gui import MVMGUI
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MVMGUI()
    window.connect()
    window.show()
    app.exec_()