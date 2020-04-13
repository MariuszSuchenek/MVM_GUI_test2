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

    def __init__(self, config, esp32, settings):
        '''
        Constructor

        arguments:
        - config: the dictionary storing the configuration
        - esp32: the esp32serial object
        - settings: the Settings panel
        '''

        self._config = config
        self._esp32 = esp32
        self._settings = settings

        self._init_settings_panel()

        self._timer = QTimer()
        self._timer.timeout.connect(self._esp32_io)
        self._start_timer()


    def _init_settings_panel(self):
        '''
        Initializes the settings values.
        If the ESP if running, read the current parameters
        and set them in the Setting panel. 
        If the ESP is not running, don't do anything here,
        and leave the default behaviour.
        '''
        
        if not self._esp32.get('run'):
            return

        for param, esp_name in self._config['esp_settable_param'].items():
            print('Reading Settings parameters from ESP:', param, self._esp32.get(esp_name))
            self._settings.update_spinbox_value(param, self._esp32.get(esp_name))


    def _esp32_io(self):
        return

    def _start_timer(self):
        self._timer.start()




 