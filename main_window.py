'''
main_window.py
'''

import wx
import numpy as np 
from utility import gray_ndarray_to_wxImage
from pubsub import pub

# TODO: refactor scale_image_for_display

class MainWindow(wx.Frame):
    def __init__(self, pos, size):
        super().__init__(parent = None, title = "SLM and Camera Control", 
                         pos = pos, size = size)
        self.camera_object = wx.GetApp().camera_object
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetMinSize(size)
        self.fgs = wx.FlexGridSizer(2, 3, 0, 0) # 2 rows, 3 cols
        #self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.camera_control_panel = CameraControlPanel(parent = self)
        self.camera_panel = CameraPanel(parent=self)
        self.slm_control_panel = SLMControlPanel(parent = self)
        self.slm_points_panel = SLMPointsPanel(parent = self)
        self.slm_monitor_panel = SLMMonitorPanel(parent = self)
        #self.v_sizer.Add(self.cameraPanel, 1, wx.EXPAND)
        self.fgs.AddMany([(self.camera_control_panel, 1, wx.EXPAND),
                          (self.camera_panel, 1, wx.EXPAND),
                          ((50,50)), #spacer, not used
                          (self.slm_control_panel, 1, wx.EXPAND),
                          (self.slm_points_panel, 1, wx.EXPAND),
                          (self.slm_monitor_panel, 1, wx.EXPAND),])
        self.SetSizer(self.fgs)
        
        self.InitUI()
        
        
    def OnClose(self, event):
        #self.camera_object._cleanup()
        self.Destroy()
        
    def InitUI(self):
        self.CreateMenuBar()
        
        #self.controlPanel = ControlPanel(parent=self)
        #self.v_sizer.Add(self.controlPanel, 1, wx.EXPAND)
        
    

        
        

    def CreateMenuBar(self):
        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        
        saveSubMenu = wx.Menu()
        
        saveSubMenu.Append(201, 'Save sequence of images', 'Save sequence of images')
        fileMenu.AppendSubMenu(saveSubMenu, 'Acquire')
    
        menubar.Append(fileMenu,'&File')
        
        settingsMenu = wx.Menu()
        exposureMenu = wx.Menu()
        exposureMenu.Append(101, 'Set Exposure Time', 'Set exposure time')
        settingsMenu.AppendSubMenu(exposureMenu, 'Exposure Time')
        menubar.Append(settingsMenu, '&Settings')

        self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnSetExposure, id=101)
        self.Bind(wx.EVT_MENU, self.OnSaveSequence, id = 201)
        self.SetMenuBar(menubar)
    
    
    def OnSaveSequence(self,e):
        dlg = wx.DirDialog(self, "Choose file directory to save images",style = wx.DD_DEFAULT_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
          path = dlg.GetPath()
          dlg.Destroy()
          
          
          dialog = wx.Dialog(self, title = "Save sequence of images")
          
          wx.StaticText(dialog,label = "Folder Path", pos = (10,10))
          path_text = wx.TextCtrl(dialog, value = path, pos = (120,10), size = (100,-1), style =wx.TE_READONLY)
          
          wx.StaticText(dialog, label = "File name",pos = (10,40))
          filename_text = wx.TextCtrl(dialog, pos = (120,40), size = (200,-1))
          
          wx.StaticText(dialog, label = "Number of images", pos = (10,70))
          num_images = wx.SpinCtrl(dialog, value = '1', pos = (120,70), size = (80, -1), min = 1, max = 2000)
          
          
          wx.StaticText(dialog, label = "Frame rate", pos = (10,100))
          frame_rate = wx.TextCtrl(dialog, pos = (120,100))
          
          btn_ok = wx.Button(dialog, wx.ID_OK, "Start Acquisition", pos = (120, 150))
          btn_cancel = wx.Button(dialog, wx.ID_CANCEL, "Cancel", pos = (250,150))
          
          
          btn_ok.Bind(wx.EVT_BUTTON, lambda event: self.OnStartAcquisition(event, path_text.GetValue(), filename_text.GetValue(), num_images.GetValue(), frame_rate.GetValue()))
          
          
          
          if dialog.ShowModal() ==wx.ID_OK:
       
            filename = filename_text.GetValue()
            num_images = num_images.GetValue()
        
        
      
    def OnStartAcquisition(self,e,path,filename,num_images,frame_rate):
        pass
        # self.camera_object.camera.disarm()
        # self.camera_object.camera.frames_per_trigger_zero_for_unlimited = num_images
        # self.camera_object.camera.frame_rate_control_value = float(frame_rate) 
        # self.camera_object.camera.arm(num_images+1)
        # self.camera_object.camera.issue_software_trigger()
        
        # for i in range(num_images):
        #   frame = self.camera_object.camera.get_pending_frame_or_null()
        #   if frame is not None:
         
        #     image_data = np.copy(frame.image_buffer)
        #     pil_image = im.fromarray(image_data)
          
        #     image_filename = filename + str(i).zfill(3) + '.tif'
        #     image_filepath=os.path.join(path, image_filename)
          
        #     pil_image.save(image_filepath)
        #     print(f"Saved image {i+1}/{num_images} to {image_filepath}")
        #   else:
        #     print("timeout reached")
        #     break
        
        # self.camera_object.camera.disarm()
        # self.camera_object.camera.frames_per_trigger_zero_for_unlimited = 1
        # self.camera_object.camera.arm(2)
          
        
          
    def OnQuit(self, e):
        self.Close()

    def OnSetExposure(self, e):
        current_exposure_time = self.camera_object.camera.exposure_time_us / 1000
        exposure_dialog = wx.TextEntryDialog(self, f'Enter exposure time in ms (currently at {current_exposure_time}ms): ','Set Exposure Time')
        if exposure_dialog.ShowModal() == wx.ID_OK  and exposure_dialog.GetValue().isdigit():
            exposure_time = int(exposure_dialog.GetValue()) 
            self.camera_object.camera.exposure_time_us = exposure_time * 1000
            
            #set exposure time to the value we get
            print(f'Exposure time set to {exposure_time} ms')
            
        else:
            print("Use a non-zero integer") #wx.MessageBox("Invalid input. Please enter a non-zero integer.", "Error", wx.OK | wx.ICON_ERROR)
            
        exposure_dialog.Destroy()
    

class CameraControlPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(wx.StaticText(self, label = 'Camera Live View:'),
                            wx.SizerFlags().CenterHorizontal())
        self.start_button = wx.Button(self, label = 'Start')
        self.stop_button = wx.Button(self, label = 'Stop')
        self.main_sizer.Add(self.start_button, proportion = 0.3, flag = wx.ALL | wx.CENTER,
                            border = 5)        
        self.main_sizer.Add(self.stop_button, proportion = 0.3, flag = wx.ALL | wx.CENTER,
                            border = 5)    
                            
        # event handlers
        self.Bind(wx.EVT_BUTTON, self.on_start, self.start_button)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
        # TODO: use evt_update_ui to disable the button once pressed
        
    def on_start(self, evt):
        pass 
        
    def on_stop(self, evt):
        pass 
        
                


def scale_bitmap(bitmap,ratio):
    # image = wx.ImageFromBitmap(bitmap)
    image =  bitmap.ConvertToImage()
    nujm = ratio
    image = image.Scale(round(nujm*1.6), round(nujm*1), wx.IMAGE_QUALITY_HIGH)
    # image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.Bitmap(image)
    return result        


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
        self.v_sizer.Add(update_slm_button)
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

        

class ControlPanel(wx.Panel):
    def __init__(self,parent):
        super().__init__(parent = parent )
        
        self.slmpanel = SLMPanel(parent=self)
        self.onInint()

    
    def onInint(self):
        # set Sizers
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        local_v_sizer_1 = wx.BoxSizer(wx.VERTICAL)
        local_v_sizer_2 = wx.BoxSizer(wx.VERTICAL)
        local_v_sizer_3 = wx.BoxSizer(wx.VERTICAL)
        h_sizer.Add(local_v_sizer_1,1,wx.EXPAND)
        h_sizer.Add(local_v_sizer_2,1,wx.EXPAND)
        h_sizer.Add(local_v_sizer_3,2,wx.EXPAND)  
    
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
        
        
        self.pointL = wx.StaticText(self, label="Points")
        self.points = wx.TextCtrl(self,size = (200,250),style = wx.TE_MULTILINE)
        local_v_sizer_2.Add(self.pointL,0,wx.ALIGN_CENTRE)
        local_v_sizer_2.Add(self.points,0,wx.ALIGN_CENTRE)
    
        
        update_slm_button = wx.Button(self,id = wx.ID_ANY, size= (200,40),label= "Update SLM")
        update_slm_button.Bind(wx.EVT_BUTTON, wx.GetApp().slm_object.update_slm)
        
        self.slmpanelL = wx.StaticText(self, label = "SLM Display")
        local_v_sizer_3.Add(self.slmpanelL,0,wx.ALIGN_CENTER)
        local_v_sizer_3.Add(self.slmpanel,0,wx.ALIGN_CENTER)
        local_v_sizer_3.Add(update_slm_button,0,wx.ALIGN_CENTER)
        self.SetSizer(h_sizer)        
    
    

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
            

class SLMPanel(wx.Panel):
    def __init__(self,parent):
        super().__init__(parent = parent)
        
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.parent = parent
        self.scaling_ratio = 8

        # Scaling strategy: get size of camera panel and size relative to it
        
        native_slm_size = wx.GetApp().slm_display.GetGeometry()[2:4]
        self.aspect_ratio = native_slm_size[0]/native_slm_size[1]
        # eventually get rid of self.bitmap
        self.bitmap = self.scale_image_for_display(wx.Image(*native_slm_size)).ConvertToBitmap()
        self.curdis = wx.StaticBitmap(self, -1, self.bitmap)
        self.v_sizer.Add(self.curdis, 1, wx.ALIGN_CENTER)
        self.SetSizer(self.v_sizer)

        self.Bind(wx.EVT_SIZE, self.onResize)
        
        pub.subscribe(self.update_panel, 'update_slm')
        
        
    def scale_image_for_display(self, image):
        return image.Scale(round(self.parent.Size[1] * self.scaling_ratio * self.aspect_ratio), 
                           round(self.parent.Size[1] * self.scaling_ratio), wx.IMAGE_QUALITY_HIGH)
        
    
    # TODO: update and bind to listener 
    def update_panel(self, image):  
        self.curdis.SetBitmap(self.scale_image_for_display(image).ConvertToBitmap())
        
        
    def onResize(self,event):
        self.v_sizer.Clear()
        self.bitmap = scale_bitmap(self.bitmap,self.parent.Size[1]*0.80)            
        self.curdis.SetBitmap(self.bitmap)
        self.v_sizer.Add(self.curdis, 1, wx.ALIGN_CENTER)
        self.Refresh()
        self.Layout()
        
    



        
