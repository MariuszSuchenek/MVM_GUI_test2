#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
import sys

class SettingsBar(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the SettingsBar container widget.

        Provides a passthrough to underlying widgets.
        """
        super(SettingsBar, self).__init__(*args)
        uic.loadUi("settings/settingsbar.ui", self)

