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

    def connect_monitors_and_plots(self, mainparent):
        self.mainparent = mainparent
        self.monitors = mainparent.monitors
        self.monitor_slots = mainparent.monitor_slots
        self.plots = mainparent.plots
        self.plot_slots = mainparent.plot_slots
        self.plot_hidden_slots = mainparent.plot_hidden_slots

    def populate_monitors_and_plots(self):
        # Get all active plots and monitors and put the remaining monitors on the alarms page
        self.active_plots = []
        self.active_monitors = []
        for (i, name) in enumerate(self.monitors):
            monitor = self.monitors[name]
            plot = self.plots[name]
            self.layout.addWidget(monitor, int(i % 3), 10-int(i / 3)) 
            self.plot_hidden_slots.addWidget(plot, i)
            for (mon_slotname, plot_slotname) in zip(self.monitor_slots, self.plot_slots):
                monitor_slot = self.monitor_slots[mon_slotname]
                if monitor.location == mon_slotname:
                    self.monitor_slots[mon_slotname].addWidget(monitor, 0, 0)
                    self.plot_slots[plot_slotname].addWidget(plot, 0, 0)
                    self.active_monitors.append(monitor)
                    self.active_plots.append(plot)
                    break

        return (self.active_monitors, self.active_plots)
