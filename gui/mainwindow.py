#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets


from maindisplay.maindisplay import MainDisplay
from settings.settings import Settings

from toolbar.toolbar import Toolbar
from menu.menu import Menu
from settings.settingsbar import SettingsBar

from toolsettings.toolsettings import ToolSettings
from monitor.monitor import Monitor
from data_filler import DataFiller
from data_handler import DataHandler
from start_stop_worker import StartStopWorker

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
        Get the toppane and child pages
        '''
        self.toppane  = self.findChild(QtWidgets.QStackedWidget, "toppane")
        self.main     = self.findChild(QtWidgets.QWidget,        "main")
        self.settings = self.findChild(QtWidgets.QWidget,        "settings")
        self.startup  = self.findChild(QtWidgets.QWidget,        "startup")

        '''
        Get the bottombar and child pages
        '''
        self.bottombar   = self.findChild(QtWidgets.QStackedWidget, "bottombar")
        self.toolbar     = self.findChild(QtWidgets.QWidget,        "toolbar")
        self.menu        = self.findChild(QtWidgets.QWidget,        "menu")
        self.frozen_bot  = self.findChild(QtWidgets.QWidget,        "frozenplots_bottom")
        self.settingsbar = self.findChild(QtWidgets.QWidget,        "settingsbar")
        self.blank       = self.findChild(QtWidgets.QWidget,        "blank")

        '''
        Get the stackable bits on the right
        '''
        self.rightbar     = self.main.findChild(QtWidgets.QStackedWidget, "rightbar")
        self.monitors_bar = self.main.findChild(QtWidgets.QWidget,        "three_monitors")
        self.frozen_right = self.main.findChild(QtWidgets.QWidget,        "frozenplots_right")

        '''
        Get startup buttons
        '''
        self.button_new_patient    = self.startup.findChild(QtWidgets.QPushButton, "button_new_patient")
        self.button_resume_patient = self.startup.findChild(QtWidgets.QPushButton, "button_resume_patient")

        '''
        Get toolbar widgets
        '''
        self.button_menu  = self.toolbar.findChild(QtWidgets.QPushButton, "button_menu")
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
        Get frozen plots bottom bar widgets and connect
        '''
        self.button_unfreeze =   self.frozen_bot.findChild(QtWidgets.QPushButton, "button_unfreeze")

        '''
        Connect startup buttons
        '''
        self.button_resume_patient.pressed.connect(self.resume_patient):
        self.button_new.pressed.connect(self.new_patient):

        '''
        Connect back and menu buttons to toolbar and menu
        '''
        self.button_back.pressed.connect(self.open_toolbar)
        self.button_menu.pressed.connect(self.open_menu)
        self.button_freeze.pressed.connect(self.freeze_plots)
        self.button_unfreeze.pressed.connect(self.unfreeze_plots)
        self.button_settings.pressed.connect(self.open_settings)

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
            monitor = self.main.findChild(QtWidgets.QWidget, name)
            self.monitors[name] = self.init_monitor(monitor, name, config, monitor_default)
            
        self.data_filler.connect_monitor('monitor_top', self.monitors['monitor_top'])
        self.data_filler.connect_monitor('monitor_mid', self.monitors['monitor_mid'])
        self.data_filler.connect_monitor('monitor_bot', self.monitors['monitor_bot'])


        '''
        Set up plots (PyQtPlot)

        self.plots[..] are the PyQtPlot objects.
        '''
        self.plots = [];
        self.plots.append(self.main.findChild(QtWidgets.QWidget, "plot_top"))
        self.plots.append(self.main.findChild(QtWidgets.QWidget, "plot_mid"))
        self.plots.append(self.main.findChild(QtWidgets.QWidget, "plot_bot"))
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
        self.settings.connect_workers(self)
        self.settings.load_presets()
        
        '''
        Connect buttons on freeze menus
        '''
        self.frozen_bot.connect_workers(self.data_filler, self.plots)
        self.frozen_right.connect_workers(self.plots)
        
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
                dec_precision=entry.get("dec_precision", monitor_default["dec_precision"]))
        return monitor

    def open_menu(self):
        self.bottombar.setCurrentWidget(self.menu)

    def open_toolbar(self):
        self.bottombar.setCurrentWidget(self.toolbar)

    def open_settings(self):
        self.bottombar.setCurrentWidget(self.settingsbar)
        self.toppane.setCurrentWidget(self.settings)
        self.settings.tabWidget.setFocus()

    def open_main(self):
        self.toppane.setCurrentWidget(self.main)
        
    def freeze_plots(self):
        self.data_filler.freeze()
        self.rightbar.setCurrentWidget(self.frozen_right)
        self.bottombar.setCurrentWidget(self.frozen_bot)

    def new_patient(self):
        self.open_toolbar()
        self.open_main()

    def resume_patient(self):
        self.open_toolbar()
        self.open_main()
        
    def unfreeze_plots(self):
        self.data_filler.unfreeze()
        self.rightbar.setCurrentWidget(self.monitors_bar)
        self.open_menu()

    def closeEvent(self, event):
        self._data_h.stop_io()

