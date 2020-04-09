
from PyQt5 import QtCore, QtGui, QtWidgets

from messagebox import MessageBox
from communication.esp32serial import ESP32Alarm


class AlarmHandler:

    def __init__(self, config, esp32):
        self._config = config
        self._esp32 = esp32

        self._alarm_raised = False


        self._msg = MessageBox()

        self._alarm_timer = QtCore.QTimer()
        self._alarm_timer.timeout.connect(self.handle_alarms)
        self._alarm_timer.start(config["alarminterval"] * 1000)



    def handle_alarms(self):

        esp32alarm = self._esp32.get_alarms()
        print('esp32alarm', esp32alarm)	

        if esp32alarm:
            errors = esp32alarm.strerror_all()

            if not self._alarm_raised:
                self._msg.critical("ALARM",
                             " - ".join(errors),
                             "\n".join(errors), 
                             "Alarm received.",
                             { self._msg.Ok: lambda: self.ok_worker,
                               self._msg.Abort: lambda: None},
                             do_not_block=True)
                self._msg.open()
            else:
                self._msg.setInformativeText(" - ".join(errors))

    def ok_worker(self, btn):

        self._alarm_raised = False

        # Reset the alarms in the ESP
        try:
            self._esp32.reset_alarms()
        except Exception as error:
            msg = MessageBox()
            fn = msg.critical("Critical",
                              "Severe hardware communication error",
                              str(error), 
                              "Communication error",
                              { msg.Ok: lambda: None })
            fn()
        

