from communication.esp32serial import ESP32Serial
from communication.peep import peep
from threading import Lock

import yaml
import os

class FakeESP32Serial(ESP32Serial):
    """
    Class to simulate the ESP32
    """
    peep = peep()
    def __init__(self):
        """
        Contructor
        """
        base_dir = os.path.dirname(__file__)
        settings_file = os.path.join(base_dir + '/..', 'default_settings.yaml')
        
        with open(settings_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.peep.setConfig(config)
        self.lock = Lock()

    def _parse(self, result):
        """
        Parses the message from ESP32

        arguments:
        - result         what the ESP replied as a binary buffer

        returns the requested value as a string
        """

        check_str, value = result.decode().split('=')
        check_str = check_str.strip()

        if check_str != 'valore':
            raise Exception("protocol error: 'valore=' expected")
        return value.strip()

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
        return 'OK'

    def get(self, name):
        """
        Get command wrapper

        arguments:
        - name           the parameter name as a string

        returns: the requested value
        """

        with self.lock:
            result = 0
            return result

    def get_all(self):
        """
        Get the pressure, flow, o2, and bpm at once and in this order.

        returns: a dict with member keys as written above and values as
        strings.
        """

        with self.lock:
            pressure = self.peep.pressure()
            flow = self.peep.flow()
            o2 = 1
            bpm = 12
            return { "pressure": pressure, "flow": flow, "o2": o2,
                     "bpm": bpm }
