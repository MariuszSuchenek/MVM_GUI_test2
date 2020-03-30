import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic


class MVMGUI(QtWidgets.QMainWindow):
    '''
    The main window of the MVM GUI application
    '''
    
    def __init__(self, uifilename='main.ui', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_ui(uifilename)

    def load_ui(self, name='main.ui'):
        uic.loadUi(name, self)

    def connect(self):
        self.pushButton.clicked.connect(self.printhi)

    def printhi(self):
        print('Hi!')
