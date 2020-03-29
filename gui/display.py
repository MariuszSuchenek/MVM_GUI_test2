#!/usr/bin/python3
from PyQt5 import QtWidgets, uic

from toolsettings.toolsettings import ToolSettings
import pyqtgraph as pg
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('mainwindow.ui', self) # Load the .ui file

        self.toolsettings = [];

        self.toolsettings.append(self.findChild(QtWidgets.QWidget, "toolsettings_1"))
        self.toolsettings.append(self.findChild(QtWidgets.QWidget, "toolsettings_2"))
        self.toolsettings.append(self.findChild(QtWidgets.QWidget, "toolsettings_3"))
        self.toolsettings.append(self.findChild(QtWidgets.QWidget, "toolsettings_4"))
        self.toolsettings[0].setup("O<sub>2<\sub> conc.", (21, 40, 100))
        self.toolsettings[1].setup("PEEP",                (0,   5, 50))
        self.toolsettings[2].setup("Resp. Rate",          (4,  12, 100))
        self.toolsettings[3].setup("PC Above PEEP",       (0,  25, 120))

        self.pushbutton_settings = self.findChild(QtWidgets.QPushButton, "pushbutton_settings")
        self.show() # Show the GUI


app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = MainWindow() # Create an instance of our class
app.exec_() # Start the application
