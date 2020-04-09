#!/usr/bin/env python3
'''
Runs the MVM GUI
'''

import sys
import os
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import uic

import yaml

from mainwindow import MainWindow
from communication.esp32serial import ESP32Serial
from communication.fake_esp32serial import FakeESP32Serial
from messagebox import MessageBox
from alarm_handler import AlarmHandler

def connect_esp32(config):
    try:
        if 'fakeESP32' in sys.argv:
            print('******* Simulating communication with ESP32')
            err_msg = "Cannot setup FakeESP32Serial"
            esp32 = FakeESP32Serial()
            esp32.set("wdenable", 1)
        else:
            err_msg = "Cannot communicate with port %s" % config['port']
            esp32 = ESP32Serial(config['port'])
            esp32.set("wdenable", 1)
    except Exception as error:
        msg = MessageBox()
        fn = msg.critical("Do you want to retry?",
                          "Severe hardware communication error",
                          str(error) + err_msg, "Communication error",
                          { msg.Retry: lambda: connect_esp32(config),
                            msg.Abort: lambda: None})
        return fn()

    return esp32


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    settings_file = os.path.join(base_dir, 'default_settings.yaml')

    with open(settings_file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    print ('Config:', yaml.dump(config), sep='\n')

    app = QtWidgets.QApplication(sys.argv)

    esp32 = connect_esp32(config)

    if esp32 is None:
        exit(-1)

    watchdog = QtCore.QTimer()
    watchdog.timeout.connect(esp32.set_watchdog)
    watchdog.start(config["wdinterval"] * 1000)

    alarm_h = AlarmHandler(config, esp32)

    window = MainWindow(config, esp32)
    window.show()
    app.exec_()
    esp32.set("wdenable", 0)

