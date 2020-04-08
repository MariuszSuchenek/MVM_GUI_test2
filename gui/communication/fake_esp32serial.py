"""
A dummy class that can be used for testing the GUI when a real
ESP32 chip isn't available.

Currently just reports fixed values. Can be made more intelligent
as needed.
"""

from threading import Lock
import random
from communication.peep import peep

class FakeESP32Serial:
    peep = peep()
    def __init__(self):
        self.lock = Lock()
        self.set_params = {"alarm": 0, "warning": 0}
        self.random_params = ["pressure", "flow", "o2", "bpm", "tidal",
                              "peep", "temperature", "power_mode",
                              "battery" ]

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

        with self.lock:
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

        with self.lock:
            retval = 0

            if name in self.set_params:
                retval = self.set_params[name]
            elif name in self.random_params:
                retval = random.uniform(10, 100)

            return str(retval)

    def get_all(self):
        """
        Get the pressure, flow, o2, and bpm at once and in this order.

        returns: a dict with member keys as written above and values as
        strings.
        """

        print("FakeESP32Serial-DEBUG: get all")

        with self.lock:
            return {"pressure":    self.peep.pressure(),
                    "flow":        self.peep.flow(),
                    "o2":          random.uniform(10, 100),
                    "bpm":         random.uniform(10, 100),
                    "tidal":       random.uniform(1000, 1500),
                    "peep":        random.uniform(4, 20),
                    "temperature": random.uniform(10, 50),
                    "power_mode":  int(random.uniform(0, 1.5)),
                    "battery":     random.uniform(1, 100)}

    def get_alarms(self):
        """
        Get the alarms from the ESP32

        returns: a ESP32Alarm instance describing the possible alarms.
        """

        return ESP32Alarm(int(self.get("alarm")))

    def get_warnings(self):
        """
        Get the warnings from the ESP32

        returns: a ESP32Alarm instance describing the possible warnings.
        """

        return ESP32Alarm(int(self.get("warning")))

    def reset_alarms(self):
        """
        Reset all the raised alarms in ESP32

        returns: an "OK" string in case of success.
        """

        return self.set("alarm", 0)

    def raise_alarm(self, alarm_type):
        """
        Raises an alarm in ESP32

        arguments:
        - alarm_type      an integer representing the alarm type

        returns: an "OK" string in case of success.
        """

        return self.set("alarm", alarm_type)
