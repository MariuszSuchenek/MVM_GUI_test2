#!/usr/bin/env python3
import sys, traceback
import time
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from messagebox import MessageBox

class DataHandler():
    '''
    This class takes care of starting a new QThread which
    is entirey dedicated to read data from the ESP32.
    You will need to connect a DataFiller using connect_data_filler(),
    and this class will fill the data direclty.
    '''

    def __init__(self, config, esp32, data_filler):
        '''
        Initializes this class by creating a new QThreadPool
        '''

        self._config = config
        self._esp32 = esp32
        self._data_f = data_filler

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.esp32_io)


    def esp32_data_callback(self, parameter, data):
        '''
        This method is called everytime there is a new read from
        the ESP32, and it receives the parameters read, and
        the data associated to it
        '''

        if parameter == 'Done.' and data is None and not self._running:
            # it is the signal that the thread is closing gracefully,
            # ignore it! TODO: feel free to implement a better way to do
            # this.
            return

        print('Got data at time', datetime.datetime.now(), '=>', parameter, data)
        status = self._data_f.add_data_point(parameter, data)


    def esp32_io(self):
        '''
        This is the main function that runs in the thread.
        '''

        try:
            # Get all params from ESP
            current_values = self._esp32.get_all()

            # Converting from str to float
            for p, v in current_values.items():
                current_values[p] = float(v)

            # finally, emit for all the values we have:
            for p, v in current_values.items():
                self.esp32_data_callback(p, v)

        except Exception as error:
            self.open_comm_error(str(error))

        return "Done."

    def open_comm_error(self, error):
        '''
        Called when a thread ends.
        '''
        msg = MessageBox()

        # TODO: find a good exit point
        callbacks = {msg.Retry: self.restart_timer,
                     msg.Abort: lambda: sys.exit(-1)}

        fn = msg.critical("COMMUNICATION ERROR",
                          "CANNOT COMMUNICATE WITH THE HARDWARE",
                          "Check cable connections then click retry.\n"+error,
                          "COMMUNICATION ERROR",
                          callbacks)
        fn()


    def start_timer(self):
        '''
        Starts the thread.
        '''
        self._timer.start(self._config["sampling_interval"] * 1000)

    def restart_timer(self):
        if self._timer.isActive():
            self._timer.stop()

        self._timer.start(self._config["sampling_interval"] * 1000)

    def set_data(self, param, value):

        result = self._esp32.set(param, value)

        return result == self._config['return_success_code']

