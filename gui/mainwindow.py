#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets

from toolsettings.toolsettings import ToolSettings
from monitor.monitor import Monitor
from settings.settings import Settings
from data_filler import DataFiller
from data_handler import DataHandler

import pyqtgraph as pg
import sys
import time


class MainWindow(QtWidgets.QMainWindow):
    MODE_STOP   = 0
    MODE_AUTO   = 1
    MODE_ASSIST = 2
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
        self.mode = self.MODE_STOP # 0 is stop, 1 is auto, 2 is assisted
        self.button_startauto = self.findChild(QtWidgets.QPushButton, "button_startauto")
        self.button_startman = self.findChild(QtWidgets.QPushButton, "button_startman")
        self.button_startauto.pressed.connect(self.toggle_automatic)
        self.button_startman.pressed.connect(self.toggle_assisted)

        '''
        Set up data monitor/alarms (side bar)

        self.monitors[..] are the objects that hold monitor values and thresholds for alarm min
        and max. The current value and optional stats for the monitored value (mean, max) are set
        here.
        '''
        monitor_names = {"monitor_top", "monitor_mid", "monitor_bot"};
        self.monitors = {};
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
        self.data_filler.connect_monitor(config['plot_top_var'], self.monitors['monitor_top'])
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
        self._data_h.start_io_thread()

    def closeEvent(self, event):
        self._data_h.stop_io()

    def start_button_pressed(self, button):
        self.button_startman.setDisabled(True)
        self.button_startauto.setEnabled(False)
        self.button_startman.repaint()
        self.button_startauto.repaint()
        text = button.text()
        text = text.replace('Start', 'Stop')
        button.setText(text)

    def stop_button_pressed(self, button):
        button.setDown(False)
        currentMode = button.text().split(' ')[1].upper()
        confirmation = QtWidgets.QMessageBox.warning(
            self, 
            '**STOPPING AUTOMATIC MODE**', 
            "Are you sure you want to STOP " + currentMode + " MODE?", 
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, 
            QtWidgets.QMessageBox.Cancel)
        
        if confirmation == QtWidgets.QMessageBox.Ok:
            self.mode = self.MODE_STOP
            text = button.text()
            text = text.replace('Stop', 'Start')
            button.setText(text)
            self.button_startauto.setEnabled(True)
            self.button_startman.setEnabled(True)
            self.button_startman.repaint()
            self.button_startauto.repaint()

    def button_timeout(self):
        print('Setting timeout')
        timeout = 1000
        # Set timeout for being able to stop this mode
        if 'start_mode_timeout' in self.config:
            timeout = self.config['start_mode_timeout']
            # set maximum timeout
            if timeout > 3000: 
                timeout = 3000
        return timeout
            
    def toggle_automatic(self):
        """
        Toggles between automatic mode (1) and stop (0).

        Changes text from "Start" to "Stop" and en/disables assisted button depending on mode.
        """
        print('Current mode: {}'.format(self.mode))
        if self.mode == self.MODE_STOP:
            self.mode = self.MODE_AUTO
            self.start_button_pressed(self.button_startauto)

            QtCore.QTimer.singleShot(self.button_timeout(), lambda: ( 
                     self.button_startauto.setDisabled(False)))

        else:
            self.stop_button_pressed(self.button_startauto)

    def toggle_assisted(self):
        """
        Toggles between assisted mode (2) and stop (0).

        Changes text from "Start" to "Stop" and en/disables automatic button depending on mode.
        """
        if self.mode == self.MODE_STOP:
            self.mode = self.MODE_ASSIST
            self.start_button_pressed(self.button_startman)
            
            QtCore.QTimer.singleShot(self.button_timeout(), lambda: ( 
                    self.button_startman.setDisabled(False)))

        else:
            self.stop_button_pressed(self.button_startman)

