'''
Constanty checks the status of the ESP controller.
'''

# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer

from messagebox import MessageBox


class ControllerStatus:
    '''
    This class constanty checks 
    the status of the ESP controller.
    Is it running? In which mode?
    Has it entered backup mode?
    '''

    def __init__(self, config, esp32):
        '''
        Constructor

        arguments:
        - config: the dictionary storing the configuration
        - esp32: the esp32serial object
        '''

        self._config = config
        self._esp32 = esp32

        self._init_settings_panel()

        self._timer = QTimer()
        self._timer.timeout.connect(self._esp32_io)
        self._start_timer()

    def _init_settings_panel(self):
        return

    def _esp32_io(self):
        return




 