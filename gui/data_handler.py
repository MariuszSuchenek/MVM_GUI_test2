#!/usr/bin/python3
import sys, traceback
import time
from PyQt5.QtCore import QThreadPool
from communication.threading_utils import Worker

class DataHandler():
    '''
    This class takes care of starting a new QThread which
    is entirey dedicated to reading data from the ESP32.
    You will need to connect a DataFiller using connect_data_filler(),
    and this class will fill the data direclty.
    '''

    def __init__(self, config, esp32):
        '''
        Initializes this class by creating a new QThreadPool
        '''
        self._running = False
        self._threadpool = QThreadPool()
        print('Number of available threads:', self._threadpool.maxThreadCount())

        self._config = config
        self._esp32 = esp32

        self._n_attempts = 0

    def connect_data_filler(self, data_filler):
        '''
        Connects a DataFiller to this class
        '''
        self._data_f = data_filler

    def esp32_data_callback(self, parameter, data):
        '''
        This method is called everytime there is a new read from
        the ESP32, and it receives the parameters read, and
        the data associated to it
        '''
        # print('Got data:', parameter, data)
        status = self._data_f.add_data_point(parameter, data)

        if not status:
            print(f"\033[91mERROR: Will ingore parameter {parameter}.\033[0m")

    def stop_io(self):
        '''
        Ask the thread to gracefully stop iterating
        '''

        self._running = False

    def esp32_io(self, data_callback):
        '''
        This is the main function that runs in the thread.
        '''

        if self._running:
            return

        self._running = True

        while self._running:
            # retrieve the values
            mve = float(self._esp32.get("mve"))
            vti = float(self._esp32.get("vti"))
            vte = float(self._esp32.get("vte"))

            # data_callback emits a signal, which is
            # received by esp32_data_callback, which
            # then sets the parameters in the DataFiller
            data_callback.emit('mve', mve)
            data_callback.emit('vti', vti)
            data_callback.emit('vte', vte)

            # Sleep for some time...
            time.sleep(self._config['sampling_interval'])

        return "Done."

    def thread_complete(self):
        '''
        Called when a thread ends.
        '''

        if self._running:
            print(f"\033[91mERROR: The I/O thread finished! Going to start a new one...\033[0m")
            self._n_attempts += 1
            if self._n_attempts > 100:
                raise Exception('Failed to communicate with ESP after 100 attempts.')
            self.start_io_thread()

    def start_io_thread(self):
        '''
        Starts the thread.
        '''
        worker = Worker(self.esp32_io)
        worker.signals.result.connect(self.esp32_data_callback)
        worker.signals.finished.connect(self.thread_complete)

        self._threadpool.start(worker)

