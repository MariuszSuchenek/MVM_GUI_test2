#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui


class AlarmsBar(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the AlarmsBar widget.

        Grabs child widgets.
        """
        super(AlarmsBar, self).__init__(*args)
        uic.loadUi("alarms/alarmsbar.ui", self)
