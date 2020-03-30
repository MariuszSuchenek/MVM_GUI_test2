#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets

class Settings(QtWidgets.QMainWindow):
    def __init__(self, *args):
        """
        Initialized the Settings overlay widget.
        """
        super(Settings, self).__init__(*args)
        uic.loadUi("settings/settings.ui", self)
