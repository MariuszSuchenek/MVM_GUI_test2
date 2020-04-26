#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui


class MainDisplay(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the MainDisplay container widget.

        Provides a passthrough to underlying widgets.
        """
        super(MainDisplay, self).__init__(*args)
        uic.loadUi("maindisplay/maindisplay.ui", self)
