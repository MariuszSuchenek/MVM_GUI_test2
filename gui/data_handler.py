#!/usr/bin/python3
import sys, traceback
import random, time
from PyQt5.QtCore import QThreadPool
from communication.esp32serial import ESP32Serial
from communication.threading_utils import Worker

class DataHandler():
    '''
    This class takes care of starting a new QThread which
    is entirey dedicated to reading data from the ESP32.
    You will need to connect a DataFiller using connect_data_filler(),
    and this class will fill the data direclty.
    '''

    def __init__(self, port):
        '''
        Initializes this class by creating a new QThreadPool
        '''
        self._threadpool = QThreadPool()
        print('Number of available threads:', self._threadpool.maxThreadCount())

        self._port = port

        self._n_attempts = 0

    def connect_data_filler(self, data_filler):
        '''
        Connects a DataFiller to this class
        '''
        self._data_f = data_filler

    def eps32_data_callback(self, parameter, data):
        '''
        This method is called everytime there is a new read from 
        the ESP32, and it receives the parameters read, and
        the data associated to it
        '''
        # print('Got data:', parameter, data)
        status = self._data_f.add_data_point(parameter, data)

        if not status:
            print(f"\033[91mERROR: Will ingore parameter {parameter}.\033[0m")

    def eps32_io(self, data_callback):
        '''
        This is the main function that runs in the thread.
        As of now, it generated random data which is set in 
        the ESP, and the same data is then retrieved.
        '''
        
        try:
            esp32 = ESP32Serial(self._port)
        except:
            print(f"\033[91mERROR: Cannot communicate with port {self._port}\033[0m")
            return

        
        while True:
            # set a random value for now
            result = esp32.set("mve", random.randint(10, 40))
            result = esp32.set("vti", random.randint(10, 40))
            result = esp32.set("vte", random.randint(10, 40))

            if result != 'OK':
                print(f"\033[91mERROR: Failed to retrieve parameter from the EPS!\033[0m")
                return

            # retrieve the same random value
            mve = float(esp32.get("mve"))
            vti = float(esp32.get("vti"))
            vte = float(esp32.get("vte"))
            
            # data_callback emits a signal, which is
            # received by eps32_data_callback, which 
            # then sets the parameters in the DataFiller
            data_callback.emit('mve', mve)
            data_callback.emit('vti', vti)
            data_callback.emit('vte', vte)

            # Sleep for some time...
            time.sleep(0.1)

        return "Done."    
            
    def thread_complete(self):
        '''
        Called when a thread ends.
        '''
        print(f"\033[91mERROR: The I/O thread finished! Going to start a new one...\033[0m")
        self._n_attempts += 1
        if self._n_attempts > 100:
            raise Exception('Failed to communicate with ESP after 100 attempts.')
        self.start_io_thread()

    def start_io_thread(self):
        '''
        Starts the thread.
        '''
        worker = Worker(self.eps32_io)
        worker.signals.result.connect(self.eps32_data_callback)
        worker.signals.finished.connect(self.thread_complete) 

        self._threadpool.start(worker) 



