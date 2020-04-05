#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
import sys

class Startup(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Startup container widget.

        Provides a passthrough to underlying widgets.
        """
        super(Startup, self).__init__(*args)
        uic.loadUi("startup/startup.ui", self)
