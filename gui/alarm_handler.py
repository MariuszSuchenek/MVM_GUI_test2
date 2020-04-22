
from PyQt5 import QtCore, QtGui, QtWidgets

from messagebox import MessageBox
from communication.esp32serial import ESP32Alarm, ESP32Warning

class SnoozeButton:
    '''
    '''
    ERROR = 0
    WARNING = 1

    def __init__(self, esp32, alarm_h, alarmsnooze):
        self._esp32 = esp32
        self._alarm_h = alarm_h
        self._alarmsnooze = alarmsnooze

        self._alarmsnooze.hide()
        self._code = None
        self._mode = None

        self._alarmsnooze.clicked.connect(self._on_click_snooze)
        self._alarmsnooze.setStyleSheet('background-color: blue; color : white; font-weight: bold;')

    def set_code(self, code):
        self._code = code
        self._alarmsnooze.setText('Snooze %s' % str(self._code))

    def set_mode(self, mode):
        self._mode = mode

    def show(self):
        self._alarmsnooze.show()

    def _on_click_snooze(self):
        '''
        The callback function called when the alarm
        or warning pop up window is closed by clicking
        on the Ok button.

        arguments:
        - mode: what this is closing, an 'alarm' or a 'warning'
        '''

        if self._mode not in [self.WARNING, self.ERROR]:
            raise Exception('mode must be alarm or warning.')

        # Reset the alarms/warnings in the ESP
        # If the ESP connection fails at this
        # time, raise an error box
        try:
            if self._mode == self.ERROR:
                self._esp32.snooze_hw_alarm(self._code)
                self._alarm_h.snooze_alarm(self._code)
            else:
                self._esp32.reset_warnings()
                self._alarm_h.snooze_warning(self._code)
        except Exception as error:
            msg = MessageBox()
            fn = msg.critical("Critical",
                              "Severe hardware communication error",
                              str(error),
                              "Communication error",
                              { msg.Retry: lambda: self.ok_worker(mode),
                                msg.Abort: lambda: None })
            fn()

class AlarmButton(QtGui.QPushButton):
    '''
    '''
    ERROR = 0
    WARNING = 1

    def __init__(self, mode, code, errstr, label, snooze_btn):
        super(AlarmButton, self).__init__()
        self._mode = mode
        self._code = code
        self._errstr = errstr
        self._label = label
        self._snooze_btn = snooze_btn

        self.clicked.connect(self.on_click_event)

        if self._mode == self.ERROR:
            self._bkg_color = 'red'
        elif self._mode == self.WARNING:
            self._bkg_color = 'orange'
        else:
            raise Exception('Option %s not supported'.format(self._mode))

        self.setText(str(code))

        self.setStyleSheet('background-color: %s; color : white; border: 0.5px solid white; font-weight: bold;' % self._bkg_color)

        self.setMaximumWidth(35)

    def on_click_event(self):

        # Set the label showing the alarm name
        self._label.setStyleSheet('QLabel { background-color : %s; color : white; font-weight: bold;}' % self._bkg_color)
        self._label.setText(self._errstr)
        self._label.show()

        self._activate_snooze_btn()

    def _activate_snooze_btn(self):
        self._snooze_btn.set_mode(self._mode)
        self._snooze_btn.set_code(self._code)
        self._snooze_btn.show()


class AlarmHandler:
    '''
    This class starts a QTimer dedicated
    to checking is there are any errors
    or warnings coming from ESP32
    '''

    def __init__(self, config, esp32, alarmbar):
        '''
        Constructor

        arguments:
        - config: the dictionary storing the configuration
        - esp32: the esp32serial object
        - alarmbar: the alarm bar 
        '''

        self._config = config
        self._esp32 = esp32
        self._alarmbar = alarmbar

        self._alarm_raised = False
        self._warning_raised = False

        self._msg_err = MessageBox()
        self._msg_war = MessageBox()

        self._alarm_timer = QtCore.QTimer()
        self._alarm_timer.timeout.connect(self.handle_alarms)
        self._alarm_timer.start(config["alarminterval"] * 1000)

        self._err_buttons = {}
        self._war_buttons = {}

        self._alarmlabel = self._alarmbar.findChild(QtWidgets.QLabel, "alarmlabel")
        self._alarmstack = self._alarmbar.findChild(QtWidgets.QHBoxLayout, "alarmstack")
        self._alarmsnooze = self._alarmbar.findChild(QtWidgets.QPushButton, "alarmsnooze")

        self._snooze_btn = SnoozeButton(self._esp32, self, self._alarmsnooze)



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
            esp32alarm = None
            esp32warning = None
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

            alarm_codes = esp32alarm.get_alarm_codes()

            for alarm_code, err_str in zip(alarm_codes, errors):
                if alarm_code not in self._err_buttons:
                    btn = AlarmButton(AlarmButton.ERROR, alarm_code, err_str, self._alarmlabel, self._snooze_btn)
                    self._alarmstack.addWidget(btn)
                    self._err_buttons[alarm_code] = btn

            if not self._alarm_raised:
                self._alarm_raised = True
                self._msg_err.critical("ALARM",
                             " - ".join(errors),
                             "\n".join(errors_full),
                             "Alarm received.",
                             { self._msg_err.Ignore: lambda:
                                 self.ok_worker('alarm', esp32alarm) },
                             do_not_block=True)
                self._msg_err.move(0, 100)
                self._msg_err.open()
            else:
                # If the window is already opened, just change the text
                self._msg_err.setInformativeText(" - ".join(errors))
                self._msg_err.setDetailedText("\n".join(errors_full))
                self._msg_err.raise_()


        #
        # WARNINGS
        #
        if esp32warning:
            errors = esp32warning.strerror_all()
            errors_full = esp32warning.strerror_all(append_err_no=True)

            warning_codes = esp32warning.get_alarm_codes()

            for warning_code, err_str in zip(warning_codes, errors):
                if warning_code not in self._war_buttons:
                    btn = AlarmButton(AlarmButton.WARNING, warning_code, err_str, self._alarmlabel, self._snooze_btn)
                    self._alarmstack.addWidget(btn)
                    self._war_buttons[warning_code] = btn

            if not self._warning_raised:
                self._warning_raised = True
                self._msg_war.warning("WARNING",
                             " - ".join(errors),
                             "\n".join(errors_full),
                             "Warning received.",
                             { self._msg_war.Ok: lambda:
                                 self.ok_worker('warning', esp32warning) },
                             do_not_block=True)
                self._msg_war.move(0, 300)
                self._msg_war.open()
            else:
                # If the window is already opened, just change the text
                self._msg_war.setInformativeText(" - ".join(errors))
                self._msg_war.setDetailedText("\n".join(errors_full))
                self._msg_war.raise_()

    def snooze_alarm(self, code):
        if code not in self._err_buttons:
            raise Exception('Cannot snooze code %s as alarm button doesn\t exist.' % code)

        self._err_buttons[code].deleteLater()
        del self._err_buttons[code]
        self._alarmlabel.setText('')
        self._alarmlabel.setStyleSheet('QLabel { background-color : black;')
        self._alarmsnooze.hide()


    def snooze_warning(self, code):
        if code not in self._war_buttons:
            raise Exception('Cannot snooze code %s as warning button doesn\t exist.' % code)

        self._war_buttons[code].deleteLater()
        del self._war_buttons[code]
        self._alarmlabel.setText('')
        self._alarmlabel.setStyleSheet('QLabel { background-color : black;')
        self._alarmsnooze.hide()


    def ok_worker(self, mode, raised_ones):
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
                for alarm_code in raised_ones.unpack():
                    self._esp32.snooze_hw_alarm(alarm_code)
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

    def raise_alarm(self):
        '''
        Raises an alarm in the ESP
        '''
        self._esp32.raise_gui_alarm()

    def stop_alarm(self, code):
        '''
        Stops an alarm in the ESP
        '''
        self._esp32.reset_alarms()

