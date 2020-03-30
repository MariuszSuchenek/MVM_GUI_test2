#!/usr/bin/python3
'''
Runs the MVM GUI
'''

import sys
import os
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

import yaml

from mainwindow import MainWindow
from communication.esp32serial import ESP32Serial
import communication.fake_esp32serial

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    settings_file = os.path.join(base_dir, 'default_settings.yaml')
    
    with open(settings_file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    print ('Config:', yaml.dump(config), sep='\n')

    if config['read_from_esp']:
        try:
            esp32 = ESP32Serial(config['port'])
        except:
            # TODO: find a more graphical way to report the error
            # it won't run in a terminal!
            print(f"\033[91mERROR: Cannot communicate with port {config['port']}\033[0m")
    else:
        esp32 = communication.fake_esp32serial.FakeESP32Serial()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(config, esp32)
    window.show()
    app.exec_()
