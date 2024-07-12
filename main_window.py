'''
main_window.py
'''

import wx

class MainWindow(wx.Frame):
    def __init__(self, pos, size, camera_object):
        super().__init__(parent = None, title = "SLM and Camera Control", 
                         pos = pos, size = size)
        self.camera_object = camera_object
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
    def on_close(self, event):
        self.camera_object._cleanup()
        self.Destroy()
