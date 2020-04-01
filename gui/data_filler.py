from PyQt5 import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from ast import literal_eval # to convert a string to list

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

        # Show the alarm thresholds on plots
        if self._config['show_safe_ranges_on_graphs']:
            self.show_safe_ranges(monitor_name, plot)

        # Fix the y axis range
        value_min = self._config[monitor_name]['min']
        value_max = self._config[monitor_name]['max']
        ymin = value_min - (value_max-value_min)*0.1
        ymax = value_max + (value_max-value_min)*0.1
        plot.setYRange(ymin, ymax)

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

    def show_safe_ranges(self, monitor_name, plot):
        '''
        Adds to lines corresponding to where the 
        alarm values are
        '''

        # Min Line
        self._line_min = pg.InfiniteLine(pos=self._config[monitor_name]['min'], 
                                         angle=0, 
                                         movable=False,
                                         pen=pg.mkPen(cosmetic=False, 
                                                      width=0, 
                                                      color='r',
                                                      style=QtCore.Qt.DotLine))

        # Max Line
        self._line_max = pg.InfiniteLine(pos=self._config[monitor_name]['max'], 
                                         angle=0, 
                                         movable=False,
                                         pen=pg.mkPen(cosmetic=False, 
                                                      width=0, 
                                                      color='r',
                                                      style=QtCore.Qt.DotLine))
        plot.addItem(self._line_min)
        plot.addItem(self._line_max)


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


