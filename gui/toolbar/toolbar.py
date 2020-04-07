#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
import os

from menu.menu import Menu

class Toolbar(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Toolbar container widget.

        Provides a passthrough to underlying widgets.
        """
        super(Toolbar, self).__init__(*args)
        uic.loadUi(os.environ['MVMGUI']+"toolbar/toolbar.ui", self)

        self.label_status = self.findChild(QtWidgets.QLabel, "label_status")
        self.set_stopped("Automatic")

    def set_stopped(self, mode_text=""):
        self.label_status.setText("Status: Stopped\n" + mode_text)
        self.label_status.setStyleSheet(
                "QLabel { background-color : red; color: yellow;}");

    def set_running(self, mode_text=""):
        self.label_status.setText("Status: Running\n" + mode_text)
        self.label_status.setStyleSheet(
                "QLabel { background-color : green;  color: yellow;}");
