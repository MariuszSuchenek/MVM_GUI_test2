#!/usr/bin/python3
from PyQt5 import QtWidgets, uic
import sys

class ToolSettings(QtWidgets.QWidget):
    def __init__(self, *args):
        super(ToolSettings, self).__init__(*args)
        uic.loadUi("toolsettings/toolsettings.ui", self)
        self.show()
    def setup(self, name, setrange):
        print(1)

