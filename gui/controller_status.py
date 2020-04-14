'''
Constanty checks the status of the ESP controller.
'''

from PyQt5.QtCore import QTimer
import sys
from messagebox import MessageBox


class ControllerStatus:
    '''
    This class constanty checks
    the status of the ESP controller.
    Is it running? In which mode?
    Has it entered backup mode?
    '''

    def __init__(self, config, esp32, settings, start_stop_worker):
        '''
        Constructor

        arguments:
        - config: the dictionary storing the configuration
        - esp32: the esp32serial object
        - settings: the Settings panel
        - start_stop_worker: the StartStopWorker class
                             that takes care of start/stop operations
        '''

        self._config = config
        self._esp32 = esp32
        self._settings = settings
        self._start_stop_worker = start_stop_worker

        self._backup_ackowledged = False

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

        if not int(self._esp32.get('run')):
            return

        for param, esp_name in self._config['esp_settable_param'].items():
            print('Reading Settings parameters from ESP:', param, self._esp32.get(esp_name))
            self._settings.update_spinbox_value(param, int(self._esp32.get(esp_name)))


    def _esp32_io(self):
        '''
        The callback function called every time the
        QTimer times out.
        '''

        try:
            self._call_esp32()
        except Exception as error:
            self._open_comm_error(str(error))


    def _call_esp32(self):
        '''
        Gets the run, mode and backup vairables
        from the ESP, and passes them to the
        StartStopWorker class.
        '''

        self._start_stop_worker.set_run(int(self._esp32.get('run')))
        self._start_stop_worker.set_mode(int(self._esp32.get('mode')))

        if int(self._esp32.get('backup')):
            if not self._backup_ackowledged:
                self._open_backup_warning()
        else:
            self._backup_ackowledged = False


    def _open_backup_warning(self):
        '''
        Opens a warning message if the ventilator
        changed from assisted to automatic ventilation.
        '''
        msg = MessageBox()

        callbacks = {msg.Ok: self._acknowlege_backup}

        fn = msg.warning("CHANGE OF MODE",
                         "The ventilator changed from assisted to automatic mode.",
                         "The microcontroller raised the backup flag.",
                         "",
                         callbacks)
        fn()


    def _open_comm_error(self, error):
        '''
        Opens a message window if there is a communication error.
        '''
        msg = MessageBox()

        # TODO: find a good exit point
        callbacks = {msg.Retry: self._restart_timer,
                     msg.Abort: lambda: sys.exit(-1)}

        fn = msg.critical("COMMUNICATION ERROR",
                          "CANNOT COMMUNICATE WITH THE HARDWARE",
                          "Check cable connections then click retry.\n"+error,
                          "COMMUNICATION ERROR",
                          callbacks)
        fn()


    def _acknowlege_backup(self):
        '''
        Sets _backup_ackowledged to True
        '''
        self._backup_ackowledged = True


    def _start_timer(self):
        '''
        Starts the QTimer.
        '''
        self._timer.start(self._config["status_sampling_interval"] * 1000)


    def _stop_timer(self):
        '''
        Stops the QTimer.
        '''
        self._timer.stop()


    def _restart_timer(self):
        '''
        Restarts the QTimer if the QTimer is active,
        or simply starts the QTimer
        '''
        if self._timer.isActive():
            self._stop_timer()

        self._start_timer()

