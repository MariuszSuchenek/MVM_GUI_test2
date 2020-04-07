#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui

class Alarms(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Alarms widget.

        Grabs child widgets.
        """
        super(Alarms, self).__init__(*args)
        uic.loadUi("alarms/alarms.ui", self)

        self.layout = self.findChild(QtWidgets.QGridLayout, "monitors_layout")

    def connect_monitors(self, monitors, monitor_slots):
        self.monitors = monitors
        self.monitor_slots = monitor_slots

    def populate_monitors(self):
        for (i, name) in enumerate(self.monitors):
            monitor = self.monitors[name]
            self.layout.addWidget(self.monitors[name], int(i % 3), 10-int(i / 3)) 
            for barname in self.monitor_slots:
                monitor_slot = self.monitor_slots[barname]
                if monitor.location == barname:
                    self.monitor_slots[barname].addWidget(monitor, 0, 0)
                    break
