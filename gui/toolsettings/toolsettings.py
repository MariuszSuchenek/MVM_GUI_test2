#!/usr/bin/python3
from PyQt5 import QtWidgets, uic
import sys

class ToolSettings(QtWidgets.QWidget):
    def __init__(self, *args):
        super(ToolSettings, self).__init__(*args)
        uic.loadUi("toolsettings/toolsettings.ui", self)
        self.label_name = self.findChild(QtWidgets.QLabel, "label_name")
        self.label_value = self.findChild(QtWidgets.QLabel, "label_value")
        self.slider_value = self.findChild(QtWidgets.QSlider, "slider_value")

        self.slider_value.valueChanged.connect(self.update)

        self.show()
    def setup(self, name, setrange):
        self.label_name.setText(name)

        # unpack and assign slider min, current, and max
        (low, val, high) = setrange
        self.slider_value.setMinimum(low)
        self.slider_value.setMaximum(high)
        self.update(val)
        print("Set value to " + str(low) + " " + str(val)  + " " + str(high))

    def update(self, value):
        self.slider_value.setSliderPosition(value)
        self.label_value.setText(str(value))


