
class ESP32Alarm:

    alarm_to_string = {
        # From the ESP
        0: "Gas pressure too low",
        1: "Gas pressure too high",
        2: "Internal pressure too low (internal leakage)",
        3: "Internal pressure too high",
        4: "Out of battery power",
        5: "Leakage in gas circuit",
        6: "Obstruction in idraulic circuit",
        7: "Partial obstruction in idraulic circuit",
        # From the GUI
        8: "Pressure to patient mouth too low",
        9: "Pressure to patient mouth too high",
        10: "Inpiratory flux too low",
        11: "Inpiratory flux too high",
        12: "Expiratory flux too low",
        13: "Expiratory flux too high",
        14: "Tidal volume too low",
        15: "Tidal volume too high",
        16: "O2 too low",
        17: "O2 too high",
        18: "PEEP too low",
        19: "PEEP too high",
        20: "Respiratory rate too low",
        21: "Respiratory rate too high",
        
        31: "System failure",
    }

    def __init__(self, number):
        self.number = number

    def __bool__(self):
        print('in __bool__:', self.number)
        return self.number != 0

    def unpack(self):
        bit_pos = 0
        self.alarms = []

        while self.number:
            if self.number & 1:
                self.alarms.append(bit_pos)

            bit_pos += 1
            self.number >>= 1

        print('Found alarms', self.alarms)

        return self.alarms

    def strerror(self, n):
        if not hasattr(self, 'alarms'):
            self.unpack()

        if n in self.alarm_to_string:
            return self.alarm_to_string[n]
        else:
            return 'Unknown error'

    def strerror_all(self):
        if not hasattr(self, 'alarms'):
            self.unpack()

        str_error = []
        for n in self.alarms:
            str_error.append(self.strerror(n))

        return str_error