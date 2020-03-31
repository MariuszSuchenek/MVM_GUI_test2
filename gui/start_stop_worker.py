from PyQt5 import QtCore, QtGui, QtWidgets

STOP = -1
AUTOMATIC = 0
ASSISTED = 1

DO_RUN = 1
DONOT_RUN = 0

class StartStopWorker():
    def __init__(self, main_window, config, esp32, button_startauto, button_startman):
        self.main_window = main_window
        self.config = config
        self.esp32 = esp32
        self.button_startauto = button_startauto
        self.button_startman = button_startman

        self.mode = STOP
        return 

    def toggle_automatic(self):
        """
        Toggles between automatic mode (1) and stop (0).

        Changes text from "Start" to "Stop" and en/disables assisted button depending on mode.
        """
        if self.mode == STOP:
            self.mode = AUTOMATIC
            self.button_startman.setDisabled(True)
            self.button_startauto.setDisabled(True)

            # Set timeout for being able to stop this mode
            palette = self.button_startauto.palette()
            role = self.button_startauto.backgroundRole() 
            if 'start_mode_timeout' in self.config:
                timeout = self.config['start_mode_timeout']
                # set maximum timeout
                if timeout > 3000: 
                    timeout = 3000
            else:
                timeout = 1000
            QtCore.QTimer.singleShot(timeout, lambda: ( 
                    # change button color and enable the stop button
                    self.button_startauto.setText("Stop Automatic"),
                    palette.setColor(role, QtGui.QColor("#fc6203")),
                    self.button_startauto.setPalette(palette),
                    self.button_startauto.setEnabled(True),
                    self.button_startauto.setStyleSheet("color: red")))

            # Send signal to ESP to start automatic mode
            result = self.esp32.set('mode', AUTOMATIC)
            result = self.esp32.set('run', DO_RUN)

            if result != self.config['return_success_code']:
                print(f"\033[91mERROR: Failed to start with mode AUTOMATIC.\033[0m")

        else:
            confirmation = QtWidgets.QMessageBox.warning(
                    self.main_window, 
                    '**STOPPING AUTOMATIC MODE**', 
                    "Are you sure you want to STOP AUTOMATIC MODE?", 
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, 
                    QtWidgets.QMessageBox.Cancel)

            if confirmation == QtWidgets.QMessageBox.Ok:
                self.mode = STOP
                self.button_startauto.setText("Start Automatic")
                self.button_startman.setEnabled(True)
                self.button_startauto.setStyleSheet("color: black")

                # change button color
                palette = self.button_startauto.palette()
                role = self.button_startauto.backgroundRole() 
                palette.setColor(role, QtGui.QColor("#eeeeee"))
                self.button_startauto.setPalette(palette)

                # Send signal to ESP to stop running
                self.esp32.set('run', DONOT_RUN)
                self.esp32.set('mode', STOP)

    def toggle_assisted(self):
        """
        Toggles between assisted mode (2) and stop (0).

        Changes text from "Start" to "Stop" and en/disables automatic button depending on mode.
        """
        if self.mode == STOP:
            self.mode = ASSISTED
            self.button_startauto.setDisabled(True)
            self.button_startman.setDisabled(True)
            
            # Set timeout for being able to stop this mode
            palette = self.button_startman.palette()
            role = self.button_startman.backgroundRole() 
            if 'start_mode_timeout' in self.config:
                timeout = self.config['start_mode_timeout']
                # set maximum timeout
                if timeout > 3000: 
                    timeout = 3000
            else:
                timeout = 1000
            QtCore.QTimer.singleShot(timeout, lambda: ( 
                    # change button color and enable the stop button
                    self.button_startman.setText("Stop Assisted"),
                    palette.setColor(role, QtGui.QColor("#fc6203")),
                    self.button_startman.setPalette(palette),
                    self.button_startman.setEnabled(True),
                    self.button_startman.setStyleSheet("QPushButton {color: red;}")))

            # Send signal to ESP to start automatic mode
            result = self.esp32.set('mode', ASSISTED)
            result = self.esp32.set('run', DO_RUN)

            if result != self.config['return_success_code']:
                print(f"\033[91mERROR: Failed to start with mode ASSISTED.\033[0m")


        else:
            confirmation = QtWidgets.QMessageBox.warning(
                    self.main_window, 
                    '**STOPPING ASSISTED MODE**', 
                    "Are you sure you want to STOP ASSISTED MODE?", 
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, 
                    QtWidgets.QMessageBox.Cancel)

            if confirmation == QtWidgets.QMessageBox.Ok:
                self.mode = STOP
                self.button_startman.setText("Start Assisted")
                self.button_startauto.setEnabled(True)
                self.button_startman.setStyleSheet("color: black")

                # change button color
                palette = self.button_startman.palette()
                role = self.button_startman.backgroundRole() 
                palette.setColor(role, QtGui.QColor("#eeeeee"))
                self.button_startman.setPalette(palette)

                # Send signal to ESP to stop running
                self.esp32.set('run', DONOT_RUN)
                self.esp32.set('mode', STOP)
