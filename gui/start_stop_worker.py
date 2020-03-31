from PyQt5 import QtCore, QtGui, QtWidgets



class StartStopWorker():
    '''
    A class entirely dedicated to start and stop 
    the ventilator. For now, this is called from the
    mainwindow, or from the settings panel.
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

        self.mode = self.MODE_STOP
        self.desired_mode = self.MODE_AUTO
        return 

    def toggle_mode(self):
        if self.desired_mode == self.MODE_AUTO:
            self.desired_mode = self.MODE_ASSIST
            self.button_autoassist.setText("Assisted")
        else:
            self.desired_mode = self.MODE_AUTO
            self.button_autoassist.setText("Automatic")

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
        self.button_startstop.repaint()
        self.button_autoassist.repaint()

        self.button_startstop.setText("Start")
        self.button_startstop.setStyleSheet("color: black")

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
        print('Setting timeout')
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
        Toggles between desired mode (MODE_ASSIST or MODE_AUTO) and MODE_STOP.
        """

        print('Current mode: {}'.format(self.mode))
        if self.mode == self.MODE_STOP:
            self.mode = self.desired_mode

            # Send signal to ESP to start automatic mode
            result = self.esp32.set('mode', self.mode)
            result = self.esp32.set('run', self.DO_RUN)

            if result != self.config['return_success_code']:
                print(f"\033[91mERROR: Failed to start with mode AUTOMATIC.\033[0m")

            self.start_button_pressed()


        else:
            if self.confirm_stop_pressed():
                self.mode = self.MODE_STOP
                
                # Send signal to ESP to stop running
                self.esp32.set('run', self.DONOT_RUN)
                self.esp32.set('mode', self.MODE_STOP)

                self.stop_button_pressed()

