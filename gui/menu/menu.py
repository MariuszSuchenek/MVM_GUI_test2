#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore
from messagebox import MessageBox

class Menu(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the Menu widget.

        Grabs child widgets.
        """
        super(Menu, self).__init__(*args)
        uic.loadUi("menu/menu.ui", self)

        self._configured = False

        self.button_expause.pressed.connect(lambda: self.paused_pressed('pause_exhale'))
        self.button_expause.released.connect(lambda: self.paused_released('pause_exhale'))

        self.button_inspause.pressed.connect(lambda: self.paused_pressed('pause_inhale'))
        self.button_inspause.released.connect(lambda: self.paused_released('pause_inhale'))


    def connect_datahandler_config(self, data_h, config):
        '''
        Passes the data handler and the confi dict to this class.
        '''
        self._configured = True
        self._data_h = data_h
        self._config = config

    def paused_pressed(self, mode):
        '''
        Called when either the inspiration ot expiration pause
        buttons are pressed.
        '''
        if not self._configured:
            raise Exception('Need to call connect_config_esp first.')
        if mode not in ['pause_exhale', 'pause_inhale']:
            raise Exception('Can only call paused_pressed with pause_exhale or pause_inhale.')


        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(lambda: self.send_signal(mode)) 
        self._timer.start(self._config['expinsp_setinterval'])


    def paused_released(self, mode):
        '''
        Called when either the inspiration ot expiration pause
        buttons are released.
        '''
        if not self._configured:
            raise Exception('Need to call connect_config_esp first.')
        if mode not in ['pause_exhale', 'pause_inhale']:
            raise Exception('Can only call paused_pressed with pause_exhale or pause_inhale.')

        if hasattr(self, '_timer'):
            self._timer.stop()


    def send_signal(self, mode):
        '''
        Sends signal the appropriate signal the ESP
        to pause inpiration or expiration. 
        '''
        if not self._data_h.set_data(mode, 1):
            msg = MessageBox()
            fn = msg.critical("Critical",
                              "Severe hardware communication error",
                              "Cannot set %s to ESP32." % mode, 
                              "Communication error",
                              { msg.Ok: lambda: self.paused_released(mode) })
            fn()

