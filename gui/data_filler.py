from PyQt5 import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from ast import literal_eval # to convert a string to list


class CustomAxis(pg.AxisItem):
    '''
    Apparently you cannot change the position of the label
    in pyqtgraph, as it is hardcoded :(
    This class overrides the AxisItem so the `nudge` can
    be set externally. `nudge` controls the offset between 
    the label and the axis.
    '''
    @property
    def nudge(self):
        if not hasattr(self, "_nudge"):
            self._nudge = 5
        return self._nudge

    @nudge.setter
    def nudge(self, nudge):
        self._nudge = nudge
        s = self.size()
        # call resizeEvent indirectly
        self.resize(s + QtCore.QSizeF(1, 1))
        self.resize(s)

    def resizeEvent(self, ev=None):
        # s = self.size()

        ## Set the position of the label
        nudge = self.nudge
        br = self.label.boundingRect()
        p = QtCore.QPointF(0, 0)
        if self.orientation == "left":
            p.setY(int(self.size().height() / 2 + br.width() / 2))
            p.setX(-nudge)
        elif self.orientation == "right":
            p.setY(int(self.size().height() / 2 + br.width() / 2))
            p.setX(int(self.size().width() - br.height() + nudge))
        elif self.orientation == "top":
            p.setY(-nudge)
            p.setX(int(self.size().width() / 2.0 - br.width() / 2.0))
        elif self.orientation == "bottom":
            p.setX(int(self.size().width() / 2.0 - br.width() / 2.0))
            p.setY(int(self.size().height() - br.height() + nudge))
        self.label.setPos(p)
        self.picture = None

class DataFiller():
    '''
    This class fills the data for all the
    displayed plots on the screen, and 
    updates the plots accordingly.
    It also passes data to the monitors.
    '''

    def __init__(self, config):
        self._plots = {}
        self._monitors = {}
        self._data = {}
        self._colors = {}
        self._config = config
        self._n_smaples = self._config['nsamples']
        self._sampling = self._config['sampling_interval']
        self._time_window = self._n_smaples * self._sampling # seconds
        self._xdata = np.linspace(-self._time_window, 0, self._n_smaples)
        return

    def connect_plot(self, monitor_name, plot):
        '''
        Connects a plot to this class by
        storing it in a dictionary
        '''
        name = self._config[monitor_name]['plot_var']

        self._plots[name] = plot.plot()
        self._data[name] = np.linspace(0, 0, self._n_smaples)
        self._plots[name].setData(self._xdata, self._data[name])
        self._colors[name] = self._config[monitor_name]['color']

        # Set the Y axis
        y_axis_label = self._config[monitor_name]['name']
        y_axis_label += ' ['
        y_axis_label += self._config['var_units'].get(name, '')
        y_axis_label += ']'
        plot.setLabel(axis='left', text=y_axis_label)

        # Set the X axis
        if self._config['show_x_axis_labels'] and 'bot' in monitor_name:
            self.add_x_axis_label(plot)

        # Remove x ticks, if selected
        if not self._config['show_x_axis_ticks']:
            plot.getAxis('bottom').setTicks([])
            plot.getAxis('bottom').setStyle(tickTextOffset=0, tickTextHeight=0)

        # Customize the axis color
        color = self.parse_color(self._config['axis_line_color'])
        plot.getAxis('bottom').setPen(pg.mkPen(color, width=self._config['axis_line_width']))
        plot.getAxis('left').setPen(pg.mkPen(color, width=self._config['axis_line_width']))

        # Remove mouse interaction with plots
        plot.setMouseEnabled(x=False, y=False)
        plot.setMenuEnabled(False)

        print('NORMAL: Connected plot', monitor_name, 'with variable', name)

    def add_x_axis_label(self, plot):
        '''
        Adds the x axis label 'Time [s]' in the form
        of a QGraphicsTextItem. This is done because it 
        is hard to customize the PyQtGraph label.
        '''
        self._x_label = QtGui.QGraphicsTextItem()
        self._x_label.setVisible(True)
        self._x_label.setHtml(f'<p style="color: {self._config["axis_line_color"]}">Time [s]:</p>')  

        # Find the position of the label
        br = self._x_label.boundingRect()
        p = QtCore.QPointF(0, 0)
        axis = plot.getAxis('bottom')
        x = plot.size().width()/2. - br.width()/2.
        y = plot.size().height() - br.height() 
        p.setX(0) # Leave it on the left, so it doesn't cover labels.
        p.setY(y)
        self._x_label.setPos(p)
        plot.getAxis('bottom').scene().addItem(self._x_label)


    def connect_monitor(self, monitor_name, monitor):
        '''
        Connect a monitor to this class by
        storing it in a dictionary
        '''
        name = self._config[monitor_name]['plot_var']
        self._monitors[name] = monitor

        print('NORMAL: Connected monitor', monitor_name, 'with variable', name)

    def add_data_point(self, name, data_point):
        '''
        Adds a data point to the plot with
        name 'name'
        '''
        if name not in self._plots:
            # print(f"\033[91mERROR: Can't set data for plot with name {name}.\033[0m")
            return False

        # shift data 1 sample left
        self._data[name][:-1] = self._data[name][1:]

        # add the last data point
        self._data[name][-1] = data_point

        # set the data to the plot to show
        color = self._colors[name]
        color = color.replace('rgb', '')
        color = literal_eval(color)
        self._plots[name].setData(self._xdata, 
                                  self._data[name],
                                  pen=pg.mkPen(color, width=self._config['line_width']))

        self.update_monitor(name)

        return True

    def update_monitor(self, name):
        '''
        Updates the values in a monitor,
        if a monitor exists with this name
        '''

        if name in self._monitors:
            # Mean
            self._monitors[name].label_statvalues[0].setText("%.2f" % np.mean(self._data[name]))
            # Max
            self._monitors[name].label_statvalues[1].setText("%.2f" % np.max(self._data[name]))
            # Value
            self._monitors[name].update(self._data[name][-1])
        else:
            return

    def parse_color(self, rgb_string):

        color = rgb_string.replace('rgb', '')
        return literal_eval(color)


