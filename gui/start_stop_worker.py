from PyQt5 import QtCore, QtGui, QtWidgets



class StartStopWorker():
    '''
    A class entirely dedicated to start and stop 
    the ventilator, and also to set the ventilator
    mode. For now, this is called only from the
    mainwindow.
    '''
    MODE_STOP = -1
    MODE_AUTO = 0
    MODE_ASSIST = 1

    DO_RUN = 1
    DONOT_RUN = 0

    def __init__(self, main_window, config, esp32, button_startstop, button_autoassist):
        self.main_window = main_window
        self.config = config
        self.esp32 = esp32
        self.button_startstop = button_startstop
        self.button_autoassist = button_autoassist

        self.mode = self.MODE_AUTO
        self.run  = self.DONOT_RUN
        return 

    def raise_comm_error(self, message):
        """
        Opens an error window with 'message'.
        """
        confirmation = QtWidgets.QMessageBox.critical(
            self.main_window, 
            '** COMMUNICATION ERROR **', 
            '** COMMUNICATION ERROR **\n' + message, 
            QtWidgets.QMessageBox.Ok, 
            QtWidgets.QMessageBox.Cancel)

    def toggle_mode(self):
        """
        Toggles between desired mode (MODE_AUTO or MODE_ASSIST).
        """
        if self.mode == self.MODE_AUTO:
            result = self.esp32.set('mode', self.MODE_ASSIST)

            if result:
                self.button_autoassist.setText("Assisted")
                self.mode = self.MODE_ASSIST
            else:
                self.raise_comm_error('Cannot set assisted mode.')

        else:
            result = self.esp32.set('mode', self.MODE_AUTO)

            if result:
                self.button_autoassist.setText("Automatic")
                self.mode = self.MODE_AUTO
            else:
                self.raise_comm_error('Cannot set automatic mode.')

    def start_button_pressed(self):
        self.button_startstop.setDisabled(True)
        self.button_autoassist.setDisabled(True)
        self.button_startstop.repaint()
        self.button_autoassist.repaint()

        self.button_startstop.setText("Stop")
        QtCore.QTimer.singleShot(self.button_timeout(), lambda: ( 
                 self.button_startstop.setEnabled(True),
                 self.button_startstop.setStyleSheet("color: red")))

    def stop_button_pressed(self):
        self.button_startstop.setEnabled(True)
        self.button_autoassist.setEnabled(True)

        self.button_startstop.setText("Start")
        self.button_startstop.setStyleSheet("color: black")

        self.button_startstop.repaint()
        self.button_autoassist.repaint()

    def confirm_stop_pressed(self):
        self.button_autoassist.setDown(False)
        currentMode = self.button_autoassist.text().upper()
        confirmation = QtWidgets.QMessageBox.warning(
            self.main_window, 
            '**STOPPING ' + currentMode + ' MODE**', 
            "Are you sure you want to STOP " + currentMode + " MODE?", 
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, 
            QtWidgets.QMessageBox.Cancel)
        return confirmation == QtWidgets.QMessageBox.Ok


    def button_timeout(self):
        timeout = 1000
        # Set timeout for being able to stop this mode
        if 'start_mode_timeout' in self.config:
            timeout = self.config['start_mode_timeout']
            # set maximum timeout
            if timeout > 3000: 
                timeout = 3000
        return timeout

    def toggle_start_stop(self):
        """
        Toggles between desired run state (DO_RUN or DONOT_RUN).
        """

        if self.run == self.DONOT_RUN:

            # Send signal to ESP to start running
            result = self.esp32.set('run', self.DO_RUN)

            if result:
                self.run = self.DO_RUN
                self.start_button_pressed()
            else:
                self.raise_comm_error('Cannot start ventilator.')


        else:
            if self.confirm_stop_pressed():

                # Send signal to ESP to stop running
                result = self.esp32.set('run', self.DONOT_RUN)

                if result:
                    self.run = self.DONOT_RUN
                    self.stop_button_pressed()
                else:
                    self.raise_comm_error('Cannot stop ventilator.')


