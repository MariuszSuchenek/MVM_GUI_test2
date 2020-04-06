from PyQt5.QtWidgets import QMessageBox

class MessageBox():
    '''
    Class that helps display a QT message box, with callbacks
    attached to each button.
    
    Example usage:
    
    ```
    from PyQt5.QtWidgets import QMessageBox

    callbacks = {QMessageBox.Retry: your_retry_callback_function,
                 QMessageBox.Abort: exit}
                 
    MessageBox().critical("Title", "Text", callbacks)
    ```
    '''
    def __init__(self):
        self.msg = QMessageBox()
        self.callbacks = {}
    
    def confirm(self, window_title, text, info_text=None, ok_callback=None, cancel_callback=None):
        '''
        Show a confirmation dialog with OK and Cancel buttons.
        
        You may specify callback functions for each button, or just check
        the return value of this function (OK => True, Cancel => False).
        '''
        self.callbacks = {QMessageBox.Ok: ok_callback,
                          QMessageBox.Cancel: cancel_callback}
        
        btn = self._show(title, text, info_text, QMessageBox.Question, QMessageBox.Cancel)
        return btn == QMessageBox.Ok
        
    def question(self, window_title, text, info_text, button_callbacks, default_button=None):
        '''
        Show a question dialog.
        
        button_callbacks is a dictionary where the keys are 
        QMessageBox.StandardButton, and the values are functions to call
        if that button is pressed (or None).
        
        default_button is the QMessageBox.StandardButton that is 
        highlighted by default.
        '''
        self.callbacks = button_callbacks
        self._show(title, text, QMessageBox.Question, default_button)
    
    def message(self, title, text, info_text=None, ok_callback=None):
        '''
        Show a message dialog with an OK button.
        
        You may specify a callback function that is called when the
        user presses the OK button.
        '''
        self.callbacks = {QMessageBox.Ok: ok_callback}
        self._show(title, text, info_text, QMessageBox.Information, QMessageBox.Ok)
    
    def warning(self, title, text, info_text=None, button_callbacks={QMessageBox.Ok: None}, default_button=None, detail=None):
        '''
        Show a warning dialog.
        
        button_callbacks is a dictionary where the keys are 
        QMessageBox.StandardButton, and the values are functions to call
        if that button is pressed (or None).
        
        default_button is the QMessageBox.StandardButton that is 
        highlighted by default.
        
        detail is optional text that will be displayed if the user
        clicks a "More details" button.
        '''
        self.callbacks = button_callbacks
        self._show(title, text, info_text, QMessageBox.Warning, default_button, detail)
    
    def critical(self, title, text, info_text=None, button_callbacks={QMessageBox.Ok: None}, default_button=None, detail=None):
        '''
        Show a critical warning dialog.
        
        button_callbacks is a dictionary where the keys are 
        QMessageBox.StandardButton, and the values are functions to call
        if that button is pressed (or None).
        
        default_button is the QMessageBox.StandardButton that is 
        highlighted by default.
        
        detail is optional text that will be displayed if the user
        clicks a "More details" button.
        '''
        self.callbacks = button_callbacks
        self._show(title, text, info_text, QMessageBox.Critical, default_button, detail)

    def _show(self, title, text, info_text, icon, default_btn=None, detail_text=""):
        '''
        Build the actual message box, based on the supplied
        arguments and the content of self.callbacks.
        '''
        self.msg.setIcon(icon)
        
        self.msg.setWindowTitle(title) 
        self.msg.setText(text) 
        self.msg.setInformativeText(info_text)
        self.msg.setDetailedText(detail_text)
        
        bitmask = 0
        for b in self.callbacks.keys():
            bitmask |= b
            
        self.msg.setStandardButtons(bitmask)
        
        if default_btn:
            self.msg.setDefaultButton(default_btn)
            
        btn = self.msg.exec()
        self._click_handler(btn)
        return btn
    
    def _click_handler(self, btn):
        callback = self.callbacks.get(btn, None)
        
        if callback:
            callback()
    
