#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic


class Menu(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Menu widget.

        Grabs child widgets.
        """
        super(Menu, self).__init__(*args)
        uic.loadUi("menu/menu.ui", self)
