#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui

class Monitor(QtWidgets.QWidget):
    def __init__(self, name, config, *args):
        """
        Initialize the Monitor widget.

        Grabs child widgets and sets alarm facility up.

        """
        super(Monitor, self).__init__(*args)
        uic.loadUi("monitor/monitor.ui", self)
        self.config = config
        self.configname = name

        self.label_name = self.findChild(QtWidgets.QLabel, "label_name")
        self.label_value = self.findChild(QtWidgets.QLabel, "label_value")
        self.label_min = self.findChild(QtWidgets.QLabel, "label_min")
        self.label_max = self.findChild(QtWidgets.QLabel, "label_max")
        self.stats_slots = self.findChild(QtWidgets.QGridLayout, "stats_slots")
        self.frame = self.findChild(QtWidgets.QFrame, "frame")

        monitor_default = {
                "name": "NoName",
                "init": 50,
                "units": None,
                "step": 1,
                "dec_precision": 0,
                "color": "white",
                "alarmcolor": "red",
                "observable": "o2"}
        entry = self.config['monitors'].get(name, monitor_default)

        self.entry = entry
        self.name = entry.get("name", monitor_default["name"])
        self.value = entry.get("init", monitor_default["init"])
        self.units = entry.get("units", monitor_default["units"])
        self.dec_precision = entry.get("dec_precision", monitor_default["dec_precision"])
        self.color = entry.get("color", monitor_default["color"])
        self.alarmcolor = entry.get("alarmcolor", monitor_default["alarmcolor"])
        self.step = entry.get("step", monitor_default["step"])
        self.observable = entry.get("observable", monitor_default["observable"])

        self.refresh()
        self.set_alarm_state(False)
        self.update_value(self.value)
        self.update_thresholds(None, None, None, None)
        # self.alarm = None

        # Setup config mode
        self.config_mode = False
        self.unhighlight()

        # Handle optional stats
        # TODO: determine is stats are useful/necessary

    def name(self):
        '''
        Returns the configuration name 
        for this monitor
        '''
        return self.configname

    def connect_gui_alarm(self, gui_alarm):
        '''
        Stores the GuiAlarm class
        '''
        self.gui_alarm = gui_alarm

    def update_thresholds(self, alarm_min, alarm_setmin, alarm_max, alarm_setmax):
        '''
        Updates the labes showind the threshold values
        '''
        self.label_min.hide()
        self.label_max.hide()
        # if self.alarm is not None:
        print("Updating thresholds for " + self.configname)

        if alarm_min is not None:
            self.label_min.setText(str(alarm_setmin))
            self.label_min.show()

        if alarm_max is not None:
            self.label_max.setText(str(alarm_setmax))
            self.label_max.show()

    def refresh(self):
        # Handle optional units
        if self.units is not None:
            self.label_name.setText(self.name + " " + str(self.units))
        else:
            self.label_name.setText(self.name)

        self.setStyleSheet("QWidget { color: " + str(self.color) + "; }");
        self.setAutoFillBackground(True)

    def set_alarm_state(self, isalarm):
        '''
        Sets or clears the alarm
        arguments:
        - isalarm: True is alarmed state
        '''
        if isalarm:
            color = self.alarmcolor
        else:
            color = QtGui.QColor("#000000")
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(color))
        self.setPalette(palette)

    def highlight(self):
        self.frame.setStyleSheet("#frame { border: 5px solid limegreen; }");

    def unhighlight(self):
        self.frame.setStyleSheet("#frame { border: 0.5px solid white; }");

    def update_value(self, value):
        if self.step is not None:
            self.value = round(value / self.step) * self.step
        else:
            self.value = value;
        self.label_value.setText("%.*f" % (self.dec_precision, self.value))




