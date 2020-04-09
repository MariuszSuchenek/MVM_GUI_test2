#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui

class Monitor(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Monitor widget.

        Grabs child widgets.
        """
        super(Monitor, self).__init__(*args)
        uic.loadUi("monitor/monitor.ui", self)
        self.name = None
        self.label_name = self.findChild(QtWidgets.QLabel, "label_name")
        self.label_value = self.findChild(QtWidgets.QLabel, "label_value")
        self.label_min = self.findChild(QtWidgets.QLabel, "label_min")
        self.label_max = self.findChild(QtWidgets.QLabel, "label_max")
        self.label_statnames = [];
        self.label_statnames.append(self.findChild(QtWidgets.QLabel, "label_statname1"))
        self.label_statnames.append(self.findChild(QtWidgets.QLabel, "label_statname2"))
        self.label_statvalues = [];
        self.label_statvalues.append(self.findChild(QtWidgets.QLabel, "label_statvalue1"))
        self.label_statvalues.append(self.findChild(QtWidgets.QLabel, "label_statvalue2"))

        # Set up connections
        self.mouseReleaseEvent = self.clear_alarm

        self.setAutoFillBackground(True)

    def setup(self, name, setrange=(0,50,100), units=None, stats=None, alarmcolor='red',
            color='black', step=None, dec_precision=0, alarm_min_code=-1, alarm_max_code=-1, alarm_handler=None):
        """
        Sets up main values for the Monitor widget, including the name and the values for the
        range as (minimum, initial, maximum). Also optionally set the units and statistical values
        of the monitored field.

        name: The name to be displayed.
        setrange: Tuple (min, current, max) specifying the allowed min/max values and current value.
        units: String value for the units to be displayed.
        alarmcolor: Background color that the monitor will change to on alarm
        color: Text color
        step: optional value for nearest rounded value (e.g. step=10 rounds to nearest 10)
        dec_precision: 
        alarm_min_code: the ESP code correponding at the minumum alarm
        alarm_max_code: the ESP code correponding at the maxmum alarm
        alarm_handler: the handler to communicate alarms with the ESP
        """

        # unpack and assign min, current, and max
        (low, val, high) = setrange
        self.name = name
        self.label_min.setText(str(low))
        self.label_max.setText(str(high))
        self.value = val
        self.minimum = low
        self.maximum = high
        self.step = step
        self.dec_precision = dec_precision

        # Handle optional units
        if units is not None:
            name = name + " " + str(units)
        self.label_name.setText(name)

        self.setStyleSheet("QWidget { color: " + str(color) + "; }");

        self.alarmcolor = alarmcolor
        self.update(val)

        self.alarm_min_code = alarm_min_code
        self.alarm_max_code = alarm_max_code
        self.alarm_h = alarm_handler

        # Handle optional stats
        # TODO: determine is stats are useful/necessary

    def update(self, value):
        """
        Updates the value in the monitored field

        value: The value that the monitor will display.
        """
        if self.step is not None:
            self.value = round(value / self.step) * self.step
        else:
            self.value = value;
        self.label_value.setText("%.*f" % (self.dec_precision, self.value))

        # handle palette changes due to alarm
        if self.is_alarm():
            palette = self.palette()
            role = self.backgroundRole() #choose whatever you like
            palette.setColor(role, QtGui.QColor(self.alarmcolor))
            self.setPalette(palette)
            if self.alarm_h is not None:
                self.alarm_h.raise_alarm(self.alarm_min_code is self.is_alarm_min() else self.alarm_max_code)

    def clear_alarm(self, event):
        """
        Clears previous out of range alarms by reverting the background color.
        """
        palette = self.palette()
        role = self.backgroundRole() #choose whatever you like
        palette.setColor(role, QtGui.QColor("#000000"))
        self.setPalette(palette)
        if self.alarm_h is not None:
            self.alarm_h.stop_alarm(self.name)


    def is_alarm(self):
        """
        Returns true if the monitored value is beyond the min or max threshold (i.e ALARM!).
        """
        return self.value <= self.minimum or self.value >= self.maximum

    def is_alarm_min(self):
        """
        Returns true if the monitored value is below the min threshold (i.e ALARM!).
        """
        return self.value <= self.minimum
