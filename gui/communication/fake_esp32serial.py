"""
A dummy class that can be used for testing the GUI when a real
ESP32 chip isn't available.

Currently just reports fixed values. Can be made more intelligent
as needed.
"""

from threading import Lock
import random
        
class FakeESP32Serial:
    def __init__(self):
        self.lock = Lock()
        self.set_params = {}
        self.random_params = ["mve", "vti", "vte"]
        
    def set(self, name, value):
        """
        Set command wrapper

        arguments:
        - name           the parameter name as a string
        - value          the value to assign to the variable as any type
                         convertible to string

        returns: an "OK" string in case of success.
        """

        with self.lock:
            self.set_params[name] = value
            return "OK"
    
    def get(self, name):
        """
        Get command wrapper

        arguments:
        - name           the parameter name as a string

        returns: the requested value
        """

        with self.lock:
            if name in self.set_params:
                return self.set_params[name]
            elif name in self.random_params:
                return random.uniform(10, 100)
            else:
                return 0