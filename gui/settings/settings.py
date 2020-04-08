#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets
import os
import yaml
import copy

from presets.presets import Presets

class Settings(QtWidgets.QMainWindow):
    def __init__(self, mainparent, *args):
        """
        Initialized the Settings overlay widget.
        """
        super(Settings, self).__init__(*args)
        uic.loadUi("settings/settings.ui", self)

        self._debug = True
        self.mainparent = mainparent

        # Get access to parent widgets and data
        self._config = self.mainparent.config
        self._data_h = self.mainparent._data_h
        self._toolsettings = self.mainparent.toolsettings
        self._start_stop_worker = self.mainparent._start_stop_worker

        # This contains all the default params
        self._current_values = {}
        self._current_values_temp = {}

        self._all_spinboxes = {
            # Auto
            'respiratory_rate':  self.spinBox_rr,
            'insp_expir_ratio':  self.spinBox_insp_expir_ratio,
            'insp_pressure':     self.spinBox_insp_pressure,
            # Assist
            'pressure_trigger':  self.spinBox_pressure_trigger,
            'flow_trigger':      self.spinBox_flow_trigger,
            'support_pressure':  self.spinBox_support_pressure,
            'minimal_resp_rate': self.spinBox_min_resp_rate,
            'enable_backup':     self.toggle_enable_backup,
        }

        self._all_fakebtn = {
            # Auto
            'respiratory_rate': self.fake_btn_rr,
            'insp_expir_ratio': self.fake_btn_ie,
            'insp_pressure':    self.fake_btn_insp_pressure,
            # Assist
            'pressure_trigger':  self.fake_btn_pr_trigger,
            'flow_trigger':      self.fake_btn_flow_trig,
            'support_pressure':  self.fake_btn_support_pressure,
            'minimal_resp_rate': self.fake_btn_min_resp_rate,
        }

        # Connect all widgets
        self.connect_workers()

        # Init presets
        self._current_preset = None
        self._current_preset_name = None

        self.load_presets()

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
        self.activate_settings_buttons()

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
        '''
        Inactivates all in the settings window
        '''
        self.tabWidget.setDisabled(True)

    def activate_settings_buttons(self):
        '''
        Activates all in the settings window
        '''
        self.tabWidget.setEnabled(True)


    def open_main_and_toolbar(self):
        '''
        Switches back to the main window and toolbar
        '''
        self.mainparent.open_main()
        self.mainparent.open_toolbar()

    def connect_workers(self):
        '''
        Connects all the buttons, inputs, etc
        to the the appropriate working functions
        '''
        # Shared apply, close, preset buttons
        self._button_apply = self.mainparent.settingsbar.findChild(QtWidgets.QPushButton, "button_apply")
        self._button_close = self.mainparent.settingsbar.findChild(QtWidgets.QPushButton, "button_close")
        self._button_loadpreset = self.mainparent.settingsbar.findChild(QtWidgets.QPushButton, "button_loadpreset")

        self._button_apply.clicked.connect(self.apply_worker)
        self._button_loadpreset.clicked.connect(self.load_presets)
        self._button_close.clicked.connect(self.close_settings_worker)


        # Auto
        self._all_fakebtn['respiratory_rate'].clicked.connect(lambda: self.spawn_presets_window('respiratory_rate'))
        self._all_fakebtn['insp_expir_ratio'].clicked.connect(lambda: self.spawn_presets_window('insp_expir_ratio'))
        self._all_fakebtn['insp_pressure'].clicked.connect(lambda: self.spawn_presets_window('insp_pressure'))

        # Assist
        self._all_fakebtn['pressure_trigger'].clicked.connect(lambda: self.spawn_presets_window('pressure_trigger'))
        self._all_fakebtn['flow_trigger'].clicked.connect(lambda: self.spawn_presets_window('flow_trigger'))
        self._all_fakebtn['support_pressure'].clicked.connect(lambda: self.spawn_presets_window('support_pressure'))
        self._all_fakebtn['minimal_resp_rate'].clicked.connect(lambda: self.spawn_presets_window('minimal_resp_rate'))

        for param, btn in self._all_spinboxes.items():
            if param == 'enable_backup':
                btn.clicked.connect(self.worker)
            else:
                btn.valueChanged.connect(self.worker)



    def load_presets(self):
        '''
        Loads the presets from the config file
        '''

        for param, btn in self._all_spinboxes.items():
            value_config = self._config[param]

            if param == 'enable_backup':
                btn.setChecked(value_config['default'])
                self._current_values[param] = value_config['default']
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

        self._current_values_temp = copy.copy(self._current_values)

        self.repaint()


    def close_settings_worker(self):
        '''
        Closes the settings window, w/o applying
        any changes to the parameters
        '''
        self._current_values_temp = copy.copy(self._current_values)

        # Restore to previous values
        for param, btn in self._all_spinboxes.items():
            if param == 'enable_backup':
                btn.setChecked(self._current_values[param])
            else:
                print('resetting', param, 'to ', self._current_values[param])
                btn.setValue(self._current_values[param])

        self.repaint()
        self.open_main_and_toolbar()


    def apply_worker(self):
        '''
        Applyes the current changes and sends them to the ESP
        '''
        self._current_values = copy.copy(self._current_values_temp)
        self.send_values_to_hardware()
        self.open_main_and_toolbar()


    def send_values_to_hardware(self):
        '''
        Sends the currently set values to the ESP
        '''
        for param, btn in self._all_spinboxes.items():
            if param == 'enable_backup':
                value = int(self._current_values[param])
            elif param == 'insp_expir_ratio':
                value = 1. - 1. / self._current_values[param]
            else:
                value = self._current_values[param]

            if self._debug: print('Setting value of', param, ':', value)

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
                    self._current_values_temp[param] = int(btn.isChecked())
                elif param == 'insp_expir_ratio':
                    self._current_values_temp[param] = 1 - 1./btn.value()
                else:
                    self._current_values_temp[param] = btn.value()

