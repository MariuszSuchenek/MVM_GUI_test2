"""
Alarm facility.
"""

from copy import copy

class GuiAlarm():
    def __init__(self, name, config, monitors, alarm_handler):
        self._config = config
        self.name = name
        self.alarm_h = alarm_handler

        alarm_default = {
                "min": 0,
                "value": 0,
                "max": 100,
                "alarm_min_code": -1,
                "alarm_max_code": -1,
                "under_threshold_code": None,
                "over_threshold_code": None,
                "observable": "o2",
                "linked_monitor": None}
        entry = self._config['alarms'].get(name, alarm_default)

        self.entry = entry
        self.min = entry.get("min", alarm_default["min"])
        self.setmin = entry.get("setmin", self.min)
        self.value = entry.get("value", alarm_default["value"])
        self.max = entry.get("max", alarm_default["max"])
        self.setmax = entry.get("setmax", self.max)
        self.alarm_min_code = entry.get("alarm_min_code", alarm_default["alarm_min_code"])
        self.alarm_max_code = entry.get("alarm_max_code", alarm_default["alarm_max_code"])
        self.under_threshold_code = entry.get("under_threshold_code", alarm_default["under_threshold_code"])
        self.over_threshold_code = entry.get("over_threshold_code", alarm_default["over_threshold_code"])
        self.observable = entry.get("observable", alarm_default["observable"])
        self.linked_monitor = entry.get("linked_monitor", alarm_default["linked_monitor"])

        # Link monitor, if specified
        if self.linked_monitor is not None:
            # Assign the alarm to the given monitored field
            self.linked_monitor = monitors[self.linked_monitor]
            print("Linking " + self.name + " to " + self.linked_monitor.configname)
            self.linked_monitor.assign_alarm(self)

    def update(self, value):
        """
        Updates the value in the monitored field

        value: The value that the monitor will display.
        """
        self.value = value
        # Handle potential over/under threshold
        alarm_raised = False
        if self.setmin is not None and value < self.setmin and self.under_threshold_code is not None:
            self.alarm_h.raise_alarm(self.under_threshold_code)
            alarm_raised = True
        if self.setmax is not None and value > self.setmax and self.over_threshold_code is not None:
            alarm_raised = True
            self.alarm_h.raise_alarm(self.over_threshold_code)

        # Handle sending alarm to monitor
        if self.linked_monitor is not None and alarm_raised:
            self.linked_monitor.set_alarm_state(True)

    def valid_minmax(self):
        return self.max is not None and self.min is not None

    def clear_alarm(self):
        """
        Clears previous out of range alarms by reverting the background color.
        """
        self.alarm_h.stop_alarm(self.name)

