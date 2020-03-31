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

    def __init__(self, main_window, config, esp32, button_startauto, button_startman):
        self.main_window = main_window
        self.config = config
        self.esp32 = esp32
        self.button_startauto = button_startauto
        self.button_startman = button_startman

        self.mode = self.MODE_STOP
        return 

    def start_button_pressed(self, button):
        self.button_startman.setDisabled(True)
        self.button_startauto.setEnabled(False)
        self.button_startman.repaint()
        self.button_startauto.repaint()
        text = button.text()
        text = text.replace('Start', 'Stop')
        button.setText(text)

    def stop_button_pressed(self, button):
        button.setDown(False)
        currentMode = button.text().split(' ')[1].upper()
        confirmation = QtWidgets.QMessageBox.warning(
            self.main_window, 
            '**STOPPING AUTOMATIC MODE**', 
            "Are you sure you want to STOP " + currentMode + " MODE?", 
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, 
            QtWidgets.QMessageBox.Cancel)
        
        if confirmation == QtWidgets.QMessageBox.Ok:
            self.mode = self.MODE_STOP
            text = button.text()
            text = text.replace('Stop', 'Start')
            button.setText(text)
            button.setStyleSheet("color: black")
            self.button_startauto.setEnabled(True)
            self.button_startman.setEnabled(True)
            self.button_startman.repaint()
            self.button_startauto.repaint()

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

    def toggle_automatic(self):
        """
        Toggles between automatic mode (1) and stop (0).

        Changes text from "Start" to "Stop" and en/disables assisted button depending on mode.
        """

        print('Current mode: {}'.format(self.mode))
        if self.mode == self.MODE_STOP:
            self.mode = self.MODE_AUTO

            # Send signal to ESP to start automatic mode
            result = self.esp32.set('mode', self.MODE_AUTO)
            result = self.esp32.set('run', self.DO_RUN)

            self.start_button_pressed(self.button_startauto)

            QtCore.QTimer.singleShot(self.button_timeout(), lambda: ( 
                     self.button_startauto.setDisabled(False),
                     self.button_startauto.setStyleSheet("color: red")))

        else:
            # Send signal to ESP to stop running
            self.esp32.set('run', self.DONOT_RUN)
            self.esp32.set('mode', self.MODE_STOP)

            self.stop_button_pressed(self.button_startauto)


    def toggle_assisted(self):
        """
        Toggles between assisted mode (2) and stop (0).

        Changes text from "Start" to "Stop" and en/disables automatic button depending on mode.
        """

        if self.mode == self.MODE_STOP:
            self.mode = self.MODE_ASSIST

            # Send signal to ESP to start automatic mode
            result = self.esp32.set('mode', self.MODE_ASSIST)
            result = self.esp32.set('run', self.DO_RUN)

            if result != self.config['return_success_code']:
                print(f"\033[91mERROR: Failed to start with mode AUTOMATIC.\033[0m")

            self.start_button_pressed(self.button_startman)
            
            QtCore.QTimer.singleShot(self.button_timeout(), lambda: ( 
                    self.button_startman.setDisabled(False),
                    self.button_startman.setStyleSheet("color: red")))

        else:
            # Send signal to ESP to stop running
            self.esp32.set('run', self.DONOT_RUN)
            self.esp32.set('mode', self.MODE_STOP)

            self.stop_button_pressed(self.button_startman)

      
