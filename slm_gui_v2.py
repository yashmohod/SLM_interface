import wx
import numpy as np
from PIL import Image as im
import os
import glob
import time


from thorcam_container import CameraContainer
from slm_container import SLMContainer 
from main_window import MainWindow
from slm_window import SLMWindow 

class MainApp(wx.App):
    '''
    MainApp contains camera object and two Frames, one for main monitor,
    one for SLM
    '''
    def __init__(self):
        super().__init__(redirect = False, clearSigInt = True)
        self.main_window_scale_factor = 0.7
        self.slm_object =  SLMContainer()
        self.camera_object = CameraContainer()
        self.identify_displays()
        self.main_frame = self.init_main_window()
        self.main_frame.Show()
        
        self.slm_frame = self.init_slm_window()
        self.slm_frame.Show()
        
        
    def identify_displays(self):
        '''
        Get geometry of all connected displays.
        Requires that at least two displays be connected.
        Look for one that matches the known SLM geometry.
        Edge case not handled: main monitor and SLM have same geometry.
        '''
        display_count = wx.Display.GetCount()
        if display_count < 2:
            raise ValueError("At least 2 displays must be connected.")
        display_indices = [*range(display_count)]
        geometries = [wx.Display(i).GetGeometry() for i in display_indices]
        
        slm_matches = []
        for i in display_indices:
            if geometries[i][2:4] == self.slm_object.slm_display_shape:
                slm_matches.append(i)
        
        if len(slm_matches) == 0:
            raise ValueError("No connected display has geometry matching slm_display_shape entry in optical_train_config.yaml")
        elif len(slm_matches) > 1:
            raise ValueError("More than one connected display has geometry matching slm_display_shape entry in optical_train_config.yaml")
        else:
            self.slm_display_index = slm_matches[0]
            self.slm_display = wx.Display(self.slm_display_index)
            
        # Now find the largest remaining display and use it as the main display 
        display_indices.remove(slm_matches[0])
        display_areas = np.array([geometries[i][2] * geometries[i][3] 
                                  for i in display_indices])
        self.main_display_index = display_indices[display_areas.argmax()] 
        self.main_display = wx.Display(self.main_display_index)
     
        
    def init_main_window(self):
        # Calculate appropriate size to center on main monitor 
        main_display_geo = self.main_display.GetGeometry()
        main_window_pos = (np.array(main_display_geo[2:4]) * 0.5 *
                           (1 - self.main_window_scale_factor)).round().astype('int')
        main_window_size = (self.main_window_scale_factor * 
                            np.array(main_display_geo[2:4])).round().astype('int')
        return MainWindow(pos = main_window_pos, size = main_window_size)
        
        
    def init_slm_window(self):
        slm_display_geo = self.slm_display.GetGeometry()
        return SLMWindow(parent = self.main_frame, pos = slm_display_geo[0:2],
                         size = slm_display_geo[2:4])
        
        

if __name__ == "__main__":
    app = MainApp()
    app.MainLoop()
