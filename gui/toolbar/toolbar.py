#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
import sys

from menu.menu import Menu

class Toolbar(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Toolbar container widget.

        Provides a passthrough to underlying widgets.
        """
        super(Toolbar, self).__init__(*args)
        uic.loadUi("toolbar/toolbar.ui", self)

        self.show()

