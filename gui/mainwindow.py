#!/usr/bin/python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets

from toolsettings.toolsettings import ToolSettings
from monitor.monitor import Monitor
from settings.settings import Settings
from data_filler import DataFiller
from data_handler import DataHandler

import pyqtgraph as pg
import sys


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, config, esp32, *args, **kwargs):
        """
        Initializes the main window for the MVM GUI. See below for subfunction setup description.
        """

        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('mainwindow.ui', self) # Load the .ui file

        self.config = config

        self.data_filler = DataFiller(config['nsamples'])
        self.esp32 = esp32

        '''
        Set up tool settings (bottom bar)

        self.toolsettings[..] are the objects that hold min, max values for a given setting as
        as the current value (displayed as a slider and as a number).
        '''
        self.toolsettings = [];
        self.toolsettings.append(self.findChild(QtWidgets.QWidget, "toolsettings_1"))
        self.toolsettings.append(self.findChild(QtWidgets.QWidget, "toolsettings_2"))
        self.toolsettings.append(self.findChild(QtWidgets.QWidget, "toolsettings_3"))

        self.toolsettings[0].setup("O<sub>2</sub> conc.", setrange=(21, 40, 100), units="%")
        self.toolsettings[1].setup("PEEP",                setrange=(0,   5, 50),  units="cmH<sub>2</sub>O")
        self.toolsettings[2].setup("Resp. Rate",          setrange=(4,  12, 100), units="b/min")

        '''
        Set up start/stop auto/min mode buttons.

        Connect each to their respective mode toggle functions.
        '''
        self.mode = 0 # 0 is stop, 1 is auto, 2 is manual
        self.button_startauto = self.findChild(QtWidgets.QPushButton, "button_startauto")
        self.button_startman = self.findChild(QtWidgets.QPushButton, "button_startman")
        self.button_startauto.pressed.connect(self.toggle_automatic)
        self.button_startman.pressed.connect(self.toggle_manual)

        '''
        Set up data monitor/alarms (side bar)

        self.monitors[..] are the objects that hold monitor values and thresholds for alarm min
        and max. The current value and optional stats for the monitored value (mean, max) are set
        here.
        '''
        self.monitors = [];
        self.monitors.append(self.findChild(QtWidgets.QWidget, "monitor_top"))
        self.monitors.append(self.findChild(QtWidgets.QWidget, "monitor_mid"))
        self.monitors.append(self.findChild(QtWidgets.QWidget, "monitor_bot"))

        self.monitors[0].setup("RR",            setrange=(5, 12, 30),    units="(b/min)")
        self.monitors[1].setup("O<sub>2</sub>", setrange=(35, 41, 45),   units="(b/min)")
        self.monitors[2].setup("MVe",           setrange=(50, 71, 400),  units="(b/min)")

        self.data_filler.connect_monitor(config['plot_top_var'], self.monitors[2])
        # Need to add the other monitors...which ones?


        '''
        Set up plots (PyQtPlot)

        self.plots[..] are the PyQtPlot objects.
        '''
        self.plots = [];
        self.plots.append(self.findChild(QtWidgets.QWidget, "plot_top"))
        self.plots.append(self.findChild(QtWidgets.QWidget, "plot_mid"))
        self.plots.append(self.findChild(QtWidgets.QWidget, "plot_bot"))
        self.data_filler.connect_plot(config['plot_top_var'], self.plots[0])
        self.data_filler.connect_plot(config['plot_mid_var'], self.plots[1])
        self.data_filler.connect_plot(config['plot_bot_var'], self.plots[2])

        '''
        Connect settings button to Settings overlay.
        '''
        self.settings = Settings(self)
        self.button_settings = self.findChild(QtWidgets.QPushButton, "button_settings")
        self.button_settings.pressed.connect(self.settings.show)

        '''
        Instantiate DataHandler, which will start a new
        thread to read data from the ESP32. We also connect
        the DataFiller to it, so the thread will pass the
        data directly to the DataFiller, which will
        then display them.
        '''
        self._data_h = DataHandler(config, self.esp32)
        self._data_h.connect_data_filler(self.data_filler)
        if config['read_from_esp']:
            self._data_h.start_io_thread()

    def toggle_automatic(self):
        """
        Toggles between automatic mode (1) and stop (0).

        Changes text from "Start" to "Stop" and en/disables manual button depending on mode.
        """
        if self.mode == 0:
            self.mode = 1
            self.button_startauto.setText("Stop Automatic")
            self.button_startman.setDisabled(True)
        else:
            self.mode = 0
            self.button_startauto.setText("Start Automatic")
            self.button_startman.setEnabled(True)

    def toggle_manual(self):
        """
        Toggles between manual mode (2) and stop (0).

        Changes text from "Start" to "Stop" and en/disables automatic button depending on mode.
        """
        if self.mode == 0:
            self.mode = 2
            self.button_startman.setText("Stop Manual")
            self.button_startauto.setDisabled(True)
        else:
            self.mode = 0
            self.button_startman.setText("Start Manual")
            self.button_startauto.setEnabled(True)
