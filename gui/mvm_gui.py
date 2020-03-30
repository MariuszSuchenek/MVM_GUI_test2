#!/usr/bin/python3
'''
Runs the MVM GUI
'''

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

import yaml

from mainwindow import MainWindow
        
if __name__ == "__main__":

    with open('default_settings.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    print ('Config:', yaml.dump(config), sep='\n')

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    app.exec_()
