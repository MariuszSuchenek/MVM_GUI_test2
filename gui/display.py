#!/usr/bin/python3
from PyQt5 import QtWidgets, uic

from toolsettings.toolsettings import ToolSettings
import pyqtgraph as pg
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('mainwindow.ui', self) # Load the .ui file
        self.pushbutton_settings = self.findChild(QtWidgets.QPushButton, "pushbutton_settings")
        self.show() # Show the GUI


app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = MainWindow() # Create an instance of our class
app.exec_() # Start the application
