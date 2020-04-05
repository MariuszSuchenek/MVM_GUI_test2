
from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api

from mvm_basics import *
# from PyQt5 import QtCore, QtGui, QtWidgets
# import os, sys, yaml

# from communication.fake_esp32serial import FakeESP32Serial


# base_dir = os.path.dirname(__file__)
# settings_file = os.path.join(base_dir, 'default_settings.yaml')
# with open(settings_file) as f:
#     config = yaml.load(f, Loader=yaml.FullLoader)
# esp32 = FakeESP32Serial()

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

if __name__ == "__main__":
    test_hello()












