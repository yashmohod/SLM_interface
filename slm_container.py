'''
slm_container.py 
'''

import os
import numpy as np
import yaml
import pyhot
import wx
from pubsub import pub
from utility import gray_ndarray_to_wxImage

class SLMContainer(object):
    def __init__(self):
        gui_dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        config_fname = os.path.abspath(gui_dir_abs_path) + os.sep + 'optical_train_config.yaml'
        with open(config_fname, mode = 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.wavelength = self.config['wavelength']
        self.slm_pixel_size = self.config['slm_pixel_size']
        self.slm_display_shape = tuple(self.config['slm_display_shape'])
        self.objective_focal_length = self.config['objective_focal_length']
        
        self.slm_engine = pyhot.SLM(self.slm_display_shape[1], self.slm_display_shape[0],
                                    self.wavelength, self.slm_pixel_size, 
                                    self.objective_focal_length)
                                    
    def update_slm(self, evt):
        '''
        Button in main window binds here.
        '''
        # get points from main window control panel
        points = self._unpack_points_from_textctrl(wx.GetApp().main_frame.controlPanel.points.GetValue())
        
        self.update_slm_pts(points = points)
        
        
    def update_slm_pts(self, points):
        '''
        can also be called by other methods
        ''' 
        
        # check main slm_window
        current_wavelength = float(wx.GetApp().main_frame.controlPanel.input_wavelength.GetValue())
        current_pixel_size = float(wx.GetApp().main_frame.controlPanel.input_px.GetValue())
        current_focal_length = float(wx.GetApp().main_frame.controlPanel.input_focal_len.GetValue())
        
        if ((self.wavelength == current_wavelength) and (self.slm_pixel_size == current_pixel_size)
            and (self.objective_focal_length == current_focal_length)):
            # no need to update the engine 
            pass 
        else: # update 
            self.wavelength = current_wavelength
            self.slm_pixel_size = current_pixel_size
            self.objective_focal_length = current_focal_length
            self.slm_engine = pyhot.SLM(self.slm_display_shape[1], self.slm_display_shape[0],
                                    self.wavelength, self.slm_pixel_size, 
                                    self.objective_focal_length)
        
        if wx.GetApp().main_frame.controlPanel.multitrap_rb.GetSelection() == 0: # Simultaneous display
            holo_img = gray_ndarray_to_wxImage(self.slm_engine.calc_holo(points))
            pub.sendMessage("update_slm", image = holo_img)
        else: # time shared
            raise NotImplementedError

    
        
    def _unpack_points_from_textctrl(self, points):
        points = points.split("\n")
        points_arr=[]
        for pt in points:
            if pt != "":
                if str(pt).count("(") == 1 and str(pt).count(")") == 1 and str(pt).count(",") == 2:
                    pt = str(pt).replace("(","").replace(")","").split(",")
                    ptsarr.append([float(pt[0]),float(pt[1]),float(pt[2])])
        return np.array(points_arr)
        
    
                                    
    # Implement wxTimer 
    # Sends update messages
        
