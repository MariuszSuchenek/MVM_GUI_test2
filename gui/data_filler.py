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

    In "frozen" mode, we keep adding new data points to _data,
    but don't update the displayed graph. When we unfreeze, we
    then see the full recent data.
    '''

    def __init__(self, config):
        self._qtgraphs = {}
        self._plots = {}
        self._monitors = {}
        self._data = {}
        self._colors = {}
        self._default_ranges = {}
        self._config = config
        self._n_samples = self._config['nsamples']
        self._sampling = self._config['sampling_interval']
        self._time_window = self._n_samples * self._sampling # seconds
        self._xdata = np.linspace(-self._time_window, 0, self._n_samples)
        self._frozen = False
        self._first_plot = None
        self._looping = self._config['use_looping_plots']
        self._looping_data_idx = {}
        self._looping_lines = {}
        return

    def connect_plot(self, plotname, plot):
        '''
        Connects a plot to this class by
        storing it in a dictionary
        '''
        plot_config = self._config['plots'][plotname]
        name = plot_config['observable']

        # Link X axes if we've already seen a plot
        if self._first_plot:
            plot.setXLink(self._first_plot)
        else:
            self._first_plot = plot

        self._qtgraphs[name] = plot
        self._plots[name] = plot.plot()
        self._data[name] = np.linspace(0, 0, self._n_samples)
        self._plots[name].setData(self._xdata, self._data[name])
        self._colors[name] = plot_config['color'] 
        self._looping_data_idx[name] = 0

        # Set the Y axis
        y_axis_label = plot_config['name'] 
        y_axis_label += ' '
        y_axis_label += plot_config['units'] 
        plot.setLabel(axis='left', text=y_axis_label)

        # Set the X axis
        if self._config['show_x_axis_labels'] and 'bot' in plot_config['name'] and not self._looping:
            self.add_x_axis_label(plot)

        # Remove x ticks, if selected
        if self._looping or not self._config['show_x_axis_ticks']:
            plot.getAxis('bottom').setTicks([])
            plot.getAxis('bottom').setStyle(tickTextOffset=0, tickTextHeight=0)

        # Customize the axis color
        color = self.parse_color(self._config['axis_line_color'])
        plot.getAxis('bottom').setPen(pg.mkPen(color, width=self._config['axis_line_width']))
        plot.getAxis('left').setPen(pg.mkPen(color, width=self._config['axis_line_width']))

        if self._looping:
            self.add_looping_lines(name, plot)

        # Fix the x axis range
        self.set_default_x_range(name)

        # Fix the y axis range
        value_min = plot_config['min']
        value_max = plot_config['max']
        ymin = value_min - (value_max-value_min)*0.1
        ymax = value_max + (value_max-value_min)*0.1
        self._default_ranges[name] = [ymin, ymax]
        self.set_default_y_range(name)

        # Remove mouse interaction with plots
        plot.setMouseEnabled(x=False, y=False)
        plot.setMenuEnabled(False)

        print('NORMAL: Connected plot', plot_config['name'], 'with variable', name)

    def set_default_y_range(self, name):
        '''
        Set the Y axis range of the plot to the defaults
        specified in the config file.
        '''
        self._qtgraphs[name].setYRange(self._default_ranges[name][0], self._default_ranges[name][1])

    def set_default_x_range(self, name):
        '''
        Set the X axis range of the plot to the defaults
        specified in the config file.
        '''
        self._qtgraphs[name].setXRange(-self._n_samples * self._sampling, 0)

    def add_x_axis_label(self, plot):
        '''
        Adds the x axis label 'Time [s]' in the form
        of a QGraphicsTextItem. This is done because it
        is hard to customize the PyQtGraph label.
        '''
        self._x_label = QtGui.QGraphicsTextItem()
        self._x_label.setVisible(True)
        self._x_label.setHtml('<p style="color: %s">Time [s]:</p>' % self._config["axis_line_color"])

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

    def add_looping_lines(self, name, plot):
        '''
        Add line corresponding to where the
        data is being updated when in "looping" mode.
        '''

        self._looping_lines[name] = pg.InfiniteLine(pos=0,
                                         angle=90,
                                         movable=False,
                                         pen=pg.mkPen(cosmetic=False,
                                                      width=self._time_window / 25,
                                                      color='k',
                                                      style=QtCore.Qt.SolidLine))

        plot.addItem(self._looping_lines[name])

    def connect_monitor(self, monitor):
        '''
        Connect a monitor to this class by
        storing it in a dictionary
        '''
        name = monitor.observable 
        self._monitors[name] = monitor

        print('NORMAL: Connected monitor', monitor.configname , 'with variable', name)

    def add_data_point(self, name, data_point):
        '''
        Adds a data point to the plot with
        name 'name'
        '''
        if name not in self._plots:
            # print("\033[91mERROR: Can't set data for plot with name %s.\033[0m" % name)
            return False

        if self._looping:
            # Looping plots - update next value
            self._data[name][self._looping_data_idx[name]] = data_point

            self._looping_data_idx[name] += 1

            if self._looping_data_idx[name] == self._n_samples:
                self._looping_data_idx[name] = 0
        else:
            # Scrolling plots - shift data 1 sample left
            self._data[name][:-1] = self._data[name][1:]

            # add the last data point
            self._data[name][-1] = data_point

        self.update_plot(name)
        self.update_monitor(name)

    def update_plot(self, name):
        '''
        Send new data from self._data to the actual pyqtgraph plot.
        '''

        if not self._frozen:
            # Update the displayed plot with current data.
            # In frozen mode, we don't update the display.
            color = self._colors[name]
            color = color.replace('rgb', '')
            color = literal_eval(color)
            self._plots[name].setData(self._xdata,
                                      self._data[name],
                                      pen=pg.mkPen(color, width=self._config['line_width']))

            if self._looping:
                x_val = self._xdata[self._looping_data_idx[name]] - self._sampling * 0.1
                self._looping_lines[name].setValue(x_val)



    def freeze(self):
        '''
        Enter "frozen" mode, where plots are not updated, and mouse/zoom
        interaction is enabled.
        '''
        self._frozen = True

        for plot in self._qtgraphs.values():
            plot.setMouseEnabled(x=True, y=True)

    def unfreeze(self):
        '''
        Leave "frozen" mode, resetting the zoom and showing self-updating
        plots.
        '''
        self._frozen = False

        for name in self._plots.keys():
            self.update_plot(name)

        for plot in self._qtgraphs.values():
            plot.setMouseEnabled(x=False, y=False)

        self.reset_zoom()

    def reset_zoom(self):
        '''
        Revert to normal zoom range for each plot.
        autoRange() used to set X range, then
        custom values used for Y range.
        '''
        for name, plot in self._qtgraphs.items():
            self.set_default_x_range(name)
            self.set_default_y_range(name)

    def update_monitor(self, name):
        '''
        Updates the values in a monitor,
        if a monitor exists with this name
        '''

        if name in self._monitors:
            last_data_idx = self._looping_data_idx[name] - 1 if self._looping else -1
            self._monitors[name].update_value(self._data[name][last_data_idx])
        else:
            return

    def parse_color(self, rgb_string):

        color = rgb_string.replace('rgb', '')
        return literal_eval(color)


