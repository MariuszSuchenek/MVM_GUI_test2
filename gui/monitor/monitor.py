#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui

class Monitor(QtWidgets.QWidget):
    def __init__(self, name, config, *args):
        """
        Initialize the Monitor widget.

        Grabs child widgets.
        """
        super(Monitor, self).__init__(*args)
        uic.loadUi("monitor/monitor.ui", self)
        self.config = config

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
        self.frame = self.findChild(QtWidgets.QFrame, "frame")

        monitor_default = {
                "name": "NoName",
                "min": 0,
                "init": 50,
                "max": 100,
                "step": None,
                "units": None,
                "dec_precision": 0,
                "color": "white",
                "alarmcolor": "red",
                "plot_var": "o2",
                "location": None}
        entry = self.config.get(name, monitor_default)
        # unpack and assign min, current, and max
        self.name = entry.get("name", monitor_default["name"])
        self.value = entry.get("init", monitor_default["init"])
        self.minimum = entry.get("min", monitor_default["min"])
        self.maximum = entry.get("max", monitor_default["max"])
        self.set_minimum = entry.get("setmin", self.minimum)
        self.set_maximum = entry.get("setmax", self.maximum)
        self.step = entry.get("step", monitor_default["step"])
        self.dec_precision = entry.get("dec_precision", monitor_default["dec_precision"])
        self.location = entry.get("location", monitor_default["location"])

        self.units = entry.get("units", monitor_default["units"])
        self.alarmcolor = entry.get("alarmcolor", monitor_default["alarmcolor"])
        self.color = entry.get("color", monitor_default["color"])

        self.refresh()
        self.update(self.value)

        # Setup config mode
        self.config_mode = False
        self.unhighlight()

        # Handle optional stats
        # TODO: determine is stats are useful/necessary


    def refresh(self):
        self.label_min.setText(str(self.set_minimum))
        self.label_max.setText(str(self.set_maximum))

        # Handle optional units
        if self.units is not None:
            self.label_name.setText(self.name + " " + str(self.units))
        else:
            self.label_name.setText(self.name)

        self.setStyleSheet("QWidget { color: " + str(self.color) + "; }");
        self.setAutoFillBackground(True)

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

    def clear_alarm(self):
        """
        Clears previous out of range alarms by reverting the background color.
        """
        palette = self.palette()
        role = self.backgroundRole() #choose whatever you like
        palette.setColor(role, QtGui.QColor("#000000"))
        self.setPalette(palette)

    def is_alarm(self):
        """
        Returns true if the monitored value is beyond the min or max threshold (i.e ALARM!).
        """
        return self.value <= self.set_minimum or self.value >= self.set_maximum

    def highlight(self):
        self.frame.setStyleSheet("#frame { border: 5px solid limegreen; }");

    def unhighlight(self):
        self.frame.setStyleSheet("#frame { border: 1px solid white; }");

        
