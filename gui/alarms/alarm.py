"""
Alarm facility.
"""

from copy import copy

class GuiAlarms:
    def __init__(self, config, esp32, monitors):
        self._obs = copy(config["alarms"])
        self._esp32 = esp32
        self._monitors = monitors

    def _get_by_observable(self, observable):
        return self._obs[observable]

    def _test_over_threshold(self, item, value):
        if "over_threshold" in item:
            if value > item["over_threshold"]:
                self._esp32.raise_alarm(item["over_threshold_code"])
                # TODO: find the linked_monitor in self._monitors
                #linked_monitor.set_alarm()

    def _test_under_threshold(self, item, value):
        if "under_threshold" in item:
            if value < item["under_threshold"]:
                self._esp32.raise_alarm(item["under_threshold_code"])
                # TODO: find the linked_monitor in self._monitors
                #linked_monitor.set_alarm()

    def _test_thresholds(self, item, value):
        self._test_over_threshold(item, value)
        self._test_under_threshold(item, value)

    def update_thresholds(observable, minimum, maximum):
        assert(observable in self._obs)

        self._obs[observable]["under_threshold"] = minimum
        self._obs[observable]["over_threshold"] = maximum


    def set_data(self, data):
        for observable in data:
            item = self._get_by_observable(observable)
            _test_thresholds(item, data[observable])


