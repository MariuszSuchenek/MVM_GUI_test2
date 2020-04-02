#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets
import os
import yaml

from presets.presets import Presets

class Settings(QtWidgets.QMainWindow):
    def __init__(self, config, *args):
        """
        Initialized the Settings overlay widget.
        """
        super(Settings, self).__init__(*args)
        uic.loadUi("settings/settings.ui", self)

        self._debug = True

        self._config = config

        # This contains all the default params
        self._current_values = {}
        self._current_values_temp = {}

        # Don't ask me why I am redefining these...

        # Automatic
        self._load_preset_auto_btn = self.pushButton_load_preset_auto
        self._apply_automatic_btn = self.pushButton_apply_auto
        self._close_1_btn = self.pushButton_close_1

        # Assisted
        self._load_preset_assist_btn = self.pushButton_load_preset_assist
        self._apply_assisted_btn = self.pushButton_apply_assist
        self._close_2_btn = self.pushButton_close_2

        self._all_spinboxes = {
            # Auto
            'respiratory_rate':  self.spinBox_rr,
            'insp_expir_ratio':  self.spinBox_insp_expir_ratio,
            'insp_pressure':     self.spinBox_insp_pressure,
            'peep_auto':         self.spinBox_peep_auto,
            # Assist
            'pressure_trigger':  self.spinBox_pressure_trigger,
            'flow_trigger':      self.spinBox_flow_trigger,
            'support_pressure':  self.spinBox_support_pressure,
            'peep_assist':       self.spinBox_peep_assist,
            'minimal_resp_rate': self.spinBox_min_resp_rate,
        }

        self._all_fakebtn_auto = {
            # Auto
            'respiratory_rate': self.fake_btn_rr,
            'insp_expir_ratio': self.fake_btn_ie,
            'insp_pressure':    self.fake_btn_insp_pressure,
            'peep_auto':        self.fake_btn_peep_auto,
            # Assist
            'pressure_trigger':  self.fake_btn_pr_trigger,
            'flow_trigger':      self.fake_btn_flow_trig,
            'support_pressure':  self.fake_btn_support_pressure,
            'peep_assist':       self.fake_btn_peep_assist,
            'minimal_resp_rate': self.fake_btn_min_resp_rate,
        }

        # Init presets
        self._current_preset = None
        self._current_preset_name = None

        # Auto
        self._all_fakebtn_auto['respiratory_rate'].clicked.connect(lambda: self.spawn_presets_window('respiratory_rate'))
        self._all_fakebtn_auto['insp_expir_ratio'].clicked.connect(lambda: self.spawn_presets_window('insp_expir_ratio'))
        self._all_fakebtn_auto['insp_pressure'].clicked.connect(lambda: self.spawn_presets_window('insp_pressure'))
        self._all_fakebtn_auto['peep_auto'].clicked.connect(lambda: self.spawn_presets_window('peep_auto'))

        # Assist
        self._all_fakebtn_auto['pressure_trigger'].clicked.connect(lambda: self.spawn_presets_window('pressure_trigger'))
        self._all_fakebtn_auto['flow_trigger'].clicked.connect(lambda: self.spawn_presets_window('flow_trigger'))
        self._all_fakebtn_auto['support_pressure'].clicked.connect(lambda: self.spawn_presets_window('support_pressure'))
        self._all_fakebtn_auto['peep_assist'].clicked.connect(lambda: self.spawn_presets_window('peep_assist'))
        self._all_fakebtn_auto['minimal_resp_rate'].clicked.connect(lambda: self.spawn_presets_window('minimal_resp_rate'))




    def spawn_presets_window(self, name):

        presets = self._config[name]['presets']

        self._current_preset_name = name

        if self._current_preset is not None:
            self._current_preset.close()

        self._current_preset = Presets(presets, self)
        self._current_preset.show()
        self._current_preset.button_cancel.pressed.connect(self.hide_preset_worker)
        for btn in self._current_preset.button_preset:
            btn.pressed.connect(self.preset_worker)

        self.inactivate_settings_buttons()

        # Always set the focus to the tab
        self.tabWidget.setFocus()


    def hide_preset_worker(self):
        '''
        Hides the Preset window
        '''
        self._current_preset.hide()
        # Reset the Settings window
        self.repaint()

        # Always set the focus to the tab
        self.tabWidget.setFocus()

    def preset_worker(self):

        value = self.sender().text()
        value = value.split(' ')[0]
        value = float(value)

        self._all_spinboxes[self._current_preset_name].setValue(value)
        self._current_values_temp[self._current_preset_name] = value

        self.hide_preset_worker()



    def inactivate_settings_buttons(self):
        return

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
        for btn in self._all_spinboxes.values():
            btn.valueChanged.connect(self.worker)

        self._apply_automatic_btn.clicked.connect(self.start_worker)
        self._apply_assisted_btn.clicked.connect(self.start_worker)

        self._load_preset_auto_btn.clicked.connect(self.load_presets)
        self._load_preset_assist_btn.clicked.connect(self.load_presets)

        self._close_1_btn.clicked.connect(self.close_settings_worker)
        self._close_2_btn.clicked.connect(self.close_settings_worker)


    def load_presets(self):
        '''
        Loads the presets from the config file
        '''

        for param, btn in self._all_spinboxes.items():
            value_config = self._config[param]

            if param == 'enable_backup':
                btn.setChecked(value_config)
            elif param == 'insp_expir_ratio':
                btn.setValue(1./value_config['default'])
                btn.setMinimum(1./value_config['max'])
                btn.setMaximum(1./value_config['min'])
                self._current_values[param] = 1./value_config['default']
            else:
                btn.setValue(value_config['default'])
                btn.setMinimum(value_config['min'])
                btn.setMaximum(value_config['max'])
                self._current_values[param] = value_config['default']

        # assign an easy lookup for toolsettings
        self.toolsettings_lookup = {}
        self.toolsettings_lookup["respiratory_rate"] = self._toolsettings["toolsettings_1"]
        self.toolsettings_lookup["insp_expir_ratio"] = self._toolsettings["toolsettings_2"]
        
        # setup the toolsettings with preset values
        self.toolsettings_lookup["respiratory_rate"].load_presets("respiratory_rate")
        self.toolsettings_lookup["insp_expir_ratio"].load_presets("insp_expir_ratio")

        self._current_values_temp = self._current_values


    def close_settings_worker(self):
        '''
        Closes the settings window, w/o applying
        any changes to the parameters
        '''
        self._current_values_temp = self._current_values

        # Restore to previous values
        for param, btn in self._all_spinboxes.items():
            if param == 'enable_backup':
                btn.setChecked(self._current_values[param])

            btn.setValue(self._current_values[param])

        self.close()


    def start_worker(self):
        '''
        Starts the run, applying all the changes selected
        '''
        self._current_values = self._current_values_temp
        self.send_values_to_hardware()
        self.close()


    def send_values_to_hardware(self):
        '''
        '''
        for param, btn in self._all_spinboxes.items():
            value = self._current_values[param]
            if self._debug: print('Value of', param, ':', value)

            # Update the value in the config file
            self._config[param]['current'] = value

            # Set color to red until we know the value has been set.
            btn.setStyleSheet("color: red")

            esp_param_name = self._config['esp_settable_param'][param]
            status = self._data_h.set_data(esp_param_name, value)

            if status:
                # Now set the color to green, as we know it has been set
                btn.setStyleSheet("color: green")

            if param == 'respiratory_rate':
                self.toolsettings_lookup["respiratory_rate"].update(value)
            elif param == 'insp_expir_ratio':
                self.toolsettings_lookup["insp_expir_ratio"].update(1/value)

    

    def worker(self):
        '''
        This is called when clicking on a SpinBox
        Sets the curently set value in temporary dict
        which will be saved if the user clicks on Apply
        '''
        for param, btn in self._all_spinboxes.items():
            if self.sender() == btn:
                if param == 'enable_backup':
                    self._current_values_temp[param] = btn.isChecked()
                    pass
                elif param == 'insp_expir_ratio':
                    self._current_values_temp[param] = 1./btn.value()
                else:
                    print('. value', btn.value())
                    self._current_values_temp[param] = btn.value()


 
