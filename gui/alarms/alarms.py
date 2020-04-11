#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore

def clickable(widget):
    class Filter(QtCore.QObject):
        clicked = QtCore.pyqtSignal()
        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        return True
            return False
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

class Alarms(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Alarms widget.

        Grabs child widgets.
        """
        super(Alarms, self).__init__(*args)
        uic.loadUi("alarms/alarms.ui", self)

        self.layout          = self.findChild(QtWidgets.QGridLayout, "monitors_layout")
        self.label_alarmname = self.findChild(QtWidgets.QLabel,      "label_alarmname")

        self.slider_alarmmin = self.findChild(QtWidgets.QScrollBar,  "slider_alarmmin")
        self.alarmmin_min    = self.findChild(QtWidgets.QLabel,      "alarmmin_min")
        self.alarmmin_value  = self.findChild(QtWidgets.QLabel,      "alarmmin_value")
        self.alarmmin_max    = self.findChild(QtWidgets.QLabel,      "alarmmin_max")

        self.slider_alarmmax = self.findChild(QtWidgets.QScrollBar,  "slider_alarmmax")
        self.alarmmax_min    = self.findChild(QtWidgets.QLabel,      "alarmmax_min")
        self.alarmmax_value  = self.findChild(QtWidgets.QLabel,      "alarmmax_value")
        self.alarmmax_max    = self.findChild(QtWidgets.QLabel,      "alarmmax_max")

    def connect_monitors(self, mainparent):
        """
        Grabs monitors and their corresponding display slots from the main window.

        mainparent: Reference to the main window.
        """
        self.mainparent = mainparent
        self.monitors = mainparent.monitors
        self.monitors_slots = mainparent.monitors_slots
        self.displayed_monitors = mainparent.config['displayed_monitors']

        # connect monitors to selection and alarm clearing slots
        for name in self.monitors:
            monitor = self.monitors[name]
            clickable(monitor).connect(lambda n=name: self.select_monitor(n))

    def select_monitor(self, selected):
        """
        Selected a particular monitor widget by config name.

        selected: config name
        """
        for name in self.monitors:
            monitor = self.monitors[name]
            if name == selected:
                self.selected = name
                monitor.set_alarm_state(False)
                # if monitor.alarm is not None:
                #     monitor.alarm.clear_alarm()
                # Show configuration and highlight monitor
                if monitor.config_mode:
                    monitor.highlight()
                    self.show_settings(name)
            elif monitor.config_mode:
                monitor.unhighlight()

    def set_slider_range(self, slider, monitor):
        """
        Sets the range for a slider given the current monitor being used.
        Range is set to the coarseness of the monitor.step.

        slider: Reference to the slider to be set.
        monitor: Reference to the monitor to set slider range.
        """
        alarm = monitor.gui_alarm
        if alarm.has_valid_minmax(monitor.configname):
            slider.setMinimum(0)
            slider.setMaximum((alarm.get_max(monitor.configname) - alarm.get_min(monitor.configname)) / monitor.step)
            slider.setSingleStep(monitor.step)
            slider.setPageStep(slider.maximum() / 2)
            slider.setEnabled(True)
        else:
            slider.setMinimum(0)
            slider.setMaximum(0)
            slider.setPageStep(slider.maximum())
            slider.setDisabled(True)

    def do_alarmmin_moved(self, slidervalue, monitor):
        """
        A slot for when the minimum alarm slider moves.

        slidervalue: The physical value on the slider.
        monitor: Reference to the monitor to set the slider value.
        """
        # Prevent min > max
        alarm = monitor.gui_alarm
        if alarm.has_valid_minmax(monitor.configname):
            slidervalue = min(self.slider_alarmmax.sliderPosition(), slidervalue)
            value = slidervalue * monitor.step + alarm.get_min(monitor.configname)
            self.alarmmin_value.setText("Alarm min: " + str(value))
            self.slider_alarmmin.setValue(slidervalue)
            self.slider_alarmmin.setSliderPosition(slidervalue)

    def do_alarmmax_moved(self, slidervalue, monitor):
        """
        A slot for when the maximum alarm slider moves.

        slidervalue: The physical value on the slider.
        monitor: Reference to the monitor to set the slider value.
        """
        # Prevent max < min
        alarm = monitor.gui_alarm
        if alarm.has_valid_minmax(monitor.configname):
            slidervalue = max(self.slider_alarmmin.sliderPosition(), slidervalue)
            value = slidervalue * monitor.step + alarm.get_min(monitor.configname)
            self.alarmmax_value.setText("Alarm max: " + str(value))
            self.slider_alarmmax.setValue(slidervalue)
            self.slider_alarmmax.setSliderPosition(slidervalue)

    def show_settings(self, name):
        """
        Display settins for a given named monitor.

        name: The config name of the monitor.
        """
        monitor = self.monitors[name]
        alarm = monitor.gui_alarm
        self.label_alarmname.setText(monitor.name)
        self.label_alarmname.setStyleSheet("QLabel { color: " + monitor.color + "; background-color: black}")

        self.set_slider_range(self.slider_alarmmin, monitor)
        self.slider_alarmmin.valueChanged.connect(lambda value:
                self.do_alarmmin_moved(value, monitor))

        if alarm.has_valid_minmax(name):
            sliderpos = int((alarm.get_setmin(name) - alarm.get_min(name)) / monitor.step)
            self.slider_alarmmin.setSliderPosition(sliderpos)
            self.do_alarmmin_moved(sliderpos, monitor)
            self.alarmmin_min.setText(str(alarm.get_min(name)))
            self.alarmmin_max.setText(str(alarm.get_max(name)))
        else:
            self.alarmmin_value.setText("-")
            self.alarmmin_min.setText("-")
            self.alarmmin_max.setText("-")

        self.set_slider_range(self.slider_alarmmax, monitor)
        self.slider_alarmmax.valueChanged.connect(lambda value:
                self.do_alarmmax_moved(value, monitor))
        if alarm.has_valid_minmax(name):
            sliderpos = int((alarm.get_setmax(name) - alarm.get_min(name)) / monitor.step)
            self.slider_alarmmax.setSliderPosition(sliderpos)
            self.do_alarmmax_moved(sliderpos, monitor)
            self.alarmmax_min.setText(str(alarm.get_min(name)))
            self.alarmmax_max.setText(str(alarm.get_max(name)))
        else:
            self.alarmmax_value.setText("-")
            self.alarmmax_min.setText("-")
            self.alarmmax_max.setText("-")

    def apply_selected(self):
        """
        Applies the settings on screen for the selected monitor.
        A monitor is always selected.
        """
        monitor = self.monitors[self.selected]
        alarm = monitor.gui_alarm
        if alarm.has_valid_minmax(monitor.configname):
            alarm.update_min(monitor.configname,
                             self.slider_alarmmin.sliderPosition() * monitor.step + alarm.get_min(monitor.configname))
            alarm.update_max(monitor.configname,
                             self.slider_alarmmax.sliderPosition() * monitor.step + alarm.get_min(monitor.configname))
            # monitor.update_thresholds()

    def reset_selected(self):
        """
        Resets the settings on screen for the selected monitor.
        A monitor is always selected.
        """
        self.show_settings(self.selected)

    '''
    TODO: funcionality for moving monitors to and from montitor bar needs to replace this
    def display_selected(self, slotname):

        # Assign selected to new spot and remove from old spot
        monitor = self.monitors[self.selected]
        plot = self.plots[self.selected]
        if monitor.location == slotname:
            # Plot/monitor is already where it should be on main display
            print(self.selected + " already at " + slotname)
            return
        elif monitor.location != "None" and monitor.location is not None:
            # Plot/monitor is on main display, but somewhere else
            self.monitor_slots[monitor.location].removeWidget(monitor)
            self.plot_slots[monitor.location].removeWidget(plot)
            print(self.selected + " from " + monitor.location + " to " + slotname)
        else:
            # Plot/monitor is not on main display
            self.layout.removeWidget(monitor)
            self.plot_hidden_slots.removeWidget(plot)
            print(self.selected + " from cached to " + slotname)

        # Set the new monitor location and swap with old location
        for (mon_name, plot_name) in zip(self.active_monitors, self.active_plots):
            active_monitor = self.active_monitors[mon_name]
            active_plot = self.active_plots[plot_name]
            if active_monitor.location == slotname:
                self.monitor_slots[slotname].removeWidget(active_monitor)
                self.plot_slots[slotname].removeWidget(active_plot)
                active_monitor.location = monitor.location
                break
        monitor.location = slotname

        self.populate_monitors_and_plots()
    '''

    def populate_monitors(self):
        """
        Populates monitors based on the ones assigned as displayed.
        If the monitor is not displayed, it is shown in the alarms page.
        """
        # Iterate through all monitors and either display on main bar, or put on alarms page
        disp = 0
        hidd = 0
        for name in self.monitors:
            monitor = self.monitors[name]
            if name in self.displayed_monitors:
                # Monitor displayed, so goes on Monitor Bar
                self.monitors_slots.insertWidget(disp, self.monitors[name])
                disp += 1
            else:
                # Monitor not displayed, so goes on Alarms page
                self.layout.addWidget(monitor, int(hidd % 4), 10-int(hidd / 3)) 
                hidd += 1 


    def config_monitors(self):
        """
        Set all monitors into configuration mode.
        Always selects the last monitor as selected by default.
        """
        for name in self.monitors:
            self.monitors[name].config_mode = True
            self.selected = name
        self.select_monitor(self.selected)

    def deconfig_monitors(self):
        """
        Unsets all monitors out of configuration mode.
        """
        for name in self.monitors:
            self.monitors[name].unhighlight()
            self.monitors[name].config_mode = False



