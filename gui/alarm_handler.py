
from PyQt5 import QtCore, QtGui, QtWidgets

from messagebox import MessageBox
from communication.esp32serial import ESP32Alarm, ESP32Warning

BITMAP = {1 << x: x for x in range(32)}
ERROR = 0
WARNING = 1

class SnoozeButton:
    '''
    Takes care of snoozing alarms.
    '''

    def __init__(self, esp32, alarm_h, alarmsnooze):
        '''
        Constructor

        arguments:
        - esp32: instance of ESP32Serial
        - alarm_h: instance of AlarmHandler
        - alarmsnooze: the snooze alarm button
        '''

        self._esp32 = esp32
        self._alarm_h = alarm_h
        self._alarmsnooze = alarmsnooze

        self._alarmsnooze.hide()
        self._code = None
        self._mode = None

        self._alarmsnooze.clicked.connect(self._on_click_snooze)
        self._alarmsnooze.setStyleSheet('background-color: rgb(0,0,205); color: white; font-weight: bold;')
        self._alarmsnooze.setMaximumWidth(150)

    def set_code(self, code):
        '''
        Sets the alarm code
        '''
        self._code = code
        self._alarmsnooze.setText('Snooze %s' % str(BITMAP[self._code]))

    def set_mode(self, mode):
        '''
        Sets the mode (alarm/warning)
        '''
        self._mode = mode

    def show(self):
        '''
        Shows the snooze alarm button
        '''
        self._alarmsnooze.show()

    def _on_click_snooze(self):
        '''
        The callback function called when the alarm
        snooze button is clicked.
        '''

        if self._mode not in [WARNING, ERROR]:
            raise Exception('mode must be alarm or warning.')

        # Reset the alarms/warnings in the ESP
        # If the ESP connection fails at this
        # time, raise an error box
        try:
            if self._mode == ERROR:
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
    The alarm and warning buttons
    shown in the top alarmbar
    '''

    def __init__(self, mode, code, errstr, label, snooze_btn):
        super(AlarmButton, self).__init__()
        self._mode = mode
        self._code = code
        self._errstr = errstr
        self._label = label
        self._snooze_btn = snooze_btn

        self.clicked.connect(self._on_click_event)

        if self._mode == ERROR:
            self._bkg_color = 'red'
        elif self._mode == WARNING:
            self._bkg_color = 'orange'
        else:
            raise Exception('Option %s not supported'.format(self._mode))

        self.setText(str(BITMAP[self._code]))

        self.setStyleSheet('background-color: %s; color : white; border: 0.5px solid white; font-weight: bold;' % self._bkg_color)

        self.setMaximumWidth(35)
        self.setMaximumHeight(30)



    def _on_click_event(self):
        '''
        The callback function called when the user
        clicks on an alarm button
        '''

        # Set the label showing the alarm name
        self._label.setStyleSheet('QLabel { background-color : %s; color : white; font-weight: bold;}' % self._bkg_color)
        self._label.setText(self._errstr)
        self._label.show()

        self._activate_snooze_btn()

    def _activate_snooze_btn(self):
        '''
        Activates the snooze button
        that will silence this alarm
        '''
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

        self._alarm_timer = QtCore.QTimer()
        self._alarm_timer.timeout.connect(self.handle_alarms)
        self._alarm_timer.start(config["alarminterval"] * 1000)

        self._err_buttons = {}
        self._war_buttons = {}

        self._alarmlabel = self._alarmbar.findChild(QtWidgets.QLabel, "alarmlabel")
        self._alarmstack = self._alarmbar.findChild(QtWidgets.QHBoxLayout, "alarmstack")
        self._alarmsnooze = self._alarmbar.findChild(QtWidgets.QPushButton, "alarmsnooze")

        self._snooze_btn = SnoozeButton(self._esp32, self, self._alarmsnooze)

        btn = QtGui.QPushButton('?')
        btn.setMaximumWidth(1)
        btn.setStyleSheet('background-color: black; color: black; border: 0.5px solid black; font-weight: bold;')
        self._alarmstack.addWidget(btn)


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
                    btn = AlarmButton(ERROR, alarm_code, err_str, self._alarmlabel, self._snooze_btn)
                    self._alarmstack.addWidget(btn)
                    self._err_buttons[alarm_code] = btn

        #
        # WARNINGS
        #
        if esp32warning:
            errors = esp32warning.strerror_all()
            errors_full = esp32warning.strerror_all(append_err_no=True)

            warning_codes = esp32warning.get_alarm_codes()

            for warning_code, err_str in zip(warning_codes, errors):
                if warning_code not in self._war_buttons:
                    btn = AlarmButton(WARNING, warning_code, err_str, self._alarmlabel, self._snooze_btn)
                    self._alarmstack.addWidget(btn)
                    self._war_buttons[warning_code] = btn

    def snooze_alarm(self, code):
        '''
        Graphically snoozes alarm corresponding to 'code'
        '''
        if code not in self._err_buttons:
            raise Exception('Cannot snooze code %s as alarm button doesn\'t exist.' % code)

        self._err_buttons[code].deleteLater()
        del self._err_buttons[code]
        self._alarmlabel.setText('')
        self._alarmlabel.setStyleSheet('QLabel { background-color: black; }')
        self._alarmsnooze.hide()


    def snooze_warning(self, code):
        '''
        Graphically snoozes warning corresponding to 'code'
        '''
        if code not in self._war_buttons:
            raise Exception('Cannot snooze code %s as warning button doesn\'t exist.' % code)

        self._war_buttons[code].deleteLater()
        del self._war_buttons[code]
        self._alarmlabel.setText('')
        self._alarmlabel.setStyleSheet('QLabel { background-color: black; }')
        self._alarmsnooze.hide()


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

