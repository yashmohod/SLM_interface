'''
main_window.py
'''

import wx
import numpy as np 
from PIL import Image as im
import os
from gui_subpanels import CameraControlPanel, CameraPanel, SLMControlPanel, SLMPointsPanel, SLMMonitorPanel

# TODO: refactor scale_image_for_display

class MainWindow(wx.Frame):
    def __init__(self, pos, size):
        super().__init__(parent = None, title = "SLM and Camera Control", 
                         pos = pos, size = size)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        self.camera_object = wx.GetApp().camera_object
        self.slm_object = wx.GetApp().slm_object
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
        
        self.CreateMenuBar()
        
        
        
    def OnClose(self, event):
        self.camera_object._cleanup()
        self.Destroy()


    def CreateMenuBar(self):
        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        
        saveSubMenu = wx.Menu()
       
        
        saveSubMenu.Append(501, 'Save images with blinking traps', 'Save images with blinkig traps')
        saveSubMenu.Append(201, 'Save sequence of images', 'Save sequence of images')
        #fileMenu.AppendSubMenu(saveSubMenu, 'Acquire')
    
        
        #settings menu
        settingsMenu = wx.Menu()
        exposureMenu = wx.Menu()
        
        ROIMenu = wx.Menu()
        ROIMenu.Append(301, 'Set ROI coordinates', 'Set ROI coordinates') 
        ROIMenu.Append(401, 'Full frame', 'Reset')
        exposureMenu.Append(101, 'Set Exposure Time', 'Set exposure time')
        settingsMenu.AppendSubMenu(ROIMenu, 'ROI')
        settingsMenu.AppendSubMenu(exposureMenu, 'Exposure Time')
        
        menubar.Append(fileMenu,'&File')
        menubar.Append(saveSubMenu, '&Acquire')
        menubar.Append(settingsMenu, '&Settings')

        
        self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnSetExposure, id=101)
        self.Bind(wx.EVT_MENU, self.OnSaveSequence, id = 201)
        self.Bind(wx.EVT_MENU, self.OnSetROI, id = 301)
        self.Bind(wx.EVT_MENU, self.OnResetROI, id = 401)
        self.Bind(wx.EVT_MENU, self.OnSaveBlink, id = 501)
        self.SetMenuBar(menubar)
        
        
    def OnSaveBlink(self,e):
        dlg = wx.DirDialog(self, "Choose file directory to save images",style = wx.DD_DEFAULT_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
          path_b = dlg.GetPath()
          dlg.Destroy()
          
          
          dialog = wx.Dialog(self, title = "Save sequence of images with blinking traps")
          dialog.SetSize((420,300))
          wx.StaticText(dialog,label = "Folder Path", pos = (10,10))
          path_blink_text = wx.TextCtrl(dialog, value = path_b, pos = (120,10), size = (100,-1), style =wx.TE_READONLY)
          
          wx.StaticText(dialog, label = "File name",pos = (10,40))
          filename_blink_text = wx.TextCtrl(dialog, pos = (120,40), size = (200,-1))
          
          wx.StaticText(dialog, label = "Number of images in each acquisition", pos = (10,70))
          num_images_acqu = wx.SpinCtrl(dialog, value = '1', pos = (250,70), size = (80, -1), min = 1, max = 2000)
          
          
          wx.StaticText(dialog, label = "Frame rate", pos = (10,100))
          frame_rate_blink = wx.TextCtrl(dialog, pos = (200,100))
          
          wx.StaticText(dialog, label = "Number of acquisitions for pair of traps", pos = (10,130))
          number_acqu = wx.TextCtrl(dialog, pos = (250,130))
          
          wx.StaticText(dialog, label = "Traps in format (x,y,z)", pos = (10,160))
          trap_1 = wx.TextCtrl(dialog, pos = (140, 160),style = wx.TE_MULTILINE)
          trap_2 = wx.TextCtrl(dialog, pos = (265, 160),style = wx.TE_MULTILINE)
          
          wx.StaticText(dialog, label = f'"Far away" trap', pos = (10,200))
          blank_trap = wx.TextCtrl(dialog, pos = (140, 200))
          
          btn_ok = wx.Button(dialog, wx.ID_OK, "Start Acquisition with blinking traps", pos = (90, 230))
          btn_cancel = wx.Button(dialog, wx.ID_CANCEL, "Cancel", pos = (300,230))
          
          
          btn_ok.Bind(wx.EVT_BUTTON, lambda event: self.OnStartAcquisitionBlink(event, path_blink_text.GetValue(), filename_blink_text.GetValue(), num_images_acqu.GetValue(), frame_rate_blink.GetValue(), number_acqu.GetValue(), trap_1.GetValue(), trap_2.GetValue(), blank_trap.GetValue()))
          
          
          
          if dialog.ShowModal() ==wx.ID_OK:
       
            filename1 = filename_blink_text.GetValue() #1
            num_images_acquisition = num_images_acqu.GetValue() #2
            frame_rate_b = frame_rate_blink.GetValue() #3
            number_of_acquisitions = number_acqu.GetValue() #4
            trap_list_1 = trap_1.GetValue() #5
            trap_list_2 = trap_2.GetValue() #6
            blank_trap_coord = blank_trap.GetValue() #7 
            
            
    def OnStartAcquisitionBlink(self,e,path_b,filename1,num_images_acquisition, frame_rate_b, number_of_acquisitions,trap_list_1,trap_list_2,blank_trap_coord):
        #list for trap 1
        traps_1 = []
        trap_list_1_lines = trap_list_1.split('\n')
        for point1 in trap_list_1_lines:
            line = point1.strip()[1:-1]
            values = line.split(',')
            traps_1.append([float(values[0]), float(values[1]), float(values[2])])
        
        #list for trap 2
        traps_2 = []
        trap_list_2_lines = trap_list_2.split('\n')
        for point2 in trap_list_2_lines:
            line2 = point2.strip()[1:-1]
            values2 = line2.split(',')
            traps_2.append([float(values2[0]), float(values2[1]), float(values2[2])])
        
        #blank trap
        blank_trap_list = []
        line_blank = blank_trap_coord.split('\n')
        for blankpoint in line_blank:
            blank_line = blankpoint.strip()[1:-1]
            values_b = blank_line.split(',')
            blank_trap_list.append([float(values_b[0]), float(values_b[1]),float(values_b[2])])
        
        
        #nth pair of traps for easy use
        trap_pairing = []
        for trap in range(len(traps_2)):
          trap_pairing.append([list(traps_1[trap]),list(traps_2[trap])])
          
       
        m = 1
        for pair_of_traps in trap_pairing:     
          blank_and_trap = [blank_trap_list[0], pair_of_traps[0]]
          
                   
         
          trap = trap
          number_of_acquisitions = number_of_acquisitions
          num_images_acquisition = num_images_acquisition
         
         #move trap far away
          #change this code
          
          #print(trap_pairing[0][1])
          self.slm_object.update_slm_pts(blank_and_trap)
          
        
          
          #change this code
          
          
          #loop for how many acquisition
          for j in range(int(number_of_acquisitions)):
            num_images_acquisition = num_images_acquisition
            
            #moving traps to position
            
            
            pair_of_trap_list = [pair_of_traps[0], pair_of_traps[1]] #list for calling the update slm method
            
            #change this code
            self.slm_object.update_slm_pts(pair_of_trap_list)
            #change this code
            
            #start recording 
            self.camera_object.camera.disarm()
            self.camera_object.camera.frames_per_trigger_zero_for_unlimited = num_images_acquisition
            self.camera_object.camera.frame_rate_control_value = float(frame_rate_b)
            self.camera_object.camera.arm(num_images_acquisition + 1)
            self.camera_object.camera.issue_software_trigger()
                  
            for i in range(num_images_acquisition):
              frame1 = self.camera_object.camera.get_pending_frame_or_null()
              if frame1 is not None:
                image = np.copy(frame1.image_buffer)
                pil_image1 = im.fromarray(image)
                image_filename1 = filename1  + '_image_' + str(i).zfill(3) + '_' +str(j) + '_' + str(m) + '.tif'
                image_filepath1 = os.path.join(path_b, image_filename1)
                pil_image1.save(image_filepath1)
              print(f"Saved image {i} in acquisition {j} for pair of trap {m} to {image_filepath1}") 
            
            
            #arm camera back
            self.camera_object.camera.disarm()
            self.camera_object.camera.frames_per_trigger_zero_for_unlimited = 1
            self.camera_object.camera.arm(2)  
            #move trap back
            
            #change this code
            self.slm_object.update_slm_pts(blank_and_trap)
            #change this code   
          m += 1
       
    
    def OnSetROI(self, e):
        current_ROI = self.camera_object.camera.roi
        ROI_dialog = wx.TextEntryDialog(self, f'Enter ROI coordinates (x1,y1,x2,y2) (currently at {current_ROI}):) ', 'Set ROI coordinates')
        
        if ROI_dialog.ShowModal() == wx.ID_OK:
           input_text = ROI_dialog.GetValue()
           coordinates = input_text.strip()[1:-1]
           try:
              values = [int(val.strip()) for val in coordinates.split(',')]
              print(values)
              if len(values) == 4:
                 self.camera_object.camera.disarm()
                 lst_roi = list(self.camera_object.camera.roi)
                 lst_roi[0] = values[0]
                 lst_roi[1] = values[1]
                 lst_roi[2] = values[2]
                 lst_roi[3] = values[3]
                 self.camera_object.camera.roi = tuple(lst_roi)
                 self.camera_object.camera.arm(2)
              else:
                 pass
              
           except ValueError:
              pass   
        ROI_dialog.Destroy()              
              
              
    def OnResetROI(self, e):
        self.camera_object.camera.disarm()       
        reset_frame = (0,0,1440,1080)
        reset_list = list(self.camera_object.camera.roi)
        reset_list[0] = reset_frame[0]
        reset_list[1] = reset_frame[1]
        reset_list[2] = reset_frame[2]
        reset_list[3] = reset_frame[3]
        self.camera_object.camera.roi = tuple(reset_list)
        self.camera_object.camera.arm(2)
        print("Back to full frame")
    
    
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
        self.camera_object.camera.disarm()
        self.camera_object.camera.frames_per_trigger_zero_for_unlimited = num_images
        self.camera_object.camera.frame_rate_control_value = float(frame_rate) 
        self.camera_object.camera.arm(num_images+1)
        self.camera_object.camera.issue_software_trigger()
        
        for i in range(num_images):
            frame = self.camera_object.camera.get_pending_frame_or_null()
            if frame is not None:
                image_data = np.copy(frame.image_buffer)
                pil_image = im.fromarray(image_data)
          
                image_filename = filename + str(i).zfill(3) + '.tif'
                image_filepath=os.path.join(path, image_filename)
          
                pil_image.save(image_filepath)
                print(f"Saved image {i+1}/{num_images} to {image_filepath}")
            else:
              print("timeout reached")
              break
        
        self.camera_object.camera.disarm()
        self.camera_object.camera.frames_per_trigger_zero_for_unlimited = 1
        self.camera_object.camera.arm(2)
          
        
          
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
    







            

        
    



        
