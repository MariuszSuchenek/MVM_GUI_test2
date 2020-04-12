"""
Alarm facility.
"""

from copy import copy

class GuiAlarms:
    def __init__(self, config, esp32, monitors):
        '''
        Constructor

        arguments:
        - config: the dict config
        - esp32: instance of the esp32serial
        - monitors: a dict name->Monitor
        '''
        self._obs = copy(config["alarms"])
        self._esp32 = esp32
        self._monitors = monitors

        self._mon_to_obs = {}
        for n, v in self._obs.items():
            self._mon_to_obs[v['linked_monitor']] = n
            v['min'] = v.get('min', None)
            v['max'] = v.get('max', None)
            v['setmin'] = v.get('setmin', v.get('min'))
            v['setmax'] = v.get('setmax', v.get('max'))
        

        self.update_mon_thresholds()

    def update_mon_thresholds(self):
        '''
        Send the thresholds to the monitors
        '''
        for n, v in self._obs.items():
            self._monitors[v['linked_monitor']].update_thresholds(v.get('min'),
                                                                  v.get('setmin'),
                                                                  v.get('max'),
                                                                  v.get('setmax'))

    def _get_by_observable(self, observable):
        '''
        Gets the dict consiguration for a 
        particular observable
        '''
        for v in self._obs.values():
            if v['observable'] == observable:
                return v
        return None

    def _test_over_threshold(self, item, value):
        '''
        Checks if the current value is above
        threshold (if a threshold exists)
        '''
        if item['setmax'] is not None:
            if value > item["setmax"]:
                self._esp32.raise_alarm(item["over_threshold_code"])
                self._monitors[item['linked_monitor']].set_alarm_state(isalarm=True)

    def _test_under_threshold(self, item, value):
        '''
        Checks if the current value is under
        threshold (if a threshold exists)
        '''
        if item['setmin'] is not None:
            if value < item["setmin"]:
                self._esp32.raise_alarm(item["under_threshold_code"])
                self._monitors[item['linked_monitor']].set_alarm_state(isalarm=True)

    def _test_thresholds(self, item, value):
        '''
        Checks if the current value is above or under
        threshold (if a threshold exists)
        '''
        self._test_over_threshold(item, value)
        self._test_under_threshold(item, value)

    def clear_alarm(self, name):
        '''
        Resets all alarms. We might want to reset only
        a particular bit, this is why name is an argument here.
        '''
        self._esp32.reset_alarms()
        # obs = self._mon_to_obs.get(name, None)
        # if obs is not None:  
        #     self._esp32.clear_alarm(self._obs[obs]['under_threshold_code'])
        #     self._esp32.clear_alarm(self._obs[obs]['over_threshold_code'])


    def update_thresholds(observable, minimum, maximum):
        '''
        Updated the thresholds
        '''
        assert(observable in self._obs)

        self._obs[observable]["setmin"] = minimum
        self._obs[observable]["setmax"] = maximum


    def set_data(self, data):
        '''
        Sets the data. This is called by the 
        DataHandler
        '''
        for observable in data:
            item = self._get_by_observable(observable)
            if item is not None:
                self._test_thresholds(item, data[observable])

    def has_valid_minmax(self, name):
        '''
        Checks if max and min are not None
        '''
        obs = self._mon_to_obs.get(name, None)
        if obs is None: return False
        value_max = self._obs[obs]['max']
        value_min = self._obs[obs]['min']
        return value_max is not None and value_min is not None

    def get_setmin(self, name):
        '''
        Returns the setmin for monitor 
        with name
        '''
        obs = self._mon_to_obs.get(name, None)
        if obs is None: return False
        else: return self._obs[obs].get('setmin', self._obs[obs]['min'])

    def get_setmax(self, name):
        '''
        Returns the setmax for monitor 
        with name
        '''
        obs = self._mon_to_obs.get(name, None)
        if obs is None: return False
        else: return self._obs[obs].get('setmax', self._obs[obs]['max'])

    def get_min(self, name):
        '''
        Returns the min for monitor 
        with name
        '''
        obs = self._mon_to_obs.get(name, None)
        if obs is None: return False
        else: return self._obs[obs]['min']

    def get_max(self, name):
        '''
        Returns the max for monitor 
        with name
        '''
        obs = self._mon_to_obs.get(name, None)
        if obs is None: return False
        else: return self._obs[obs]['max']

    def update_min(self, name, minvalue):
        '''
        Updates the min for monitor 
        with name
        '''
        obs = self._mon_to_obs.get(name, None)
        if obs is not None: 
            self._obs[obs]['setmin'] = minvalue
            self.update_mon_thresholds()

    def update_max(self, name, maxvalue):
        '''
        Updates the max for monitor 
        with name
        '''
        obs = self._mon_to_obs.get(name, None)
        if obs is not None:  
            self._obs[obs]['setmax'] = maxvalue
            self.update_mon_thresholds()



