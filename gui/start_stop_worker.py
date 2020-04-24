'''
A file from class StartStopWorker
'''
import sys
from PyQt5 import QtCore
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
        self._main_window = main_window
        self._config = config
        self._esp32 = esp32
        self._button_startstop = button_startstop
        self._button_autoassist = button_autoassist
        self._toolbar = toolbar
        self._settings = settings
        self._messagebar = self._main_window.messagebar

        self._mode_text = "PCV"

        self._mode = self.MODE_PCV
        self._run = self.DONOT_RUN


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
        return self._run == self.DO_RUN


    def toggle_mode(self):
        """
        Toggles between desired mode (MODE_PCV or MODE_PSV).
        """
        if self._mode == self.MODE_PCV:
            result = self._esp32.set('mode', self.MODE_PSV)

            if result:
                self._mode_text = "PSV"
                self._button_autoassist.setText("Set\nPCV")
                self.update_startstop_text()
                self._mode = self.MODE_PSV
            else:
                self.raise_comm_error('Cannot set PSV mode.')

        else:
            result = self._esp32.set('mode', self.MODE_PCV)

            if result:
                self._mode_text = "PCV"
                self._button_autoassist.setText("Set\nPSV")
                self.update_startstop_text()
                self._mode = self.MODE_PCV
            else:
                self.raise_comm_error('Cannot set PCV mode.')

    def update_startstop_text(self):
        '''
        Updates the text in the Start/Stop button
        '''
        if self._run == self.DONOT_RUN:
            self._button_startstop.setText("Start\n" + self._mode_text)
            self._toolbar.set_stopped(self._mode_text)
        else:
            self._button_startstop.setText("Stop\n" + self._mode_text)
            self._toolbar.set_running(self._mode_text)


    def start_button_pressed(self):
        '''
        Callback for when the Start button is pressed
        '''
        # Send signal to ESP to start running
        result = self._esp32.set('run', self.DO_RUN)

        if result:
            self._run = self.DO_RUN
            self.show_stop_button()
        else:
            self.raise_comm_error('Cannot start ventilator.')

    def show_stop_button(self):
        '''
        Shows the stop button
        '''
        self._button_startstop.setDisabled(True)
        self._button_autoassist.setDisabled(True)
        self._button_startstop.repaint()
        self._button_autoassist.repaint()
        self.update_startstop_text()

        self._settings.disable_special_ops_tab()

        QtCore.QTimer.singleShot(self.button_timeout(), lambda: (
                                 self.update_startstop_text(),
                                 self._button_startstop.setEnabled(True),
                                 self._button_startstop.setStyleSheet("color: red"),
                                 self._toolbar.set_running(self._mode_text)))


    def stop_button_pressed(self):
        '''
        Callback for when the Stop button is pressed
        '''
        # Send signal to ESP to stop running
        result = self._esp32.set('run', self.DONOT_RUN)

        if result:
            self._run = self.DONOT_RUN
            self.show_start_button()
        else:
            self.raise_comm_error('Cannot stop ventilator.')

    def show_start_button(self):
        '''
        Shows the start button
        '''
        self._button_startstop.setEnabled(True)
        self._button_autoassist.setEnabled(True)

        self.update_startstop_text()
        self._button_startstop.setStyleSheet("color: black")

        self._button_startstop.repaint()
        self._button_autoassist.repaint()

        self._toolbar.set_stopped(self._mode_text)
        self._settings.enable_special_ops_tab()

    def confirm_start_pressed(self):
        '''
        Opens a window which asks for confirmation
        when the Start button is pressed.
        '''
        self._button_autoassist.setDown(False)
        currentMode = self._mode_text.upper()
        self._messagebar.get_confirmation(
                "**STARTING %s MODE**" % currentMode,
                "Are you sure you want to START %s MODE?" % currentMode,
                func_confirm=self.start_button_pressed)

    def confirm_stop_pressed(self):
        '''
        Opens a window which asks for confirmation
        when the Stop button is pressed.
        '''
        self._button_autoassist.setDown(False)
        currentMode = self._mode_text.upper()
        self._messagebar.get_confirmation(
                "**STOPPING %s MODE**" % currentMode,
                "Are you sure you want to STOP %s MODE?" % currentMode,
                func_confirm=self.stop_button_pressed)

    def button_timeout(self):
        '''
        Waits for some time before making
        the Stop button visible
        '''
        timeout = 1000
        # Set timeout for being able to stop this mode
        if 'start_mode_timeout' in self._config:
            timeout = self._config['start_mode_timeout']
            # set maximum timeout
            if timeout > 3000:
                timeout = 3000
        return timeout

    def toggle_start_stop(self):
        """
        Toggles between desired run state (DO_RUN or DONOT_RUN).
        """

        if self._run == self.DONOT_RUN:
            self.confirm_start_pressed()
        else:
            self.confirm_stop_pressed()


    def _stop_abruptly(self):
        '''
        If the hardware stops running, this
        changes the test in the bottons and status.
        '''
        self._run = self.DONOT_RUN
        self.show_start_button()

    def set_run(self, run):
        '''
        Sets the run variable directly.
        Usually called at start up, when reading
        the run value from the ESP.
        '''
        if self._run == run:
            return

        if self._run == self.DO_RUN:
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
        if self._mode != mode:
            self.toggle_mode()


