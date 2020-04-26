#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore
from pyqtgraph import InfiniteLine, TextItem, SignalProxy, PlotDataItem
import numpy as np


class Cursor:
    '''
    Handles the cursor lines and cursor labels
    '''

    def __init__(self, plots):
        '''
        Constructor

        arguments:

        -plots: the plots
        '''

        self.plots = plots

        self.cursor_x = [None] * 3
        self.cursor_y = [None] * 3
        self.cursor_label = [None] * 3
        self.signal_proxy = [None] * 3
        self.plot_data_items = [None] * 3
        self._x = [None] * 3
        self._y = [None] * 3

        for num, plot in enumerate(plots):
            self.cursor_x[num] = InfiniteLine(angle=90, movable=False)
            self.cursor_y[num] = InfiniteLine(angle=0, movable=False)
            plot.addItem(self.cursor_x[num], ignoreBounds=True)
            plot.addItem(self.cursor_y[num], ignoreBounds=True)
            self.signal_proxy[num] = SignalProxy(plot.scene().sigMouseMoved,
                                                 rateLimit=60, slot=self.update_cursor)

            self.cursor_label[num] = TextItem(
                '', (255, 255, 255), anchor=(0, 0))
            self.cursor_label[num].setPos(-10.4, 10)
            plot.addItem(self.cursor_label[num])

            # Find the PlotDataItem displaying data
            for item in plot.getPlotItem().items:
                if isinstance(item, PlotDataItem):
                    self.plot_data_items[num] = item

        self.hide_cursors()

    def show_cursors(self):
        '''
        Shows all the cursor lines and labels
        on the 3 plots
        '''
        for c in self.cursor_x:
            c.setVisible(True)
        for c in self.cursor_y:
            c.setVisible(True)
        for c in self.cursor_label:
            c.setVisible(True)

    def hide_cursors(self):
        '''
        Hides all the cursor lines and labels
        on the 3 plots
        '''
        for c in self.cursor_x:
            c.setVisible(False)
        for c in self.cursor_y:
            c.setVisible(False)
        for c in self.cursor_label:
            c.setVisible(False)

    def draw_label(self):
        '''
        Draw the cursor label
        '''
        if self._y[0] is None:
            return
        for num, plot in enumerate(self.plots):
            self.cursor_label[num].setText("{:.2f}".format(self._y[num]))
            self.cursor_label[num].setPos(
                plot.getAxis('bottom').range[0], self._y[num])

    def update_cursor(self, evt):
        '''
        Update the cursor lines and labels.
        If this menu is not shown (we are not in Freeze)
        simply return and don't waste time.
        '''

        pos = evt[0]
        for num, plot in enumerate(self.plots):
            vb = plot.getViewBox()
            if plot.sceneBoundingRect().contains(pos):
                mousePoint = vb.mapSceneToView(pos)

                # Get the x and y data from the plot
                data_x = self.plot_data_items[num].xData
                data_y = self.plot_data_items[num].yData

                # Find the x index closest to where the mouse if pointing
                index = (np.abs(data_x - mousePoint.x())).argmin()

                if index > 0 and index < len(data_y):
                    self._x[num] = mousePoint.x()
                    self._y[num] = data_y[index]

                    # Set the cursor x and y positions
                    self.cursor_x[num].setPos(self._x[num])
                    self.cursor_y[num].setPos(self._y[num])

                    self.cursor_label[num].setText(
                        "{:.2f}".format(self._y[num]))
                    self.cursor_label[num].setPos(
                        plot.getAxis('bottom').range[0], self._y[num])


class FrozenPlotsBottomMenu(QtWidgets.QWidget):
    signal_hided = QtCore.pyqtSignal()
    signal_shown = QtCore.pyqtSignal()

    def __init__(self, *args):
        """
        Initialize the FrozenPlotsBottomMenu widget.

        Grabs child widgets.
        """
        super(FrozenPlotsBottomMenu, self).__init__(*args)
        uic.loadUi("frozenplots/frozenplots_bottom.ui", self)

        self.button_reset_zoom = self.findChild(
            QtWidgets.QPushButton, "button_reset_zoom")
        self.xzoom = self.findChild(QtWidgets.QWidget, "xzoom")

    def showEvent(self, event):
        super(FrozenPlotsBottomMenu, self).showEvent(event)
        self.signal_shown.emit()

    def hideEvent(self, event):
        super(FrozenPlotsBottomMenu, self).hideEvent(event)
        self.signal_hided.emit()

    def connect_workers(self, data_filler, plots, cursor):
        '''
        Connect workers for bottom "freeze" menu.
        The unfreeze button is handled by mainwindow.
        '''
        self.button_reset_zoom.pressed.connect(data_filler.reset_zoom)

        # X axes are linked, so only need to manipulate 1 plot
        self.xzoom.connect_workers(plots[0].getPlotItem(), cursor)

        self._cursor = cursor

        self.signal_hided.connect(lambda: self.toggle_cursor(False))
        self.signal_shown.connect(lambda: self.toggle_cursor(True))

    def toggle_cursor(self, on=True):
        if on:
            self._cursor.show_cursors()
        else:
            self._cursor.hide_cursors()

    def disconnect_workers(self):
        try:
            self.button_reset_zoom.pressed.disconnect()
        except Exception:
            pass
        self.xzoom.disconnect_workers()


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

    def connect_workers(self, plots, cursor):
        '''
        Connect Y zoom workers. There are 3 widgets, each controlling
        a separate plot.
        '''
        self.yzoom_top.connect_workers(plots[0].getPlotItem(), cursor)
        self.yzoom_mid.connect_workers(plots[1].getPlotItem(), cursor)
        self.yzoom_bot.connect_workers(plots[2].getPlotItem(), cursor)

        self._cursor = cursor

    def disconnect_workers(self):
        self.yzoom_top.disconnect_workers()
        self.yzoom_mid.disconnect_workers()
        self.yzoom_bot.disconnect_workers()


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

    def disconnect_workers(self):
        try:
            self.button_plus.pressed.disconnect()
        except Exception:
            pass
        try:
            self.button_minus.pressed.disconnect()
        except Exception:
            pass
        try:
            self.button_up.pressed.disconnect()
        except Exception:
            pass
        try:
            self.button_down.pressed.disconnect()
        except Exception:
            pass

    def connect_workers(self, plot, cursor):
        self.button_plus.pressed.connect(lambda: self.zoom_in(plot))
        self.button_minus.pressed.connect(lambda: self.zoom_out(plot))
        self.button_up.pressed.connect(lambda: self.shift_up(plot))
        self.button_down.pressed.connect(lambda: self.shift_down(plot))

        self._cursor = cursor

    def zoom_in(self, plot):
        plot.getViewBox().scaleBy(y=1 / self.zoom_factor)
        self._cursor.draw_label()

    def zoom_out(self, plot):
        plot.getViewBox().scaleBy(y=self.zoom_factor)
        self._cursor.draw_label()

    def compute_translation(self, plot):
        [[xmin, xmax], [ymin, ymax]] = plot.viewRange()
        return (ymax - ymin) * self.translate_factor

    def shift_up(self, plot):
        plot.getViewBox().translateBy(y=self.compute_translation(plot))
        self._cursor.draw_label()

    def shift_down(self, plot):
        plot.getViewBox().translateBy(y=-self.compute_translation(plot))
        self._cursor.draw_label()


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

    def connect_workers(self, plot, cursor):
        self.button_plus.pressed.connect(lambda: self.zoom_in(plot))
        self.button_minus.pressed.connect(lambda: self.zoom_out(plot))
        self.button_left.pressed.connect(lambda: self.shift_left(plot))
        self.button_right.pressed.connect(lambda: self.shift_right(plot))

        self._cursor = cursor

    def disconnect_workers(self):
        try:
            self.button_plus.pressed.disconnect()
        except Exception:
            pass
        try:
            self.button_minus.pressed.disconnect()
        except Exception:
            pass
        try:
            self.button_left.pressed.disconnect()
        except Exception:
            pass
        try:
            self.button_right.pressed.disconnect()
        except Exception:
            pass

    def zoom_in(self, plot):
        plot.getViewBox().scaleBy(x=1 / self.zoom_factor)
        self._cursor.draw_label()

    def zoom_out(self, plot):
        plot.getViewBox().scaleBy(x=self.zoom_factor)
        self._cursor.draw_label()

    def compute_translation(self, plot):
        [[xmin, xmax], [ymin, ymax]] = plot.viewRange()
        return (xmax - xmin) * self.translate_factor

    def shift_left(self, plot):
        plot.getViewBox().translateBy(x=-self.compute_translation(plot))
        self._cursor.draw_label()

    def shift_right(self, plot):
        plot.getViewBox().translateBy(x=self.compute_translation(plot))
        self._cursor.draw_label()
