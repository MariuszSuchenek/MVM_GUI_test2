#!/usr/bin/env python3

from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api

from mvm_basics import *
from mainwindow import MainWindow
import time


def test_run(qtbot):
    '''
    Tests that the menu opens
    '''

    assert qt_api.QApplication.instance() is not None

    window = MainWindow(config, esp32)
    qtbot.addWidget(window)

    assert "Start" in window.button_startstop.text()

    # Start running
    
    qtbot.mouseClick(window.button_startstop, QtCore.Qt.LeftButton, delay=10)

    def check_label():
        assert "Running" in window.toolbar.label_status.text()

    qtbot.waitUntil(check_label, timeout=10000)

    assert "Running" in window.toolbar.label_status.text()


    # Stop running

    # qtbot.mouseClick(window.button_startstop, QtCore.Qt.LeftButton, delay=10)

    # def check_question():
    #     messagebox = QtWidgets.QApplication.activeWindow()
    #     assert messagebox is not None
    #     yes_button = messagebox.button(QtWidgets.QMessageBox.Yes)
    #     qtbot.mouseClick(yes_button, QtCore.Qt.LeftButton, delay=1)


    # qtbot.waitUntil(check_question, timeout=10000)

    # def check_label():
    #     assert "Stopped" in window.toolbar.label_status.text()

    # qtbot.waitUntil(check_label, timeout=10000)

    # assert "Stopped" in window.toolbar.label_status.text()















