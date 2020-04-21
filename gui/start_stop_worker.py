'''
A file from class StartStopWorker
'''

from PyQt5 import QtCore, QtGui, QtWidgets
from messagebox import MessageBox


class StartStopWorker():
    '''
    A class entirely dedicated to start and stop
    the ventilator, and also to set the ventilator
    mode. For now, this is called only from the
    mainwindow.
    '''
    MODE_PCV = 0
    MODE_PSV = 1

    DO_RUN = 1
    DONOT_RUN = 0

    def __init__(self, main_window, config, esp32, button_startstop,
            button_autoassist, toolbar, settings):
        self.main_window = main_window
        self.config = config
        self.esp32 = esp32
        self.button_startstop = button_startstop
        self.button_autoassist = button_autoassist
        self.toolbar = toolbar
        self.settings = settings

        self.mode_text = "PCV"

        self.mode = self.MODE_PCV
        self.run  = self.DONOT_RUN
        return

    def raise_comm_error(self, message):
        """
        Opens an error window with 'message'.
        """

        # TODO: find a good exit point
        msg = MessageBox()
        msg.critical('COMMUNICATION ERROR',
                     'Error communicating with the hardware', message,
                     '** COMMUNICATION ERROR **', {msg.Ok: lambda:
                         sys.exit(-1)})()
    def is_running(self):
        """
        A simple function that returns true if running.
        """
        return self.run == self.DO_RUN


    def toggle_mode(self):
        """
        Toggles between desired mode (MODE_PCV or MODE_PSV).
        """
        if self.mode == self.MODE_PCV:
            result = self.esp32.set('mode', self.MODE_PSV)

            if result:
                self.mode_text = "PSV"
                self.button_autoassist.setText("Set\nPCV")
                self.update_startstop_text()
                self.mode = self.MODE_PSV
            else:
                self.raise_comm_error('Cannot set PSV mode.')

        else:
            result = self.esp32.set('mode', self.MODE_PCV)

            if result:
                self.mode_text = "PCV"
                self.button_autoassist.setText("Set\nPSV")
                self.update_startstop_text()
                self.mode = self.MODE_PCV
            else:
                self.raise_comm_error('Cannot set PCV mode.')

    def update_startstop_text(self):
        '''
        Updates the text in the Start/Stop button
        '''
        if self.run == self.DONOT_RUN:
            self.button_startstop.setText("Start\n" + self.mode_text)
            self.toolbar.set_stopped(self.mode_text)
        else:
            self.button_startstop.setText("Stop\n" + self.mode_text)
            self.toolbar.set_running(self.mode_text)


    def start_button_pressed(self):
        '''
        Callback for when the Start button is pressed
        '''
        self.button_startstop.setDisabled(True)
        self.button_autoassist.setDisabled(True)
        self.button_startstop.repaint()
        self.button_autoassist.repaint()
        self.update_startstop_text()

        self.settings.disable_special_ops_tab()

        QtCore.QTimer.singleShot(self.button_timeout(), lambda: (
                 self.update_startstop_text(),
                 self.button_startstop.setEnabled(True),
                 self.button_startstop.setStyleSheet("color: red"),
                 self.toolbar.set_running(self.mode_text)))

    def stop_button_pressed(self):
        '''
        Callback for when the Stop button is pressed
        '''
        self.button_startstop.setEnabled(True)
        self.button_autoassist.setEnabled(True)

        self.update_startstop_text()
        self.button_startstop.setStyleSheet("color: black")

        self.button_startstop.repaint()
        self.button_autoassist.repaint()

        self.toolbar.set_stopped(self.mode_text)
        self.settings.enable_special_ops_tab()

    def confirm_start_pressed(self):
        '''
        Opens a window which asks for confirmation
        when the Start button is pressed.
        '''
        self.button_autoassist.setDown(False)
        currentMode = self.mode_text.upper()
        msg = MessageBox()
        ok = msg.question("**STARTING %s MODE**" % currentMode,
                          "Are you sure you want to START %s MODE?" %
                           currentMode,
                           None, "IMPORTANT", { msg.Yes: lambda: True,
                           msg.No: lambda: False })()
        return ok

    def confirm_stop_pressed(self):
        '''
        Opens a window which asks for confirmation
        when the Stop button is pressed.
        '''
        self.button_autoassist.setDown(False)
        currentMode = self.mode_text.upper()
        msg = MessageBox()
        ok = msg.question("**STOPPING %s MODE**" % currentMode,
                          "Are you sure you want to STOP %s MODE?" %
                           currentMode,
                           None, "IMPORTANT", { msg.Yes: lambda: True,
                           msg.No: lambda: False })()
        return ok


    def button_timeout(self):
        '''
        Waits for some time before making
        the Stop button visible
        '''
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
            if self.confirm_start_pressed():
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


    def _stop_abruptly(self):
        '''
        If the hardware stops running, this
        changes the test in the bottons and status.
        '''
        self.run = self.DONOT_RUN
        self.stop_button_pressed()

    def set_run(self, run):
        '''
        Sets the run variable directly.
        Usually called at start up, when reading
        the run value from the ESP.
        '''
        if self.run == run:
            return

        if self.run == self.DO_RUN:
            msg = MessageBox()
            msg.critical('STOPPING VENTILATION',
                         'The hardware has stopped the ventilation.',
                         'The microcontroller has stopped the ventilation by sending run = '+str(run),
                         'The microcontroller has stopped the ventilation by sending run = '+str(run),
                         {msg.Ok: self._stop_abruptly})()

        else:
            self.toggle_start_stop()

    def set_mode(self, mode):
        '''
        Sets the mode variable directly.
        Usually called at start up, when reading
        the mode value from the ESP.
        '''
        if self.mode != mode:
            self.toggle_mode()


