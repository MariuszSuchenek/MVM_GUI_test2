#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
import sys

class ToolSettings(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialized the ToolSettings widget.

        Grabs child widgets and and connects slider value to text value.
        """
        super(ToolSettings, self).__init__(*args)
        uic.loadUi("toolsettings/toolsettings.ui", self)
        self.label_name = self.findChild(QtWidgets.QLabel, "label_name")
        self.label_value = self.findChild(QtWidgets.QLabel, "label_value")
        self.slider_value = self.findChild(QtWidgets.QProgressBar, "slider_value")
        self.label_min = self.findChild(QtWidgets.QLabel, "label_min")
        self.label_max = self.findChild(QtWidgets.QLabel, "label_max")
        self.label_units = self.findChild(QtWidgets.QLabel, "label_units")

        self.slider_value.valueChanged.connect(self.update)

        self.show()
    def setup(self, name, setrange=(0,0,100), units=None):
        """
        Sets up main values for the ToolSettings widget, including the name and the values for the
        range as (minimum, initial, maximum).

        name: The name to be displayed.
        setrange: Tuple (min, current, max) specifying the allowed min/max values and current value.
        units: String value for the units to be displayed.
        """
        self.label_name.setText(name)

        # unpack and assign slider min, current, and max
        (low, val, high) = setrange
        self.slider_value.setMinimum(low)
        self.slider_value.setMaximum(high)
        self.label_min.setText(str(low))
        self.label_max.setText(str(high))
        self.value = val

        # Handle optional units
        if units is not None:
            self.label_units.setText(str(units))
        else:
            self.label_units.setText("")

        self.update(val)

    def update(self, value):
        """
        Updates the slider position and text value to a provided value (min < value < max).

        value: The value that the setting will display.
        """
        self.slider_value.setValue(value)
        self.label_value.setText(str(value))
        self.value = value


