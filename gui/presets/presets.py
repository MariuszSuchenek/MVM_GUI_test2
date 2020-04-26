#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui


class Presets(QtWidgets.QWidget):
    def __init__(self, presets, *args):
        """
        Initialize the Presets widget.

        Grabs child widgets.
        """
        super(Presets, self).__init__(*args)
        uic.loadUi("presets/presets.ui", self)

        self.value = None
        # self.settings_owner = args[0] if len(args) else None

        # get the buttons from the preset dialog
        self.button_cancel = self.findChild(
            QtWidgets.QPushButton, "button_cancel")
        self.button_preset = []
        for i in range(1, 7):
            self.button_preset.append(self.findChild(
                QtWidgets.QPushButton, "button_preset"+str(i)))

        for preset, button in zip(presets, self.button_preset):
            if len(preset[1]):
                btn_txt = str(preset[0]) + ' (' + preset[1] + ')'
            else:
                btn_txt = str(preset[0])
            button.setText(btn_txt)

        # Hide the buttons that are not needed
        for i in range(len(presets), len(self.button_preset)):
            self.button_preset[i].hide()
