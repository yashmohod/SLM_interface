'''
slm_window.py 
'''

import wx

class SLMWindow(wx.Frame):
    def __init__(parent, pos, size):
        super().__init__(parent = parent, pos = pos, size = size, 
                         style = wx.NO_BORDER)
