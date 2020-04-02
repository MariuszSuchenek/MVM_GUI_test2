#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
import sys

class Menu(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Menu widget.

        Grabs child widgets.
        """
        super(Menu, self).__init__(*args)
        uic.loadUi("menu/menu.ui", self)

        self.label_status = self.findChild(QtWidgets.QLabel, "label_status")
        self.set_stopped()

        self.show()

    def set_stopped(self):
        self.label_status.setText("Status: Stopped") 
        self.label_status.setStyleSheet("QLabel { background-color : red; }");

    def set_running(self):
        self.label_status.setText("Status: Running") 
        self.label_status.setStyleSheet("QLabel { background-color : green; }");
