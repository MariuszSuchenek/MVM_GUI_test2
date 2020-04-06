"""
Library to interface with the ESP32
"""

from threading import Lock
import serial # pySerial


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

        baudrate = kwargs["baudrate"] if "baudrate" in kwargs else 115200
        timeout = kwargs["timeout"] if "timeout" in kwargs else 1
        self.term = kwargs["terminator"] if "terminator" in kwargs else b'\n'
        self.lock = Lock()
        self.connection = serial.Serial(port=port, baudrate=baudrate,
                                        timeout=timeout, **kwargs)

        while self.connection.read():
            pass

    def __del__(self):
        """
        Destructor.

        Closes the connection.
        """
        if hasattr(self, "connection"):
            with self.lock:
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

    def get(self, name):
        """
        Get command wrapper

        arguments:
        - name           the parameter name as a string

        returns: the requested value
        """

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

        with self.lock:
            self.connection.write(b"get all\r\n")

            result = b""
            retry = 10
            while retry:
                retry -= 1
                try:
                    result = self.connection.read_until(terminator=self.term)
                    pressure, flow, o2, bpm = self._parse(result).split(',')
                    return { "pressure": pressure, "flow": flow, "o2": o2,
                             "bpm": bpm }
                except Exception as exc:
                    print("ERROR: get failing: %s %s" % (result.decode(), str(exc)))
            raise ESP32Exception("get", command, result.decode())
