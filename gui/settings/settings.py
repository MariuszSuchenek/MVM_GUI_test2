#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets
import os
import yaml

class Settings(QtWidgets.QMainWindow):
    def __init__(self, config, *args):
        """
        Initialized the Settings overlay widget.
        """
        super(Settings, self).__init__(*args)
        uic.loadUi("settings/settings.ui", self)

        self._debug = False

        self._config = config

        # Don't ask me why I am redefining these...

        # Automatic
        self._respiratory_rate_input = self.spinBox_rr
        self._insp_expir_ratio_input = self.spinBox_insp_expir_ratio
        self._load_preset_auto_btn = self.pushButton_load_preset_auto
        self._start_automatic_btn = self.pushButton_start_auto
        self._close_1_btn = self.pushButton_close_1

        # Assisted
        self._pressure_trigger_input = self.spinBox_pressure_trigger
        self._flow_trigger_input = self.spinBox_flow_trigger
        self._min_resp_rate_input = self.spinBox_min_resp_rate
        self._enable_backup_checkbox = self.checkBox_enable_backup
        self._load_preset_assist_btn = self.pushButton_load_preset_assist
        self._start_assisted_btn = self.pushButton_start_assist
        self._close_2_btn = self.pushButton_close_2


    def connect_data_handler(self, data_h):
        '''
        Connects the handler to this class, 
        so to have it avalable to set data
        '''
        self._data_h = data_h


    def connect_toolsettings(self, toolsettings):
        '''
        Connetcs the toolsettings to this class,
        so we can update their values
        '''
        self._toolsettings = toolsettings


    def connect_start_stop_worker(self, start_stop_worker):
        '''
        Receives the StartStopWorker from the mainwindow
        and stores it here, as it will be called when the
        Start button is pressed from the settings panel
        '''
        self._start_stop_worker = start_stop_worker


    def connect_workers(self):
        '''
        Connects all the buttons, inputs, etc
        to the the appropriate working function
        '''
        self._respiratory_rate_input.valueChanged.connect(self.resp_rate_worker)
        self._insp_expir_ratio_input.valueChanged.connect(self.insp_expir_ratio_worker)

        self._pressure_trigger_input.valueChanged.connect(self.pressure_trigger_worker)
        self._flow_trigger_input.valueChanged.connect(self.flow_trigger_worker)
        self._min_resp_rate_input.valueChanged.connect(self.min_resp_rate_worker)
        self._enable_backup_checkbox.stateChanged.connect(self.enable_backup_worker)

        self._start_automatic_btn.clicked.connect(self.start_worker_auto)
        self._start_assisted_btn.clicked.connect(self.start_worker_assist)

        self._load_preset_auto_btn.clicked.connect(self.load_presets_auto)
        self._load_preset_assist_btn.clicked.connect(self.load_presets_assist)

        self._close_1_btn.clicked.connect(self.close_settings_worker)
        self._close_2_btn.clicked.connect(self.close_settings_worker)


    def load_presets_auto(self):

        rr = self._config['respiratory_rate']
        self._respiratory_rate_input.setValue(rr['default'])
        self._respiratory_rate_input.setMinimum(rr['min'])
        self._respiratory_rate_input.setMaximum(rr['max'])

        ie = self._config['insp_expir_ratio']
        self._insp_expir_ratio_input.setValue(ie['default'])
        self._insp_expir_ratio_input.setMinimum(ie['min'])
        self._insp_expir_ratio_input.setMaximum(ie['max'])

        self.resp_rate_worker()
        self.insp_expir_ratio_worker()

        self._respiratory_rate_input.hide()
        self._respiratory_rate_input.show()

        self._insp_expir_ratio_input.hide()
        self._insp_expir_ratio_input.show()


        try:
            self._toolsettings[0].update_range(valuerange=(rr['min'],rr['max']))
            self._toolsettings[1].update_range(valuerange=(ie['min'],ie['max']))
        except:
            pass

    def load_presets_assist(self):

        pt = self._config['pressure_trigger']
        self._pressure_trigger_input.setValue(pt['default'])
        self._pressure_trigger_input.setMinimum(pt['min'])
        self._pressure_trigger_input.setMaximum(pt['max'])

        ft = self._config['flow_trigger']
        self._flow_trigger_input.setValue(ft['default'])
        self._flow_trigger_input.setMinimum(ft['min'])
        self._flow_trigger_input.setMaximum(ft['max'])

        mr = self._config['minimal_resp_rate']
        self._min_resp_rate_input.setValue(mr['default'])
        self._min_resp_rate_input.setMinimum(mr['min'])
        self._min_resp_rate_input.setMaximum(mr['max'])

        eb = self._config['enable_backup']
        self._enable_backup_checkbox.setChecked(eb)

        self.pressure_trigger_worker()
        self.flow_trigger_worker()
        # self.min_resp_rate_worker()
        # self.enable_backup_worker()

        self._pressure_trigger_input.hide()
        self._pressure_trigger_input.show()

        self._flow_trigger_input.hide()
        self._flow_trigger_input.show()

        self._min_resp_rate_input.hide()
        self._min_resp_rate_input.show()


    def close_settings_worker(self):
        '''
        Closes the settings window
        '''
        self.close()


    def start_worker_auto(self):
        '''
        Starts the run
        '''
        self._start_stop_worker.toggle_automatic()
        self.close()


    def start_worker_assist(self):
        '''
        Starts the run
        '''
        self._start_stop_worker.toggle_assisted()
        self.close()


    def resp_rate_worker(self):
        '''
        Worker function that sets the respiratory rate in the arduino
        When the request to update values is made, the color of the 
        number is red. When the number is written to the arduino, the 
        color becomes green. It is usually very fast, and so you
        cannot notice the red.
        AUTOMATIC
        '''
        rr = self._respiratory_rate_input.value()
        
        if self._debug: print('Setting RR to', rr)

        # Update the value in the config file
        self._config['respiratory_rate']['current'] = rr

        # Set color to red until we know the value has been set.
        self._respiratory_rate_input.setStyleSheet("color: red")

        status = self._data_h.set_data('rate', rr)

        if status == True:
            # Now set the color to green, as we know it has been set
            self._respiratory_rate_input.setStyleSheet("color: green")

        # Finally, update the value in the toolsettings
        self._toolsettings[0].update(rr)

        return


    def insp_expir_ratio_worker(self):
        '''
        Worker function that sets the insp/expir ratio in the arduino
        When the request to update values is made, the color of the 
        number is red. When the number is written to the arduino, the 
        color becomes green. It is usually very fast, and so you
        cannot notice the red.
        AUTOMATIC
        '''
        den = self._insp_expir_ratio_input.value()
        ratio = 1./den
        
        if self._debug: print('value of Ratio', ratio)

        # Update the value in the config file
        self._config['insp_expir_ratio']['current'] = ratio

        # Set color to red until we know the value has been set.
        self._insp_expir_ratio_input.setStyleSheet("color: red")

        status = self._data_h.set_data('ratio', ratio)

        if status == True:
            # Now set the color to green, as we know it has been set
            self._insp_expir_ratio_input.setStyleSheet("color: green")

        # Finally, update the value in the toolsettings
        self._toolsettings[1].update(den)

        return


    def pressure_trigger_worker(self):
        '''
        Worker function that sets the pressure trigger in the arduino
        When the request to update values is made, the color of the 
        number is red. When the number is written to the arduino, the 
        color becomes green. It is usually very fast, and so you
        cannot notice the red.
        ASSISTED
        '''
        pressure = self._pressure_trigger_input.value()
        
        if self._debug: print('value of Pressure Trigger', pressure)

        # Update the value in the config file
        self._config['pressure_trigger']['current'] = pressure

        # Set color to red until we know the value has been set.
        self._pressure_trigger_input.setStyleSheet("color: red")

        status = self._data_h.set_data('assist_ptrigger', pressure)

        if status == True:
            # Now set the color to green, as we know it has been set
            self._pressure_trigger_input.setStyleSheet("color: green")

        # Finally, update the value in the toolsettings
        # self._toolsettings[1].update(ratio)

        return


    def flow_trigger_worker(self):
        '''
        Worker function that sets the flow trigger in the arduino
        When the request to update values is made, the color of the 
        number is red. When the number is written to the arduino, the 
        color becomes green. It is usually very fast, and so you
        cannot notice the red.
        ASSISTED
        '''
        flow = self._flow_trigger_input.value()
        
        if self._debug: print('value of Pressure Trigger', flow)

        # Update the value in the config file
        self._config['flow_trigger']['current'] = flow

        # Set color to red until we know the value has been set.
        self._flow_trigger_input.setStyleSheet("color: red")

        status = self._data_h.set_data('assist_flow_min', flow)

        if status == True:
            # Now set the color to green, as we know it has been set
            self._flow_trigger_input.setStyleSheet("color: green")

        # Finally, update the value in the toolsettings
        # self._toolsettings[1].update(ratio)

        return


    def min_resp_rate_worker(self):
        '''
        Worker function that sets the min resp rate in the arduino
        When the request to update values is made, the color of the 
        number is red. When the number is written to the arduino, the 
        color becomes green. It is usually very fast, and so you
        cannot notice the red.
        ASSISTED
        '''

        print('min_resp_rate_worker not implemented.')
        return

        # mrr = self._min_resp_rate_input.value()
        
        # if self._debug: print('value of Min Resp Rate', mrr)

        # # Set color to red until we know the value has been set.
        # self._min_resp_rate_input.setStyleSheet("color: red")

        # status = self._data_h.set_data('assist_flow_min', mrr)

        # if status == True:
        #     # Now set the color to green, as we know it has been set
        #     self._min_resp_rate_input.setStyleSheet("color: green")

        # # Finally, update the value in the toolsettings
        # # self._toolsettings[1].update(ratio)

        # return


    def enable_backup_worker(self):
        '''
        Worker function that sets the enable backup param in the arduino
        ASSISTED
        '''
        print('enable_backup_worker not implemented.')
        return


