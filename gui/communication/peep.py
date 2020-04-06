import time
import numpy as np

"""
a class to simulate the patient breath
"""
class peep:
    t0  = 0
    p   = 0
    f   = 0
    param = {}
    btiming_fluctuations = 0
    def __init__(self):
        self.set('rate', 12)
        self.set('ratio', 2)
        self.set('peep_minimal_pressure', 12)
        self.set('peep_maximal_pressure', 75)
        self.set('peep_minimal_flow',      3)
        self.set('peep_maximal_flow',     20)        
        self.set('flow_decay_time',       .3)

    def setConfig(self, config):
        self.set('rate', config['respiratory_rate']['default'])
        self.set('ratio', 1/config['insp_expir_ratio']['default'])
        self.config = config

    def set(self, name, value):
        print('PEEP: Setting {} to {}'.format(name, value))
        self.param[name] = value
    
    def pressure(self):
        """
        returns the inspirarion pressure in mbar
        see the configuration file simulation.yaml for details
        """
        self.breath()
        return self.p

    def breath_duration(self):
        return 60/self.param['rate']

    def inspiration_duration(self):
        return self.breath_duration() / (1 + self.param['ratio'])

    def flow_decay_time(self):
        return self.inspiration_duration() * self.param['flow_decay_time']
        
    def breath(self):
        rr = self.breath_duration()
        t = time.time_ns()*1e-9 - self.t0
        self.p = self.param['peep_minimal_pressure']
        self.f = self.param['peep_minimal_flow']
        t1 = self.inspiration_duration()
        t2 = rr - t1
        A = 0.95*(self.param['peep_maximal_pressure'] - self.p)
        B = 0.95*(self.param['peep_maximal_flow'] - self.f)
        tau = 0.1 * t1
        tauf = self.flow_decay_time()
        if t> 0 and t < t1:
            self.p += A*(1-np.exp(-t/tau))
            self.f += B*np.exp(-t/tauf)
        elif t > 0 and t < t2:
            self.p += A*np.exp(-(t-t1)/tau)
            self.f += B*np.exp(-t/tauf)
        elif t > rr:
            self.restart()
        # add some random fluctuations
        self.p += np.random.normal(scale = .5)

    def flow(self):
        """
        returns the flow in lpm
        """
        self.breath()        
        return self.f

    def restart(self):
        # the cycle restarts after a fixed +- random time
        self.t0 = time.time_ns()*1e-9 + np.random.normal(scale = self.btiming_fluctuations)
