#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
import sys

class Presets(QtWidgets.QWidget):
    def __init__(self, presets, *args):
        """
        Initialize the Presets widget.

        Grabs child widgets.
        """
        super(Presets, self).__init__(*args)
        uic.loadUi("presets/presets.ui", self)

        self.value = None

        # get the buttons from the preset dialog
        self.button_cancel = self.findChild(QtWidgets.QPushButton, "button_cancel")
        self.button_preset = []
        for i in range(1, 7):
            self.button_preset.append(self.findChild(QtWidgets.QPushButton, "button_preset"+str(i)))

        for preset, button in zip(presets, self.button_preset):
            button.setText(str(preset))

        # Hide the buttons that are not needed
        for i in range(len(presets), len(self.button_preset) - len(presets)):
            self.button_preset[i].hide()


