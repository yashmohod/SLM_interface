'''
gui_subpanels.py
'''

import wx
import numpy as np
from utility import gray_ndarray_to_wxImage
from pubsub import pub

class CameraControlPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(wx.StaticText(self, label = 'Camera Live View:'),
                            flag = wx.ALL | wx.CENTER, border = 10)
        self.start_button = wx.Button(self, label = 'Start')
        self.stop_button = wx.Button(self, label = 'Stop')
        self.main_sizer.Add(self.start_button, proportion = 0.3, flag = wx.ALL | wx.CENTER,
                            border = 10)        
        self.main_sizer.Add(self.stop_button, proportion = 0.3, flag = wx.ALL | wx.CENTER,
                            border = 10)    
        self.SetSizer(self.main_sizer)
                            
        # event handlers
        self.Bind(wx.EVT_BUTTON, self.on_start, self.start_button)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
        # TODO: use evt_update_ui to disable the button once pressed
        
    def on_start(self, evt):
        pass 
        
    def on_stop(self, evt):
        pass 
        
                

class CameraPanel(wx.Panel):
    def __init__(self,parent):
        super().__init__(parent = parent)
        
        self.v_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.parent = parent
        
        self.camera_object = wx.GetApp().camera_object
        
        # blank image
        self.sensor_shape = self.camera_object.camera_sensor_shape
        self.sensor_aspect_ratio = self.sensor_shape[0]/self.sensor_shape[1]
        self.camera_display_scale_factor = 0.5
         
        img = wx.Image(*self.sensor_shape) #creates blank image
        scaled_img = self.scale_image_for_display(img)
        self.bitmap = scaled_img.ConvertToBitmap()
        self.curdis = wx.StaticBitmap(self, -1,self.bitmap)
        
        self.v_sizer.Add(self.curdis, 1, wx.ALIGN_CENTER)
        self.SetSizer(self.v_sizer)
        self.Bind(wx.EVT_SIZE, self.onResize)
        
        self.wasFullscreen = 0
        self.restoreSize = self.parent.Size[1]*0.50
        
        # Create a timer for acquiring video frames in live mode
        self.live_cam_timer = wx.Timer(self, id = 1)
        self.Bind(wx.EVT_TIMER, self.show_camera_snapshot, id = 1)
        # currently triggers at 20 frames/sec (every 50 ms)
        # TODO: make rate settable
        self.live_frame_time_ms = 50
        self.live_cam_timer.Start(self.live_frame_time_ms)
        
    
    def scale_image_for_display(self, image):
        return image.Scale(round(self.camera_display_scale_factor * self.sensor_aspect_ratio * self.parent.Size[1]), 
                                 round(self.parent.Size[1] * self.camera_display_scale_factor), 
                                 wx.IMAGE_QUALITY_HIGH)
        
    def onResize(self, event):
        # if self.curdis.Size[1] !=round(self.parent.Size[1]*0.55):
        self.Refresh()
        self.Layout()
        self.v_sizer.Clear()
        if self.parent.IsMaximized():
            # print(1)
            self.wasFullscreen = 1
            self.bitmap = scale_bitmap(self.bitmap,self.parent.Size[1]*0.50)
        else:
            print(0)
            if self.wasFullscreen:
                # print("here")
                self.bitmap = scale_bitmap(self.bitmap,self.restoreSize)
                self.wasFullscreen = 0
                
            else:
                self.bitmap = scale_bitmap(self.bitmap,self.parent.Size[1]*0.50)
        
        
        self.curdis.SetBitmap(self.bitmap)
        self.v_sizer.Add(self.curdis, 1, wx.ALIGN_CENTER)
        self.Refresh()
        self.Layout()
        

    def show_camera_snapshot(self, event):
        self.camera_object.camera.issue_software_trigger()
        frame = self.camera_object.camera.get_pending_frame_or_null()
        if frame is not None:
            image_buffer_copy = np.copy(frame.image_buffer)
            image = self.scale_image_for_display(gray_ndarray_to_wxImage(image_buffer_copy))
            self.curdis.SetBitmap(image.ConvertToBitmap())

class SLMControlPanel(wx.Panel):
    def  __init__(self, parent):
        super().__init__(parent = parent)
        
        # set Sizers
        #h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        local_v_sizer_1 = wx.BoxSizer(wx.VERTICAL)  
    
        default_config = wx.GetApp().slm_object.config
        
        self.unitsL = wx.StaticText(self, label = "Use any consistent length units.")
        self.input_px_label = wx.StaticText(self, label="SLM pixel size")
        self.input_px = wx.TextCtrl(self, value=str(default_config['slm_pixel_size']), size=(100,-1))
        self.input_focal_len_label = wx.StaticText(self, label="Focal length")
        self.input_focal_len = wx.TextCtrl(self, value=str(default_config['objective_focal_length']), size=(100,-1))
        self.input_wavelength_label = wx.StaticText(self, label="Wavelength")
        self.input_wavelength = wx.TextCtrl(self, value=str(default_config['wavelength']),size=(100,-1))

        self.multitrap_rb = wx.RadioBox(self, label = 'Multiple trap method',
                                        choices = ['Simultaneous', 'Time-shared'])
        self.update_timeL = wx.StaticText(self, label = 'Time share period [ms]',pos = (20, 710))
        self.update_timeVal = wx.TextCtrl(self, value = '50', size = (50, -1))
        
        local_v_sizer_1.Add(self.unitsL ,0,wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.input_px_label, 0, wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.input_px, 0, wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.input_focal_len_label, 0, wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.input_focal_len, 0, wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.input_wavelength_label, 0, wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.input_wavelength, 0, wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.multitrap_rb ,0,wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.update_timeL ,0,wx.ALIGN_CENTRE)
        local_v_sizer_1.Add(self.update_timeVal ,0,wx.ALIGN_CENTRE)
        
        self.SetSizer(local_v_sizer_1) 
    
    
class SLMPointsPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.v_sizer.Add(wx.StaticText(self, label = 'Trap Points:'),
                                       wx.SizerFlags().CenterHorizontal())
        self.points = wx.TextCtrl(self, size = (200,250), style = wx.TE_MULTILINE)
        self.v_sizer.Add(self.points,0,wx.ALIGN_CENTRE)
        update_slm_button = wx.Button(self,id = wx.ID_ANY, size= (200,40),label= "Update SLM")
        self.v_sizer.Add(update_slm_button, 0, wx.ALIGN_CENTRE)
        update_slm_button.Bind(wx.EVT_BUTTON, wx.GetApp().slm_object.update_slm)
        self.SetSizer(self.v_sizer)


class SLMMonitorPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.parent = parent
        self.scaling_ratio = 0.3
        
        # Scaling strategy: get size of parent frame and size relative to it
                
        native_slm_size = wx.GetApp().slm_display.GetGeometry()[2:4]
        self.aspect_ratio = native_slm_size[0]/native_slm_size[1]
        self.curdis = wx.StaticBitmap(self, -1, 
                                      self.scale_image_for_display(wx.Image(*native_slm_size)).ConvertToBitmap())
        self.v_sizer.Add(self.curdis, 1, wx.ALIGN_CENTER)
        self.SetSizer(self.v_sizer)
                
        pub.subscribe(self.update_panel, 'update_slm')
                
                
    def scale_image_for_display(self, image):
        return image.Scale(round(self.parent.Size[1] * self.scaling_ratio * self.aspect_ratio), 
                           round(self.parent.Size[1] * self.scaling_ratio), wx.IMAGE_QUALITY_HIGH)
                    
    def update_panel(self, image):  
        self.curdis.SetBitmap(self.scale_image_for_display(image).ConvertToBitmap())

        
    
