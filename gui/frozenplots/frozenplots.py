#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
import sys

class FrozenPlotsBottomMenu(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the FrozenPlotsBottomMenu widget.

        Grabs child widgets.
        """
        super(FrozenPlotsBottomMenu, self).__init__(*args)
        uic.loadUi("frozenplots/frozenplots_bottom.ui", self)

        self.button_reset_zoom = self.findChild(QtWidgets.QPushButton, "button_reset_zoom")
        self.xzoom = self.findChild(QtWidgets.QWidget, "xzoom")
        
    def connect_workers(self, data_filler, plots):
        '''
        Connect workers for bottom "freeze" menu.
        The unfreeze button is handled by mainwindow.
        '''
        self.button_reset_zoom.pressed.connect(data_filler.reset_zoom)
        
        # X axes are linked, so only need to manipulate 1 plot
        self.xzoom.connect_workers(plots[0].getPlotItem())

class FrozenPlotsRightMenu(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the FrozenPlotsRightMenu widget.

        Grabs child widgets.
        """
        super(FrozenPlotsRightMenu, self).__init__(*args)
        uic.loadUi("frozenplots/frozenplots_right.ui", self)

        self.yzoom_top = self.findChild(QtWidgets.QWidget, "yzoom_top")
        self.yzoom_mid = self.findChild(QtWidgets.QWidget, "yzoom_mid")
        self.yzoom_bot = self.findChild(QtWidgets.QWidget, "yzoom_bot")

    def connect_workers(self, plots):
        '''
        Connect Y zoom workers. There are 3 widgets, each controlling
        a separate plot.
        '''
        self.yzoom_top.connect_workers(plots[0].getPlotItem())
        self.yzoom_mid.connect_workers(plots[1].getPlotItem())
        self.yzoom_bot.connect_workers(plots[2].getPlotItem())
    
class YZoom(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the YZoom widget.

        Grabs child widgets.
        """
        super(YZoom, self).__init__(*args)
        uic.loadUi("frozenplots/y_zoom.ui", self)
        
        self.button_plus = self.findChild(QtWidgets.QPushButton, "y_plus")
        self.button_minus = self.findChild(QtWidgets.QPushButton, "y_minus")
        self.button_up = self.findChild(QtWidgets.QPushButton, "y_up")
        self.button_down = self.findChild(QtWidgets.QPushButton, "y_down")
        
        self.zoom_factor = 1.25
        self.translate_factor = 0.1
        
    def connect_workers(self, plot):
        self.button_plus.pressed.connect(lambda: self.zoom_in(plot))
        self.button_minus.pressed.connect(lambda: self.zoom_out(plot))
        self.button_up.pressed.connect(lambda: self.shift_up(plot))
        self.button_down.pressed.connect(lambda: self.shift_down(plot))
        
    def zoom_in(self, plot):
        plot.getViewBox().scaleBy(y=1/self.zoom_factor)
    
    def zoom_out(self, plot):
        plot.getViewBox().scaleBy(y=self.zoom_factor)
       
    def compute_translation(self, plot):
        [[xmin, xmax], [ymin, ymax]] = plot.viewRange()
        return (ymax - ymin) * self.translate_factor
    
    def shift_up(self, plot):
        plot.getViewBox().translateBy(y=self.compute_translation(plot))
        
    def shift_down(self, plot):
        plot.getViewBox().translateBy(y=-self.compute_translation(plot))
        
class XZoom(QtWidgets.QWidget):
    def __init__(self, *args):
        """
        Initialize the XZoom widget.

        Grabs child widgets.
        """
        super(XZoom, self).__init__(*args)
        uic.loadUi("frozenplots/x_zoom.ui", self)
        
        self.button_plus = self.findChild(QtWidgets.QPushButton, "x_plus")
        self.button_minus = self.findChild(QtWidgets.QPushButton, "x_minus")
        self.button_left = self.findChild(QtWidgets.QPushButton, "x_left")
        self.button_right = self.findChild(QtWidgets.QPushButton, "x_right")
        
        self.zoom_factor = 1.25
        self.translate_factor = 0.1
        
    def connect_workers(self, plot):
        self.button_plus.pressed.connect(lambda: self.zoom_in(plot))
        self.button_minus.pressed.connect(lambda: self.zoom_out(plot))
        self.button_left.pressed.connect(lambda: self.shift_left(plot))
        self.button_right.pressed.connect(lambda: self.shift_right(plot))
        
    def zoom_in(self, plot):
        plot.getViewBox().scaleBy(x=1/self.zoom_factor)
    
    def zoom_out(self, plot):
        plot.getViewBox().scaleBy(x=self.zoom_factor)
       
    def compute_translation(self, plot):
        [[xmin, xmax], [ymin, ymax]] = plot.viewRange()
        return (xmax - xmin) * self.translate_factor
    
    def shift_left(self, plot):
        plot.getViewBox().translateBy(x=-self.compute_translation(plot))
        
    def shift_right(self, plot):
        plot.getViewBox().translateBy(x=self.compute_translation(plot))
        