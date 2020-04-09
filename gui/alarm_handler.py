
from PyQt5 import QtCore, QtGui, QtWidgets

from messagebox import MessageBox
from communication.esp32serial import ESP32Alarm, ESP32Warning


class AlarmHandler:
    '''
    This class starts a QTimer dedicated
    to checking is there are any errors
    or warnings coming from ESP32
    '''

    def __init__(self, config, esp32):
        '''
        Constructor

        parameters:
        - config: the dictionary storing the configuration
        - esp32: the esp32serial object
        '''

        self._config = config
        self._esp32 = esp32

        self._alarm_raised = False
        self._warning_raised = False

        self._msg_err = MessageBox()
        self._msg_war = MessageBox()

        self._alarm_timer = QtCore.QTimer()
        self._alarm_timer.timeout.connect(self.handle_alarms)
        self._alarm_timer.start(config["alarminterval"] * 1000)



    def handle_alarms(self):
        '''
        The callback method which is called periodically
        to check if the ESP raised any alarm or warning.
        If an alarm or warning is raised, a pop up
        window appears, showing the list of alarms and
        warnings. If more alarms or warnings add up, the 
        window is updated automatically showing the latest
        errors.
        '''

        # Retrieve alarms and warnings from the ESP
        try:
            esp32alarm = self._esp32.get_alarms()
            esp32warning = self._esp32.get_warnings()
        except Exception as error:
            err_msg = "Severe hardware communication error. "
            err_msg += "Cannot retrieve alarm and warning statuses from hardware."
            msg = MessageBox()
            fn = msg.critical("Critical",
                              err_msg,
                              str(error), 
                              "Communication error",
                              { msg.Retry: lambda: None,
                                msg.Abort: lambda: None })
            fn()

        #
        # ALARMS
        #
        if esp32alarm:
            errors = esp32alarm.strerror_all()
            errors_full = esp32alarm.strerror_all(append_err_no=True)

            if not self._alarm_raised:
                self._alarm_raised = True
                self._msg_err.critical("ALARM",
                             " - ".join(errors),
                             "\n".join(errors_full), 
                             "Alarm received.",
                             { self._msg_err.Ok: lambda: self.ok_worker('alarm'),
                               self._msg_err.Abort: lambda: None},
                             do_not_block=True)
                self._msg_err.open()
            else:
                self._msg_err.setInformativeText(" - ".join(errors))
                self._msg_err.setDetailedText("\n".join(errors_full))
                self._msg_err.raise_()
                self._msg_err.setActiveWindow()


        # 
        # WARNINGS
        # 
        if esp32warning:
            errors = esp32warning.strerror_all()
            errors_full = esp32warning.strerror_all(append_err_no=True)

            if not self._warning_raised:
                self._warning_raised = True
                self._msg_war.warning("WARNING",
                             " - ".join(errors),
                             "\n".join(errors_full), 
                             "Alarm received.",
                             { self._msg_war.Ok: lambda: self.ok_worker('warning'),
                               self._msg_war.Abort: lambda: None },
                             do_not_block=True)
                self._msg_war.open()
            else:
                self._msg_war.setInformativeText(" - ".join(errors))
                self._msg_war.setDetailedText("\n".join(errors_full))
                self._msg_war.raise_()
                self._msg_war.setActiveWindow()

    def ok_worker(self, mode):
        '''
        The callback function called when the alarm 
        or warning pop up window is closed by clicking
        on the Ok button.

        arguments:
        - mode: what this is closing, an 'alarm' or a 'warning'
        '''

        if mode not in ['alarm', 'warning']:
            raise Exception('mode must be alarm or warning.')

        if mode == 'alarm':
            self._alarm_raised = False
        else:
            self._warning_raised = False

        # Reset the alarms/warnings in the ESP
        # If the ESP connection fails at this 
        # time, raise an error box
        try:
            if mode == 'alarm':
                self._esp32.reset_alarms()
            else:
                self._esp32.reset_warnings()
        except Exception as error:
            msg = MessageBox()
            fn = msg.critical("Critical",
                              "Severe hardware communication error",
                              str(error), 
                              "Communication error",
                              { msg.Retry: lambda: self.ok_worker(mode),
                                msg.Abort: lambda: None })
            fn()
        

