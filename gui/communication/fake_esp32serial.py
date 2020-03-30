"""
A dummy class that can be used for testing the GUI when a real
ESP32 chip isn't available.

Currently just reports fixed values. Can be made more intelligent
as needed.
"""

from threading import Lock
        
class FakeESP32Serial:
    def __init__(self):
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

        with self.lock:
            return "OK"
    
    def get(self, name):
        """
        Get command wrapper

        arguments:
        - name           the parameter name as a string

        returns: the requested value
        """

        with self.lock:
            return 1.5