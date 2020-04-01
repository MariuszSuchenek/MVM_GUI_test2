#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets

from toolsettings.toolsettings import ToolSettings
from monitor.monitor import Monitor
from settings.settings import Settings
from data_filler import DataFiller
from data_handler import DataHandler
from start_stop_worker import StartStopWorker

import pyqtgraph as pg
import sys
import time

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
                    dec_precision=entry.get("dec_precision", monitor_default["dec_precision"]))
            self.monitors[name] = monitor
        self.data_filler.connect_monitor('monitor_top', self.monitors['monitor_top'])
        self.data_filler.connect_monitor('monitor_mid', self.monitors['monitor_mid'])
        self.data_filler.connect_monitor('monitor_bot', self.monitors['monitor_bot'])
        # Need to add the other monitors...which ones?


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
        self.button_startstop = self.findChild(QtWidgets.QPushButton, "button_startstop")
        self.button_autoassist = self.findChild(QtWidgets.QPushButton, "button_autoassist")
        
        self._start_stop_worker = StartStopWorker(
                self, 
                self.config, 
                self.esp32, 
                self.button_startstop, 
                self.button_autoassist)

        self.button_startstop.released.connect(self._start_stop_worker.toggle_start_stop)
        self.button_autoassist.released.connect(self._start_stop_worker.toggle_mode)

        '''
        Connect settings button to Settings overlay.
        '''
        self.settings = Settings(config, self)
        self.button_settings = self.findChild(QtWidgets.QPushButton, "button_settings")
        self.button_settings.pressed.connect(self.settings.show)

        self.settings.connect_data_handler(self._data_h)
        self.settings.connect_toolsettings(self.toolsettings)
        self.settings.connect_start_stop_worker(self._start_stop_worker)
        self.settings.connect_workers()
        self.settings.load_presets_auto()
        self.settings.load_presets_assist()

    def closeEvent(self, event):
        self._data_h.stop_io()

