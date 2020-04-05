#!/usr/bin/env python3

from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api

from mvm_basics import *

def test_basics(qtbot):
    '''
    Basic test that works more like a sanity check 
    to ensure we are setting up a QApplication properly
    '''
    assert qt_api.QApplication.instance() is not None

    widget = qt_api.QWidget()
    qtbot.addWidget(widget)
    widget.setWindowTitle("W1")
    widget.show()

    assert widget.isVisible()
    assert widget.windowTitle() == "W1"

from mainwindow import MainWindow

def test_menu(qtbot):
    '''
    Tests that the menu opens
    '''

    assert qt_api.QApplication.instance() is not None

    window = MainWindow(config, esp32)
    qtbot.addWidget(window)
    qtbot.mouseClick(window.button_menu, QtCore.Qt.LeftButton)
    assert window.bottombar.currentIndex() == 1














