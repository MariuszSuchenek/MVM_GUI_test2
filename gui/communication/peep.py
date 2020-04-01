import time
import numpy as np
import os
import yaml

"""
a class to simulate the patient breath
"""
class peep:
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        settings_file = os.path.join(base_dir, 'simulation.yaml')
        with open(settings_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        print ('Simulator Config:', yaml.dump(config), sep='\n')
        self.t1 = float(config['t1'])
        self.t2 = self.t1 + float(config['t2'])
        self.t3 = self.t2 + float(config['t3'])
        self.t4 = self.t3 + float(config['t4'])
        self.t5 = self.t4 + float(config['t5'])
        self.p1 = float(config['p1'])
        self.p2 = float(config['p2'])
        self.f1 = float(config['f1'])
        self.f2 = float(config['f2'])
        self.f3 = float(config['f3'])
        self.decaytime = float(config['decay_time'])
        self.resolution = float(config['resolution'])
        self.t0 = time.time()
        self.btiming_fluctuations = float(config['btiming_fluctuations'])
        print('PEEP timing   : {} {} {} {} {}'.format(self.t1, self.t2, self.t3,
                                                   self.t4, self.t5))
        print('PEEP pressures: {} {}'.format(self.p1, self.p2))
        print('PEEP flow     : {} {} {}'.format(self.f1, self.f2, self.f3))

    def pressure(self):
        """
        returns the inspirarion pressure in mbar
        see the configuration file simulation.yaml for details
        """
        t = time.time() - self.t0
        p = 0
        if t > self.t1 and t < self.t2:
            # pressure linear increase
            a = self.p2/(self.t2-self.t1)
            b = -a*self.t1
            p = a*t + b
        elif t >= self.t2 and t < self.t3:
            # pressure reached its maximum and starts decreasing
            # exponentially
            tau = (self.t3 - self.t2)*self.decaytime
            c = self.p1
            A = self.p2 - self.p1
            p = c+A*np.exp(-(t-self.t2)/tau)
        elif t >= self.t3 and t < self.t4:
            # pressure stay stable for a while
            p = self.p1
        elif t >= self.t4 and t < self.t5:
            # pressure drops exponentially
            tau = (self.t3 - self.t2)*self.decaytime
            A = self.p1
            p = A*np.exp(-(t-self.t4)/tau)
        elif t > self.t5:
            # restart the cycle
            self.restart()
        # add some random fluctuations
        p += np.random.normal(scale = (self.p2 - self.p1)*self.resolution)
        return p

    def flow(self):
        """
        returns the flow in lpm
        """
        t = time.time() - self.t0
        f = 0
        if t > self.t1 and t < self.t2:
            # flow decays exponentially after a fast grow
            # reaching an intermediate level
            tau = (self.t2 - self.t1)*self.decaytime
            A = self.f1
            c = self.f2
            f = c + A*np.exp(-(t-self.t1)/tau)
        elif t >= self.t2 and t < self.t4:
            # flow drops to negative values, then increase
            # exponentially to zero
            tau = (self.t2 - self.t1)*self.decaytime
            A = self.f3
            c = self.f2
            f = -A*np.exp(-(t-self.t2)/tau)
        elif t > self.t5:
            # restart cycle
            self.restart()
        # add some random fluctuation
        f += np.random.normal(scale = (self.f1 - self.f2)*self.resolution)
        return f

    def restart(self):
        # the cycle restarts after a fixed +- random time
        self.t0 = time.time() + np.random.normal(scale = self.btiming_fluctuations)
