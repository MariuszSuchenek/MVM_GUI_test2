#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
import sys

class ThreeMonitors(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the ThreeMonitors widget.

        Grabs child widgets.
        """
        super(ThreeMonitors, self).__init__(*args)
        uic.loadUi("monitor/three_monitors.ui", self)

