"""
Alarm facility.
"""

from copy import copy

class GuiAlarms:
    def __init__(self, config, esp32, monitors):
        self._obs = copy(config["alarms"])
        self._esp32 = esp32
        self._monitors = monitors

        # Send the thresholds to the monitors
        for v in self._obs.values():
            self._monitors[v['linked_monitor']].update_thresholds(v.get('min'),
                                                                  v.get('setmin', v['min']),
                                                                  v.get('max'),
                                                                  v.get('setmax', v['max']))

    def _get_by_observable(self, observable):
        for v in self._obs.values():
            if v['observable'] == observable:
                return v
        return None

    def _test_over_threshold(self, item, value):
        if "setmax" in item:
            if value > item["setmax"]:
                self._esp32.raise_alarm(item["over_threshold_code"])
                self._monitors[item['linked_monitor']].set_alarm_state(isalarm=True)

    def _test_under_threshold(self, item, value):
        if "setmin" in item:
            if value < item["setmin"]:
                self._esp32.raise_alarm(item["under_threshold_code"])
                self._monitors[item['linked_monitor']].set_alarm_state(isalarm=True)

    def _test_thresholds(self, item, value):
        self._test_over_threshold(item, value)
        self._test_under_threshold(item, value)

    def update_thresholds(observable, minimum, maximum):
        assert(observable in self._obs)

        self._obs[observable]["setmin"] = minimum
        self._obs[observable]["setmax"] = maximum


    def set_data(self, data):
        for observable in data:
            print('setting data for observable', observable)
            item = self._get_by_observable(observable)
            # print('observable', observable)
            if item is not None:
                self._test_thresholds(item, data[observable])
