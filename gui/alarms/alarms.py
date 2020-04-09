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

    def connect_monitors_and_plots(self, mainparent):
        """
        Grabs monitors, plots, and their corresponding display slots from the main window.

        mainparent: Reference to the main window.
        """
        self.mainparent = mainparent
        self.monitors = mainparent.monitors
        self.monitor_slots = mainparent.monitor_slots
        self.plots = mainparent.plots
        self.plot_slots = mainparent.plot_slots
        self.plot_hidden_slots = mainparent.plot_hidden_slots

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
                monitor.clear_alarm()
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
        slider.setMinimum(0)
        slider.setMaximum((monitor.maximum - monitor.minimum) / monitor.step)
        slider.setSingleStep(monitor.step)
        slider.setPageStep(slider.maximum() / 2)

    def do_alarmmin_moved(self, slidervalue, monitor):
        """
        A slot for when the minimum alarm slider moves.

        slidervalue: The physical value on the slider.
        monitor: Reference to the monitor to set the slider value.
        """
        # Prevent min > max
        slidervalue = min(self.slider_alarmmax.sliderPosition(), slidervalue)
        value = slidervalue * monitor.step + monitor.minimum
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
        slidervalue = max(self.slider_alarmmin.sliderPosition(), slidervalue)
        value = slidervalue * monitor.step + monitor.minimum
        self.alarmmax_value.setText("Alarm max: " + str(value))
        self.slider_alarmmax.setValue(slidervalue)
        self.slider_alarmmax.setSliderPosition(slidervalue)

    def show_settings(self, name):
        """
        Display settins for a given named monitor.

        name: The config name of the monitor.
        """
        monitor = self.monitors[name]
        self.label_alarmname.setText(monitor.name)
        self.label_alarmname.setStyleSheet("QLabel { color: " + monitor.color + "; background-color: black}")

        self.alarmmin_min.setText(str(monitor.minimum))
        self.alarmmin_max.setText(str(monitor.maximum))
        self.set_slider_range(self.slider_alarmmin, monitor)
        self.slider_alarmmin.valueChanged.connect(lambda value:
                self.do_alarmmin_moved(value, monitor))
        sliderpos = int((monitor.set_minimum - monitor.minimum) / monitor.step)
        self.slider_alarmmin.setSliderPosition(sliderpos)
        self.do_alarmmin_moved(sliderpos, monitor)

        self.alarmmax_min.setText(str(monitor.minimum))
        self.alarmmax_max.setText(str(monitor.maximum))
        self.set_slider_range(self.slider_alarmmax, monitor)
        self.slider_alarmmax.valueChanged.connect(lambda value:
                self.do_alarmmax_moved(value, monitor))
        sliderpos = int((monitor.set_maximum - monitor.minimum) / monitor.step)
        self.slider_alarmmax.setSliderPosition(sliderpos)
        self.do_alarmmax_moved(sliderpos, monitor)

    def apply_selected(self):
        """
        Applies the settings on screen for the selected monitor.
        A monitor is always selected.
        """
        monitor = self.monitors[self.selected]
        monitor.set_minimum = self.slider_alarmmin.sliderPosition() * monitor.step + monitor.minimum
        monitor.set_maximum = self.slider_alarmmax.sliderPosition() * monitor.step + monitor.minimum
        monitor.refresh()

    def reset_selected(self):
        """
        Resets the settings on screen for the selected monitor.
        A monitor is always selected.
        """
        self.show_settings(self.selected)

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
        for (active_monitor, active_plot) in zip(self.active_monitors, self.active_plots):
            if active_monitor.location == slotname:
                self.monitor_slots[slotname].removeWidget(active_monitor)
                self.plot_slots[slotname].removeWidget(active_plot)
                active_monitor.location = monitor.location
                break
        monitor.location = slotname

        self.populate_monitors_and_plots()

    def populate_monitors_and_plots(self):
        """
        Populates plots and monitors based on the ones assigned to a particular display slot pair.
        If the monitor/plot pair is not displayed, it is shown in the alarms page.
        """
        # Get all active plots and monitors and put the remaining monitors on the alarms page
        self.active_plots = []
        self.active_monitors = []
        for (i, name) in enumerate(self.monitors):
            monitor = self.monitors[name]
            plot = self.plots[name]
            self.layout.addWidget(monitor, int(i % 3), 10-int(i / 3)) 
            self.plot_hidden_slots.addWidget(plot, i)
            for slotname in self.plot_slots:
                if monitor.location == slotname:
                    self.monitor_slots[slotname].addWidget(monitor, 0, 0)
                    self.plot_slots[slotname].addWidget(plot, 0, 0)
                    self.active_monitors.append(monitor)
                    self.active_plots.append(plot)
                    break

        return (self.active_monitors, self.active_plots)

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



