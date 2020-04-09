import time
import numpy as np

"""
a class to simulate the patient breath
"""
class peep:
    # class members
    t0        = 0
    p         = 0
    f         = 0
    expTime   = 0
    initiated = False

    # constants
    AUTOMATIC = 0
    ASSISTED  = 1

    # parameters: setting defaults
    param = {}
    btiming_fluctuations = 0
    def __init__(self):
        self.set('rate', 12)                    # resp. rate
        self.set('ratio', 2)                    # insp/exp ratio
        self.set('mode', self.AUTOMATIC)        # ventilation mode
        self.set('peep_minimal_pressure', 12)   # minimal pressure in auto mode (PEEP)
        self.set('ptarget', 75)                 # inpiration pressure in auto mode
        self.set('peep_minimal_flow',      3)   # simulated minimal flow
        self.set('peep_maximal_flow',     20)   # simulated maximal flow
        self.set('flow_decay_time',       .3)   # flow duration (as a fraction of resp. time)
        self.t0 = time.time_ns()*1e-9
        self.vTidal = 5e-2
        self.lastT = 0

    def setConfig(self, config):
        # set the parameters according to the configuration file
        self.set('rate', config['respiratory_rate']['default'])
        self.set('ratio', config['insp_expir_ratio']['default'])
        self.config = config

    def set(self, name, value):
        # set a parameter to the given value
        print('PEEP: Setting {} to {}'.format(name, value))
        self.param[name] = value
    
    def pressure(self):
        # returns the inspirarion pressure in mbar
        self.breath()
        return self.p

    def breath_duration(self):
        # returns the breath duration according to the respiration rate setting
        return  60/self.param['rate']

    def inspiration_duration(self):
        # the inspiration duration is a fraction of the respiration cycle
        # set by param['ratio']
        return self.breath_duration() / (1 + self.param['ratio'])

    def flow_decay_time(self):
        # returns the flow decay time in s
        return self.inspiration_duration() * self.param['flow_decay_time']

    def inspire(self, t):
        # called at the beginning of a breath
        if not self.initiated:
            self.initiated = True
            self.vTidal = 5e-2
            self.lastT = 0
            if self.param['mode'] == self.AUTOMATIC:
                self.expTime = self.breath_duration() - self.inspiration_duration()
            else:
                self.expTime = self.breath_duration() - self.inspiration_duration()
                self.expTime += np.random.normal(scale = 3)

    def vtidal(self):
        return self.vTidal * 1000
        
    def breath(self):
        # take a simaulated breath: every breath is divided into an inspiration (t0-t1)
        # and an expiration (t1-t2) cycle. During the first keep the pressure almost
        # constant with an exponential initial growth. During expiration the pressure
        # drops exponentially to zero.
        rr = self.breath_duration()                             # resp. cycle duration
        t = time.time_ns()*1e-9 - self.t0                       # current time
        self.p = self.param['peep_minimal_pressure']            # PEEP
        self.f = self.param['peep_minimal_flow']                # inhale pressure
        t1 = self.inspiration_duration()                        # inspiration time
        t2 = self.expTime                                       # expiration time
        A = 0.95*(self.param['ptarget'] - self.p)               # pressure amplitude
        B = 0.95*(self.param['peep_maximal_flow'] - self.f)     # flow amplitude
        tau = 0.1 * t1                                          # rise/decay time of the pressure 
        tauf = self.flow_decay_time()                           # decay time of the flow
        if t < t1:                                              # inspiration
            self.inspire(t)
            self.p += A*(1-np.exp(-t/tau))
            self.f += B*np.exp(-t/tauf)
            self.vTidal += self.f * (t - self.lastT)/60         # flow is in slpm
            self.lastT = t
        elif t < t1 + t2:
            # expiration
            self.p += A*np.exp(-(t-t1)/tau)
            self.f += B*np.exp(-t/tauf)
        else:
            self.initiated = False
            self.restart()
        self.p += np.random.normal(scale = .1)

    def flow(self):
        # returns the flow in lpm
        self.breath()        
        return self.f

    def restart(self):
        self.t0 = time.time_ns()*1e-9
