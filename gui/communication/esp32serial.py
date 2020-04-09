"""
Library to interface with the ESP32
"""

from threading import Lock
import serial # pySerial
from . import ESP32Alarm, ESP32Warning

__all__ = ("ESP32Serial", "ESP32Exception")


class ESP32Exception(Exception):
    """
    Exception class for decoding and hardware failures.
    """

    def __init__(self, verb, line, output):
        """
        Contructor

        arguments:
        - verb           the transmit verb = {get, set}
        - line           the line transmitted to ESP32 that is failing
        - output         what the ESP32 is replying
        """

        self.verb = verb
        self.line = line
        self.output = output

        super(ESP32Exception, self).__init__(
                "ERROR in %s: line: '%s'; output: %s" % (verb, line, output))



class ESP32Serial:
    """
    Main class for interfacing with the ESP32 via a serial connection.
    """

    def __init__(self, port, **kwargs):
        """
        Contructor

        Opens a serial connection to the MVM ESP32

        arguments:
        - port           the port device (e.g. "/dev/ttyUSB0")

        named arguments:
        - any argument available for the serial.Serial pySerial class
        - baudrate       the preferred baudrate, default 115200
        - terminator     the line terminator, binary encoded, default
                         b'\n'
        - timeout        sets the read() timeout in seconds
        """

        self.lock = Lock()

        baudrate = kwargs["baudrate"] if "baudrate" in kwargs else 115200
        timeout = kwargs["timeout"] if "timeout" in kwargs else 1
        self.term = kwargs["terminator"] if "terminator" in kwargs else b'\n'
        self.connection = serial.Serial(port=port, baudrate=baudrate,
                                        timeout=timeout, **kwargs)

        while self.connection.read():
            pass

        a = ESP32Alarm(27)
        for m in a.strerror_all():
            print(m)

    def __del__(self):
        """
        Destructor.

        Closes the connection.
        """

        with self.lock:
            if hasattr(self, "connection"):
                self.connection.close()

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

        print("ESP32Serial-DEBUG: set %s %s" % (name, value))

        with self.lock:
            # I know about Python 3.7 magic string formatting capability
            # but I don't really remember now the version running on
            # Raspbian
            command = 'set ' + name + ' ' + str(value) + '\r\n'
            self.connection.write(command.encode())

            result = b""
            retry = 10
            while retry:
                retry -= 1
                try:
                    result = self.connection.read_until(terminator=self.term)
                    return self._parse(result)
                except Exception as exc:
                    print("ERROR: set failing: %s %s" % (result.decode(), str(exc)))
            raise ESP32Exception("set", command, result.decode())

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

        print("ESP32Serial-DEBUG: get %s" % name)

        with self.lock:
            command = 'get ' + name + '\r\n'
            self.connection.write(command.encode())

            result = b""
            retry = 10
            while retry:
                retry -= 1
                try:
                    result = self.connection.read_until(terminator=self.term)
                    return self._parse(result)
                except Exception as exc:
                    print("ERROR: get failing: %s %s" % (result.decode(), str(exc)))
            raise ESP32Exception("get", command, result.decode())

    def get_all(self):
        """
        Get the pressure, flow, o2, and bpm at once and in this order.

        returns: a dict with member keys as written above and values as
        strings.
        """

        print("ESP32Serial-DEBUG: get all")

        with self.lock:
            self.connection.write(b"get all\r\n")

            result = b""
            retry = 10
            while retry:
                retry -= 1
                try:
                    result = self.connection.read_until(terminator=self.term)
                    pressure, flow, o2, bpm, tidal, peep, temperature, power_mode, battery = self._parse(result).split(',')
                    return { "pressure": pressure, "flow": flow, "o2": o2,
                             "bpm": bpm, "tidal": tidal, "peep": peep,
                             "temperature": temperature,
                             "power_mode": power_mode, "battery": battery }
                except Exception as exc:
                    print("ERROR: get failing: %s %s" % (result.decode(), str(exc)))
            raise ESP32Exception("get", "get all", result.decode())

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
