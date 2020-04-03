#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets
import os
import yaml

from frozenplots.frozen_data_filler import FrozenDataFiller

class FrozenPlots(QtWidgets.QMainWindow):
    def __init__(self, config, *args):
        """
        Initialized the "frozen-in-time" plots overlay widget.
        """
        super(FrozenPlots, self).__init__(*args)
        uic.loadUi("frozenplots/frozenplots.ui", self)

        self._config = config
        
        self._frozen_filler = FrozenDataFiller(config)
        
        self.button_back.clicked.connect(self.close_frozen_worker)
        self.button_reset.clicked.connect(self.reset_zoom_worker)

        # Plots are connected here.
        self.plots = []
        self.plots.append(self.findChild(QtWidgets.QWidget, "frozen_plot_top"))
        self.plots.append(self.findChild(QtWidgets.QWidget, "frozen_plot_mid"))
        self.plots.append(self.findChild(QtWidgets.QWidget, "frozen_plot_bot"))
        self._frozen_filler.connect_plot('monitor_top', self.plots[0])
        self._frozen_filler.connect_plot('monitor_mid', self.plots[1])
        self._frozen_filler.connect_plot('monitor_bot', self.plots[2])

        # Monitors are connected by mainwindow.MainWindow, as they are linked
        # to the LIVE data, not the frozen data.
        
    def set_data(self, name, data):
        '''
        Pass on new waveforms data to the plots.
        '''
        self._frozen_filler.set_data(name, data)
        
    def reset_zoom_worker(self):
        '''
        Resrt plots to their default zoom state.
        '''
        for plot in self.plots:
            plot.autoRange()
        
    def close_frozen_worker(self):
        '''
        Close the frozen plots overlay.
        '''
        self.close()