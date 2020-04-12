"""
A dummy class that can be used for testing the GUI when a real
ESP32 chip isn't available.

Currently just reports fixed values. Can be made more intelligent
as needed.
"""

import random
from PyQt5 import QtWidgets, uic
from communication.peep import peep
from . import ESP32Alarm, ESP32Warning

KNOWN_ALARM_CODES = [0] + [1 << bit for bit in (0, 1, 2, 3, 4, 5, 6, 7, 31)]
KNOWN_WARNING_CODES = [0] + [1 << bit for bit in (0,)]

class FakeMonitored(QtWidgets.QWidget):
    def __init__(self, name, generator, value=0, random=True):
        super(FakeMonitored, self).__init__()
        uic.loadUi('communication/input_monitor_widget.ui', self)

        self.generator = generator

        self.findChild(QtWidgets.QLabel, "label").setText(name)

        self.value_ib = self.findChild(QtWidgets.QDoubleSpinBox, "value")
        self.value_ib.setValue(value)

        self.random_cb = self.findChild(QtWidgets.QCheckBox, "random_checkbox")
        self.random_cb.setChecked(random)
        self.random_cb.toggled.connect(self._random_checkbox_fn)
        self._random_checkbox_fn()

    def _random_checkbox_fn(self):
        self.value_ib.setEnabled(not self.random_cb.isChecked())

    def generate(self):
        if self.random_cb.isChecked():
            return self.generator()
        else:
            return self.value_ib.value()

class FakeESP32Serial(QtWidgets.QMainWindow):
    peep = peep()
    def __init__(self, config, alarm_rate=0.1):
        super(FakeESP32Serial, self).__init__()

        uic.loadUi('communication/fakeesp32.ui', self)
        self.get_all_fields = config["get_all_fields"]
        self.observables = {config["monitors"][item]["observable"]: None
                                      for item in config["monitors"]}

        self._arrange_fields()
        self.alarms_checkboxes = {}
        self._connect_alarm_widgets()

        self.set_params = {"temperature": 40}
        self.alarm_rate = alarm_rate

        self.event_log = self.findChild(QtWidgets.QPlainTextEdit, "event_log")
        self.event_log.setReadOnly(True)
        self.show()

    def _arrange_fields(self):
        max_colums = 3 # you eventually need to edit the
                       # input_monitor_widget.ui file to put more

        monitors_grid = self.findChild(QtWidgets.QGridLayout, "monitors_grid")

        row = 0
        column = 0
        for name in self.observables:
            if name == "pressure":
                generator = self.peep.pressure
            elif name == "flow":
                generator = self.peep.flow
            elif name == "battery_charge":
                generator = lambda: int(random.uniform(0, 100))
            elif name == "tidal":
                generator = lambda: random.uniform(1000, 1500)
            elif name == "peep":
                generator = lambda: random.uniform(4, 20)
            elif name == "temperature":
                generator = lambda: random.uniform(10, 50)
            elif name == "battery_powered":
                generator = lambda: int(random.uniform(0, 1.5))
            elif name == "bpm":
                generator = lambda: random.uniform(10, 100)
            elif name == "o2":
                generator = lambda: random.uniform(10, 100)
            elif name == "peak":
                generator = lambda: random.uniform(10, 100)
            elif name == "total_inspired_volume":
                generator = lambda: random.uniform(10, 100)
            elif name == "total_expired_volume":
                generator = lambda: random.uniform(10, 100)
            elif name == "volume_minute":
                generator = lambda: random.uniform(10, 100)
            else:
                generator = lambda: random.uniform(10, 100)

            fake_mon = FakeMonitored(name, generator)
            self.observables[name] = fake_mon

            monitors_grid.addWidget(fake_mon, row, column)

            column += 1
            if column == max_colums:
                column = 0
                row += 1

    def _compute_and_raise_alarms(self):
        number = 0
        for item in self.alarms_checkboxes:
            if self.alarms_checkboxes[item].isChecked():
                number += item
        self.set("alarm", number)

    def _connect_alarm_widgets(self):
        def get_checkbox(wname, alarm_code):
            return (1 << alarm_code, self.findChild(QtWidgets.QCheckBox, wname))

        # for simplicity here the bit number is used. It will be converted
        # few lines below.
        known_check_boxes = {
                "low_input_pressure_alarm": 0,
                "high_input_pressure_alarm": 1,
                "low_inner_pressure_alarm": 2,
                "high_inner_pressure_alarm": 3,
                "battery_low_alarm": 4,
                "gas_leakage_alarm": 5,
                "gas_occlusion_alarm": 6,
                "partial_gas_occlusion_alarm": 7,
                "system_failure_alarm": 31}

        for name in known_check_boxes:
            code, widget = get_checkbox(name, known_check_boxes[name])
            self.alarms_checkboxes[code] = widget

        self.raise_alarms_button = self.findChild(
                QtWidgets.QPushButton,
                "raise_alarm_btn")

        self.raise_alarms_button.pressed.connect(self._compute_and_raise_alarms)

    def log(self, message):
        self.event_log.appendPlainText(message)

    def set(self, name, value):
        """
        Set command wrapper

        arguments:
        - name           the parameter name as a string
        - value          the value to assign to the variable as any type
                         convertible to string

        returns: an "OK" string in case of success.
        """

        print("FakeESP32Serial-DEBUG: set %s %s" % (name, value))

        self.set_params[name] = value
        return "OK"

    def set_watchdog(self):
        """
        Set the watchdog polling command

        returns: an "OK" string in case of success.
        """

        return self.set("watchdog_reset", 1)

    def get(self, name):
        """
        Get command wrapper

        arguments:
        - name           the parameter name as a string

        returns: the requested value
        """

        print("FakeESP32Serial-DEBUG: get %s" % name)

        retval = 0

        if name == 'alarm':
            retval = self._compute_and_raise_alarms()
        if name == 'warnings':
            retval = 0
       elif name in self.observables:
            retval = self.observables[name].generate()
        elif name in self.set_params:
            retval = self.set_params[name]
        else:
            retval = int(random.uniform(10, 100))

        return str(retval)

    def get_all(self):
        """
        Get the pressure, flow, o2, and bpm at once and in this order.

        returns: a dict with member keys as written above and values as
        strings.
        """

        print("FakeESP32Serial-DEBUG: get all")

        values = [self.get(field) for field in self.get_all_fields]

        return dict(zip(self.get_all_fields, values))

    def get_alarms(self):
        """
        Get the alarms from the ESP32

        returns: a ESP32Alarm instance describing the possible alarms.
        """

        return ESP32Alarm(int(self.get("alarm")))

    def get_warnings(self):
        """
        Get the warnings from the ESP32

        returns: a ESP32Warning instance describing the possible warnings.
        """

        return ESP32Warning(int(self.get("warning")))

    def reset_alarms(self):
        """
        Reset all the raised alarms in ESP32

        returns: an "OK" string in case of success.
        """

        return self.set("alarm", 0)

    def reset_warnings(self):
        """
        Reset all the raised warnings in ESP32

        returns: an "OK" string in case of success.
        """

        return self.set("warning", 0)

    def raise_alarm(self, alarm_type):
        """
        Raises an alarm in ESP32

        arguments:
        - alarm_type      an integer representing the alarm type

        returns: an "OK" string in case of success.
        """

        return self.set("alarm", alarm_type)
