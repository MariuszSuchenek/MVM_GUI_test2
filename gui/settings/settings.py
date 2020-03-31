#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets

class Settings(QtWidgets.QMainWindow):
    def __init__(self, *args):
        """
        Initialized the Settings overlay widget.
        """
        super(Settings, self).__init__(*args)
        uic.loadUi("settings/settings.ui", self)

        self._debug = True

        # Don't ask me why I am redefining these...

        # Automatic
        self._respiratory_rate_input = self.spinBox_rr
        self._insp_expir_ratio_input = self.spinBox_insp_expir_ratio
        self._load_preset_auto_btn = self.pushButton_load_preset_auto
        self._start_automatic_btn = self.pushButton_start_auto

        # Assisted
        self._pressure_trigger_input = self.spinBox_pressure_trigger
        self._flow_trigger_input = self.spinBox_flow_trigger
        self._min_resp_rate_input = self.spinBox_min_resp_rate
        self._enable_backup_checkbox = self.checkBox_enable_backup
        self._load_preset_assist_btn = self.pushButton_load_preset_assist
        self._start_assisted_btn = self.pushButton_start_assist

        

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


    def connect_workers(self):
        '''
        Connects all the buttons, inputs, etc
        to the the appropriate working function
        '''
        self._respiratory_rate_input.valueChanged.connect(self.resp_rate_worker)
        self._insp_expir_ratio_input.valueChanged.connect(self.insp_expir_ratio_worker)


    def resp_rate_worker(self):
        rr = self._respiratory_rate_input.value()
        
        if self._debug: print('Setting RR to', rr)

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
        den = self._insp_expir_ratio_input.value()
        ratio = 1./den
        
        if self._debug: print('value of Ratio', ratio)

        # Set color to red until we know the value has been set.
        self._insp_expir_ratio_input.setStyleSheet("color: red")

        status = self._data_h.set_data('ratio', ratio)

        if status == True:
            # Now set the color to green, as we know it has been set
            self._insp_expir_ratio_input.setStyleSheet("color: green")

        # Finally, update the value in the toolsettings
        self._toolsettings[1].update(ratio)

        return


