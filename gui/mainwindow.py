#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets

from toolsettings.toolsettings import ToolSettings
from toolbar.toolbar import Toolbar
from monitor.monitor import Monitor
from settings.settings import Settings
from data_filler import DataFiller
from data_handler import DataHandler
from start_stop_worker import StartStopWorker
from menu.menu import Menu
from frozenplots.frozenplots import FrozenPlots

import pyqtgraph as pg
import sys
import time
from pip._internal import self_outdated_check

STOP = -1
AUTOMATIC = 0
ASSISTED = 1

DO_RUN = 1
DONOT_RUN = 0



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, config, esp32, *args, **kwargs):
        """
        Initializes the main window for the MVM GUI. See below for subfunction setup description.
        """

        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('mainwindow.ui', self) # Load the .ui file

        self.config = config
        self.esp32 = esp32

        '''
        Get the toolbar and menu widgets
        '''
        self.bottombar = self.findChild(QtWidgets.QStackedWidget, "bottombar")
        self.toolbar =   self.findChild(QtWidgets.QWidget, "toolbar")
        self.menu =      self.findChild(QtWidgets.QWidget, "menu")

        '''
        Get toolbar widgets
        '''
        self.button_menu =  self.toolbar.findChild(QtWidgets.QPushButton, "button_menu")
        self.label_status = self.toolbar.findChild(QtWidgets.QLabel,      "label_status")

        toolsettings_names = {"toolsettings_1", "toolsettings_2", "toolsettings_3"}
        self.toolsettings = {};

        for name in toolsettings_names:
            toolsettings = self.toolbar.findChild(QtWidgets.QWidget, name)
            toolsettings.connect_config(config)
            self.toolsettings[name] = toolsettings

        '''
        Get menu widgets and connect settings for the menu widget
        '''
        self.button_back =       self.menu.findChild(QtWidgets.QPushButton, "button_back")
        self.button_settings =   self.menu.findChild(QtWidgets.QPushButton, "button_settings")
        self.button_expause =    self.menu.findChild(QtWidgets.QPushButton, "button_expause")
        self.button_inpause =    self.menu.findChild(QtWidgets.QPushButton, "button_inpause")
        self.button_freeze =     self.menu.findChild(QtWidgets.QPushButton, "button_freeze")
        self.button_startstop =  self.menu.findChild(QtWidgets.QPushButton, "button_startstop")
        self.button_autoassist = self.menu.findChild(QtWidgets.QPushButton, "button_autoassist")

        '''
        Connect back and menu buttons to toolbar and menu
        '''
        self.button_back.pressed.connect(self.open_toolbar)
        self.button_menu.pressed.connect(self.open_menu)

        '''
        Instantiate the DataFiller, which takes
        care of filling plots data
        '''
        self.data_filler = DataFiller(config)
        
        '''
        Instantiate DataHandler, which will start a new
        thread to read data from the ESP32. We also connect
        the DataFiller to it, so the thread will pass the
        data directly to the DataFiller, which will
        then display them.
        '''
        self._data_h = DataHandler(config, self.esp32)
        self._data_h.connect_data_filler(self.data_filler)
        self._data_h.start_io_thread()


        '''
        Set up tool settings (bottom bar)

        self.toolsettings[..] are the objects that hold min, max values for a given setting as
        as the current value (displayed as a slider and as a number).
        '''
        toolsettings_names = {"toolsettings_1", "toolsettings_2", "toolsettings_3"}
        self.toolsettings = {};

        for name in toolsettings_names:
            toolsettings = self.findChild(QtWidgets.QWidget, name)
            toolsettings.connect_config(config)
            self.toolsettings[name] = toolsettings

        '''
        Set up data monitor/alarms (side bar)

        self.monitors[..] are the objects that hold monitor values and thresholds for alarm min
        and max. The current value and optional stats for the monitored value (mean, max) are set
        here.
        '''
        monitor_names = {"monitor_top", "monitor_mid", "monitor_bot"}
        self.monitors = {}
        monitor_default = {
                "name": "NoName",
                "min": 0,
                "init": 50,
                "max": 100,
                "step": None,
                "units": None,
                "dec_precision": 2,
                "color": "black",
                "alarmcolor": "red"}

        for name in monitor_names:
            monitor = self.findChild(QtWidgets.QWidget, name)
            self.monitors[name] = self.init_monitor(monitor, name, config, monitor_default)
            
        self.data_filler.connect_monitor('monitor_top', self.monitors['monitor_top'])
        self.data_filler.connect_monitor('monitor_mid', self.monitors['monitor_mid'])
        self.data_filler.connect_monitor('monitor_bot', self.monitors['monitor_bot'])


        '''
        Set up plots (PyQtPlot)

        self.plots[..] are the PyQtPlot objects.
        '''
        self.plots = [];
        self.plots.append(self.findChild(QtWidgets.QWidget, "plot_top"))
        self.plots.append(self.findChild(QtWidgets.QWidget, "plot_mid"))
        self.plots.append(self.findChild(QtWidgets.QWidget, "plot_bot"))
        self.data_filler.connect_plot('monitor_top', self.plots[0])
        self.data_filler.connect_plot('monitor_mid', self.plots[1])
        self.data_filler.connect_plot('monitor_bot', self.plots[2])

        '''
        Set up start/stop auto/min mode buttons.

        Connect each to their respective mode toggle functions.
        The StartStopWorker class takes care of starting and stopping a run
        '''

        self._start_stop_worker = StartStopWorker(
                self,
                self.config,
                self.esp32,
                self.button_startstop,
                self.button_autoassist,
                self.toolbar)

        self.button_startstop.released.connect(self._start_stop_worker.toggle_start_stop)
        self.button_autoassist.released.connect(self._start_stop_worker.toggle_mode)

        '''
        Connect settings button to Settings overlay.
        '''
        self.settings = Settings(config, self)
        self.button_settings.pressed.connect(self.show_settings)

        self.settings.connect_data_handler(self._data_h)
        self.settings.connect_toolsettings(self.toolsettings)
        self.settings.connect_start_stop_worker(self._start_stop_worker)
        self.settings.connect_workers()
        self.settings.load_presets()
        
        '''
        Connect freeze button to FrozenPlots overlay.
        The FrozenPlots class sets up its own plots.
        '''
        self.frozen_plots = FrozenPlots(config, self)
        self.button_freeze.pressed.connect(self.show_frozen_plots)
        
        '''
        Set up monitors in the FrozenPlots overlay, which are
        connected to the LIVE data filler.
        '''
        self.frozen_monitors = {}

        for name in monitor_names:
            monitor = self.frozen_plots.findChild(QtWidgets.QWidget, "frozen_" + name)
            self.frozen_monitors[name] = self.init_monitor(monitor, name, config, monitor_default)
            
        self.data_filler.connect_monitor('monitor_top', self.frozen_monitors['monitor_top'])
        self.data_filler.connect_monitor('monitor_mid', self.frozen_monitors['monitor_mid'])
        self.data_filler.connect_monitor('monitor_bot', self.frozen_monitors['monitor_bot'])

    def init_monitor(self, monitor, name, config, monitor_default):
        entry = config.get(name, monitor_default)
        monitor.setup(
                entry.get("name", monitor_default["name"]),
                setrange=(
                    entry.get("min", monitor_default["min"]),
                    entry.get("init", monitor_default["init"]),
                    entry.get("max", monitor_default["max"])),
                units=entry.get("units", monitor_default["units"]),
                alarmcolor=entry.get("alarmcolor", monitor_default["alarmcolor"]),
                color=entry.get("color", monitor_default["color"]),
                step=entry.get("step", monitor_default["step"]),
                dec_precision=entry.get("dec_precision", monitor_default["dec_precision"]),
                clear_alarm_callback=self.monitor_clear_alarm_callback)
        return monitor

    def monitor_clear_alarm_callback(self, cleared_monitor):
        '''
        There are 2 monitor widgets for each monitored value (one on the
        main window, and one on the "frozen plots" window). This
        function means that when a user clears an alarm on one screen,
        it is cleared on the other one as well.
        '''
        for monitor in self.monitors.values():
            if monitor.name == cleared_monitor.name and monitor is not cleared_monitor:
                monitor.clear_alarm(None)

        for monitor in self.frozen_monitors.values():
            if monitor.name == cleared_monitor.name and monitor is not cleared_monitor:
                monitor.clear_alarm(None)
        
    def open_menu(self):
        self.bottombar.setCurrentIndex(1)

    def open_toolbar(self):
        self.bottombar.setCurrentIndex(0)

    def show_settings(self):
        self.open_toolbar()
        self.settings.show()
        self.settings.tabWidget.setFocus()
        
    def show_frozen_plots(self):
        for name, data in self.data_filler._data.items():
            self.frozen_plots.set_data(name, data)
        
        self.open_toolbar()
        self.frozen_plots.show()

    def closeEvent(self, event):
        self._data_h.stop_io()

