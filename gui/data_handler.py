#!/usr/bin/env python3
import sys
import datetime
from PyQt5.QtCore import QTimer
from messagebox import MessageBox

class DataHandler():
    '''
    This class takes care of starting a new QTimer which
    is entirey dedicated to read data from the ESP32.
    '''

    def __init__(self, config, esp32, data_filler, alarm_class=None):
        '''
        Initializes this class by creating a new QTimer

        arguments:
        - config: the config dictionary
        - esp32: the esp32serial instance
        - data_filler: the instance to the DataFiller class 
        - alarm_class: 
        '''

        self._config = config
        self._esp32 = esp32
        self._data_f = data_filler
        self._alarm = alarm_class

        self._timer = QTimer()
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

        # print('Got data at time', datetime.datetime.now(), '=>', parameter, data)
        status = self._data_f.add_data_point(parameter, data)
        # self._alarm.set_data(parameter, data)


    def esp32_io(self):
        '''
        This is the main function that runs every time a QTimer times out.
        It runs the get_all to get the data from the ESP.
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
        Opens a message window if there is a communication error.
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
        Starts the QTimer.
        '''
        self._timer.start(self._config["sampling_interval"] * 1000)

    def stop_timer(self):
        '''
        Stops the QTimer.
        '''
        self._timer.stop()

    def restart_timer(self):
        '''
        Restarts the QTimer if the QTimer is active,
        or simply starts the QTimer
        '''
        if self._timer.isActive():
            self.stop_timer()

        self._timer.start(self._config["sampling_interval"] * 1000)

    def set_data(self, param, value):
        '''
        Sets data to the ESP
        '''

        result = self._esp32.set(param, value)

        return result == self._config['return_success_code']

