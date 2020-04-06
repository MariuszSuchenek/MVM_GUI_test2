#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui

class PauseBar(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the PauseBar widget.

        Grabs child widgets.
        """
        super(PauseBar, self).__init__(*args)
        uic.loadUi("menu/pausebar.ui", self)

