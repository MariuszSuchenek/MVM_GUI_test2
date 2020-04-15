#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets

class NumPad():
    def __init__(self, mainparent):
        """
        Creates the numpad menu.

        numpad: The layout into which the numpad will be generated.

        """
        self.mainparent = mainparent
        self.button_back = self.mainparent.findChild(QtWidgets.QPushButton, "numpad_back")

        # Only have every other button
        self.buttons_num = []
        for i in range(0, 10, 2):
            name = "numpad_" + str(i) + str(i+1)
            button = self.mainparent.findChild(QtWidgets.QPushButton, name)
            button.pressed.connect(lambda num=i: self.input_number(num))
            self.buttons.append(button)

        self.assign_code("0000")
        self.input_values = []


    def assign_code(self, code):
        self.code = [int(d/2)*2 for d in str(code) if d.isdigit()]
        self.input_values = [0] * len(self.code)


    def input_number(self, num):
        self.input_values = self.input_values[:-2].append(num)
        print(input_values)

    
    
