'''
main_window.py
'''

import wx
import numpy as np 
from gui_subpanels import CameraControlPanel, CameraPanel, SLMControlPanel, SLMPointsPanel, SLMMonitorPanel

# TODO: refactor scale_image_for_display

class MainWindow(wx.Frame):
    def __init__(self, pos, size):
        super().__init__(parent = None, title = "SLM and Camera Control", 
                         pos = pos, size = size)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        self.camera_object = wx.GetApp().camera_object
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetMinSize(size)
        self.main_panel = wx.Panel(self)
        self.main_hbox = wx.BoxSizer(wx.HORIZONTAL)
        
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
                          
        self.main_hbox.Add(self.fgs, proportion = 1, flag = wx.ALL | wx.EXPAND, border = 0)
        self.SetSizer(self.main_hbox)
        
        self.InitUI()
        
        
    def OnClose(self, event):
        self.camera_object._cleanup()
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
    







            

        
    



        
