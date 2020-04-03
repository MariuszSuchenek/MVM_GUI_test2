from data_filler import DataFiller

class FrozenDataFiller(DataFiller):
    '''
    This class is like a regular DataFiller, but instead of updating
    the waveforms point-by-point as new data arrives from the ESP32,
    we set the full waveform content directly.
    
    In practice, when the user clicks a "freeze" button, we take the
    current content of the live plots, and copy them to these "frozen"
    plots.
    '''
    def __init__(self, config):
        DataFiller.__init__(self, config)
        
        # Keep track of the first plot we add, so we can
        # link all others to have the same X axis as it.
        self._first_plot = None
        self._debug = True
        
    def connect_plot(self, monitor_name, plot):
        '''
        Connect a plot to this class. Most of the work
        is done by the base DataFiller class, there are
        just a few tweaks for the frozen plots.
        '''
        DataFiller.connect_plot(self, monitor_name, plot)
        
        # Enable mouse interaction with plots
        plot.setMouseEnabled(x=True, y=True)
        
        # Link axes
        if self._first_plot:
            plot.setXLink(self._first_plot)
        else:
            self._first_plot = plot
    
    def add_data_point(self, name, data_point):
        '''
        add_data_point() is defined in the DataFiller base class.
        Add a sanity check here to make sure we aren't accidentally
        trying to add a data point to a frozen plot.
        '''
        raise RuntimeError("Doesn't make sense to add a data point to a frozen plot!")
    
    def set_data(self, name, data):
        '''
        This function is unique to FrozenDataFiller.
        Take the numpy array "data", and set it as the content
        of the plot called "name". Then update the plot to display
        the new data.
        '''
        if name not in self._data:
            if self._debug:
                print("%s not in frozen plots" % name)
                
            return False

        # Store the current data
        self._data[name] = data

        # Update the plot
        return self.update_plot(name)

        
    