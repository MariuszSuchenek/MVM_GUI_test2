
from PyQt5 import QtCore, QtGui, QtWidgets

from messagebox import MessageBox
from communication.esp32serial import ESP32Alarm, ESP32Warning


class AlarmHandler:

    def __init__(self, config, esp32):
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

        #
        # ALARMS
        #
        esp32alarm = self._esp32.get_alarms()
        print('esp32alarm', esp32alarm)	

        if esp32alarm:
            errors = esp32alarm.strerror_all()

            if not self._alarm_raised:
                self._alarm_raised = True
                self._msg_err.critical("ALARM",
                             " - ".join(errors),
                             "\n".join(errors), 
                             "Alarm received.",
                             { self._msg_err.Ok: lambda: self.ok_worker('alarm'),
                               self._msg_err.Abort: lambda: None},
                             do_not_block=True)
                self._msg_err.open()
            else:
                self._msg_err.setInformativeText(" - ".join(errors))
                self._msg_err.setDetailedText("\n".join(errors))


        #
        # WARNINGS
        #
        esp32warnings = self._esp32.get_warnings()
        print('esp32warnings', esp32warnings) 

        if esp32warnings:
            errors = esp32warnings.strerror_all()

            if not self._warning_raised:
                self._warning_raised = True
                self._msg_war.warning("WARNING",
                             " - ".join(errors),
                             "\n".join(errors), 
                             "Alarm received.",
                             { self._msg_war.Ok: lambda: self.ok_worker('warning'),
                               self._msg_war.Abort: lambda: None},
                             do_not_block=True)
                self._msg_war.open()
            else:
                self._msg_war.setInformativeText(" - ".join(errors))
                self._msg_war.setDetailedText("\n".join(errors))

    def ok_worker(self, mode):

        if mode not in ['alarm', 'warning']:
            raise Exception('mode must be alarm or warning.')

        if mode == 'alarm':
            self._alarm_raised = False
        else:
            self._warning_raised = False

        # Reset the alarms in the ESP
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
                              { msg.Ok: lambda: None })
            fn()
        

