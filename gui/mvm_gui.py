#!/usr/bin/python3
'''
Runs the MVM GUI
'''

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

import yaml

from mainwindow import MainWindow
from communication.esp32serial import ESP32Serial

if __name__ == "__main__":

    with open('default_settings.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    print ('Config:', yaml.dump(config), sep='\n')

    try:
        esp32 = ESP32Serial(config['port'])
    except:
        # TODO: find a more graphical way to report the error
        # it won't run in a terminal!
        print(f"\033[91mERROR: Cannot communicate with port {self._port}\033[0m")

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(config, esp32)
    window.show()
    app.exec_()
