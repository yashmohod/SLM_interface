'''
slm_window.py 
'''

import wx
from utility import gray_ndarray_to_wxImage
from pubsub import pub

class SLMWindow(wx.Frame):
    '''
    This window needs to be a child of the main window so that it closes when main window closes
    '''
    def __init__(self, parent, pos, size):
        super().__init__(parent = parent, pos = pos, size = size, 
                         style = wx.NO_BORDER)
        self.size = size 
        self.current_display = wx.StaticBitmap(parent = self, id = wx.ID_ANY,
                                               bitmap = wx.EmptyImage(*self.size).ConvertToBitmap(),
                                               pos = (0,0))
        pub.subscribe(self.update_listener, "update_slm")

                         
    def update_listener(self, image):
        '''
        Pass in a wx.Image object.
        '''
        self.current_display.SetBitmap(image.ConvertToBitmap())
    
