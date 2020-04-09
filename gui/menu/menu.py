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

        self.button_expause.pressed.connect(lambda: self.paused_pressed('pause_exhale'))
        self.button_expause.released.connect(lambda: self.paused_released('pause_exhale'))

        self.button_inspause.pressed.connect(lambda: self.paused_pressed('pause_inhale'))
        self.button_inspause.released.connect(lambda: self.paused_released('pause_inhale'))


    def connect_datahandler_config(self, data_h, config):
        '''
        Passes the data handler and the confi dict to this class.
        '''
        self._data_h = data_h
        self._config = config

    def is_configured(self):
        return hasattr(self, "_data_h") and hasattr(self, "_config")

    def paused_pressed(self, mode):
        '''
        Called when either the inspiration ot expiration pause
        buttons are pressed.
        '''
        if not self.is_configured():
            raise Exception('Need to call connect_config_esp first.')
        if mode not in ['pause_exhale', 'pause_inhale']:
            raise Exception('Can only call paused_pressed with pause_exhale or pause_inhale.')


        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(lambda: self.send_signal(mode=mode, pause=True)) 
        self._timer.start(self._config['expinsp_setinterval'] * 1000)


    def paused_released(self, mode):
        '''
        Called when either the inspiration ot expiration pause
        buttons are released.
        '''
        if not self.is_configured():
            raise Exception('Need to call connect_config_esp first.')
        if mode not in ['pause_exhale', 'pause_inhale']:
            raise Exception('Can only call paused_pressed with pause_exhale or pause_inhale.')

        self.stop_timer()

        self.send_signal(mode=mode, pause=False)


    def send_signal(self, mode, pause):
        '''
        Sends signal the appropriate signal the ESP
        to pause inpiration or expiration. 
        '''
        try:
            if not self._data_h.set_data(mode, int(pause)):
                raise Exception('Call to set_data failed.')
        except Exception as error:
            msg = MessageBox()
            fn = msg.critical("Critical",
                              "Severe hardware communication error",
                              str(error), 
                              "Communication error",
                              { msg.Ok: lambda: self.stop_timer() })
            fn()

    def stop_timer(self):
        '''
        Stops the QTimer which sends 
        signals to the ESP
        '''
        if hasattr(self, '_timer'):
            self._timer.stop()

