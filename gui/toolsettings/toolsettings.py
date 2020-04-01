#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
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

        # Set background color
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor("#eeeeee"))
        self.setPalette(palette)

        self.slider_value.valueChanged.connect(self.update)

        self.show()
    def setup(self, name, setrange=(0,0,100), units=None, step=0.1, dec_precision=0, current=None):
        """
        Sets up main values for the ToolSettings widget, including the name and the values for the
        range as (minimum, initial, maximum).

        name: The name to be displayed.
        setrange: Tuple (min, current, max) specifying the allowed min/max values and current value.
        units: String value for the units to be displayed.
        step: sets the granularity of a single step of the parameter
        """
        self.label_name.setText(name)

        # unpack and assign slider min, current, and max
        (low, val, high) = setrange
        self.update_range(valuerange=(low, high), step=step)
        self.label_min.setText(str(low))
        self.label_max.setText(str(high))
        self.value = val
        
        self.dec_precision = dec_precision
        self.current = current

        # Handle optional units
        if units is not None:
            self.label_units.setText(str(units))
        else:
            self.label_units.setText("")

        self.update(val)

    def load_presets(self, name="default"):
        toolsettings_default = {
                "name": "Param",
                "default": 50,
                "min": 0,
                "max": 100,
                "current": None,
                "units": "-",
                "step": 1,
                "dec_precision": 0}
        entry = self._config.get(name, toolsettings_default)
        self.setup(
                entry.get("name", toolsettings_default["name"]),
                setrange=(
                    entry.get("min", toolsettings_default["min"]),
                    entry.get("default", toolsettings_default["default"]),
                    entry.get("max", toolsettings_default["max"])),
                units=entry.get("units", toolsettings_default["units"]),
                step=entry.get("step", toolsettings_default["step"]),
                current=entry.get("current", toolsettings_default["current"]),
                dec_precision=entry.get("dec_precision", toolsettings_default["dec_precision"]))

    def connect_config(self, config):
        self._config = config

    def update_range(self, valuerange=(0,1), step=0.1):
        """
        Updates the range of the progress bar widget.

        valuerange: (min, max) for the parameter
        step: sets the granularity of a single step of the parameter
        """
        self.min = valuerange[0]
        self.max = valuerange[1]
        self.step = step

        num_steps = 100 * (self.max - self.min) / self.step
        self.slider_scale = num_steps / (self.max - self.min)

        # set the max for exactly the number of steps we need
        self.slider_value.setMinimum(0)
        self.slider_value.setMaximum(num_steps)

        self.label_min.setText(str(valuerange[0]))
        self.label_max.setText(str(valuerange[1]))


    def update(self, value):
        """
        Updates the slider position and text value to a provided value (min < value < max).

        value: The value that the setting will display.
        """
        value = round(value / self.step) * self.step
        slider_value = int(self.slider_scale * (value - self.min))

        self.slider_value.setValue(slider_value)
        
        if isinstance(value, float):
            value = f'{value:.3}'
        else:
            value = str(value)

        self.label_value.setText(value)
        self.value = value


