'''
slm_window.py 
'''

import wx
from pubsub import pub

class SLMWindow(wx.Frame):
    '''
    This window needs to be a child of the main window so that it closes when main window closes
    '''
    def __init__(self, parent, pos, size):
        super().__init__(parent = parent, pos = pos, size = size, 
                         style = wx.NO_BORDER)
        pub.suscribe(self.update_listener, "update_slm")
                         
    def update_listener():
        pass
    
