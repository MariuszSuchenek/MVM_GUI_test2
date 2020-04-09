from communication.esp32serial import ESP32Serial, ESP32Alarm, ESP32Warning
from communication.peep import peep
from threading import Lock
from numpy import random

import yaml
import os

class FakeESP32Serial(ESP32Serial):
    peep = peep()
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        settings_file = os.path.join(base_dir + '/..', 'default_settings.yaml')
        
        with open(settings_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.peep.setConfig(config)
        self.lock = Lock()

    def set(self, name, value):
        """
        Set command wrapper

        arguments:
        - name           the parameter name as a string
        - value          the value to assign to the variable as any type
                         convertible to string

        returns: an "OK" string in case of success.
        """
        self.peep.set(name, value)
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

#        print("FakeESP32Serial-DEBUG: get %s" % name)

        with self.lock:
            retval = 0
            
            if name == 'alarm' or name == 'warning':
                if random.uniform(0, 1) < 0.1:
                    retval = int(random.uniform(0, 2**31-1))
                    print('**************************************************** ALARM/WARINING SIMULATION, retval', retval)
                else:
                    retval = 0
            else:
                retval = self.peep.set(name, retval)
            return str(retval)
            
    def get_all(self):
        """
        Get the pressure, flow, o2, and bpm at once and in this order.

        returns: a dict with member keys as written above and values as
        strings.
        """

        with self.lock:
            return {"pressure":    self.peep.pressure(),
                    "flow":        self.peep.flow(),
                    "o2":          random.uniform(10, 100),
                    "bpm":         random.uniform(10, 100),
                    "tidal":       self.peep.vtidal(),
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
