#!/usr/bin/python3
'''
Runs the MVM GUI
'''

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

from mainwindow import MainWindow
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
