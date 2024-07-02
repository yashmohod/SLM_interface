import wx
from screeninfo import get_monitors
import numpy as np
from PIL import Image as im
import pyhot
import os
import glob
import yaml 
import time

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

class CameraContainer(object):
    def __init__(self):
        gui_dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        config_fname = os.path.abspath(gui_dir_abs_path) + os.sep + 'dll_path_config.yaml'
        with open(config_fname, mode = 'r') as file:
            config = yaml.safe_load(file)
        dll_abs_path = config['dll_absolute_path']
        os.environ['PATH'] = dll_abs_path + os.pathsep + os.environ['PATH']
        os.add_dll_directory(dll_abs_path)
        
        self.sdk = TLCameraSDK()
        
        available_cameras = self.sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            print("no cameras detected")
            self.camera = None
        else:
            self.camera = self.sdk.open_camera(available_cameras[0])
            self.camera.exposure_time_us = 5000 # 5 ms
            self.camera.image_poll_timeout_ms = 1000
            self.camera.frames_per_trigger_zero_for_unlimited = 1
            self.camera.arm(2)
            
    def _cleanup(self):
        if self.camera is not None:
            self.camera.disarm()
            self.camera.dispose()
        self.sdk.dispose()
        print("Camera was closed")
        
        

class MainApp(wx.App):
    def __init__(self, cam_object):
        super().__init__(clearSigInt = True)

        # holds camera object
        self.camera_object = cam_object

        # init frames
        self.InitAppFrame()

    def InitAppFrame(self):
        self.main_display = wx.Display(1)
        self.cur_display_geometry = self.main_display.GetGeometry()
        self.scree_size = 0.7
        self.X = round(self.cur_display_geometry[2]/2 - self.cur_display_geometry[2]*self.scree_size/2)
        self.Y = round(self.cur_display_geometry[3]/2 - self.cur_display_geometry[3]*(self.scree_size+0.1)/2)
        self.Xsize = round(self.cur_display_geometry[2]*self.scree_size)
        self.Ysize = round(self.cur_display_geometry[3]*(self.scree_size+0.1))
        gui = appFrame(parent=None,
                       title="SLM",
                       pos=(self.X,self.Y),
                       size=(self.Xsize,self.Ysize),
                       camera_object = self.camera_object
                       )
        gui.Show()
        
    
    def OnExit(self):
        '''
        put cleanup code here
        '''
        print("main app onexit")
        self.camera_object._cleanup()


class appFrame(wx.Frame):
    def __init__(self,parent,title, pos,size, camera_object):
        super().__init__(parent = parent, title = title, pos = pos, size = size )
        self.camera_object = camera_object
        self.OnInit()
        self.InitUI()

    def OnInit(self):
        guiPanel = appPanel(parent=self, camera_object = self.camera_object)
        
    def InitUI(self):
        self.CreateMenuBar()
        self.panel = wx.Panel(self)

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

class appPanel(wx.Panel):
    def __init__(self,parent, camera_object):
        super().__init__(parent = parent)
        self.holograms=[]
        self.OnInit()
        self.camera_object = camera_object

    def OnInit(self):
        self.monitor_count = wx.Display.GetCount()
        self.curDisplay = 1
        self.secondDisplayGeo = wx.Display(self.curDisplay).GetGeometry()
        self.height = self.secondDisplayGeo[3]
        self.width = self.secondDisplayGeo[2]
        dis2 = wx.Display(0)
        self.geo= dis2.GetGeometry()
        self.curDisplayPic = np.zeros((self.geo[3],self.geo[2],3),dtype=np.uint8)
        self.holo = hologram(self,
                        pos = (self.geo[0],self.geo[1]),
                        size=(self.geo[2],self.geo[3]),
                        img =self.arrTObitmap(self.curDisplayPic)
                        )
        self.holo.Show()

        self.unitsL = wx.StaticText(self, label = "Use any consistent length units.",
                                    pos = (20, 500))
        self.pxL = wx.StaticText(self, label="Pixel size", pos=(20,530))
        self.pxVal = wx.TextCtrl(self, value="", pos=(110,530), size=(100,-1))
        self.flocalLenL = wx.StaticText(self, label="Focal length", pos=(20,560))
        self.flocalLenVal = wx.TextCtrl(self, value="", pos=(110,560), size=(100,-1))
        self.WaveLenL = wx.StaticText(self, label="Wavelength", pos=(20,590))
        self.WaveLenVal = wx.TextCtrl(self, value="", pos=(110,590), size=(100,-1))

        self.multitrap_rb = wx.RadioBox(self, label = 'Multiple trap method',
                                        pos = (20, 650),
                                        choices = ['Simultaneous', 'Time-shared'])
        self.update_timeL = wx.StaticText(self, label = 'Time share period [ms]',
                                          pos = (20, 710))
        self.update_timeVal = wx.TextCtrl(self, value = '50', pos = (160, 710),
                                          size = (50, -1))




        # points

        self.pointL = wx.StaticText(self, label="Points", pos=(250,500))
        # self.pointsList = wx.ListBox(self,size = (200,200),pos =(250,525) ,style = wx.LB_SINGLE)
        self.points = wx.TextCtrl(self,size = (200,250),pos =(250,525),style = wx.TE_MULTILINE)

        # addPoints = wx.Button(self,id = wx.ID_ANY, size= (100,40), pos =(250,730),label= "Add Points")
        # clearPoints = wx.Button(self,id = wx.ID_ANY, size= (100,40), pos =(350,730),label= "Cleas Points")



        # display status
        # png = img.ConvertToBitmap()
        png =self.arrTObitmap(self.curDisplayPic)

        # png = wx.Image("./test.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # curdis = wx.StaticBitmap(self, id = wx.ID_ANY, bitmap = scale_bitmap(png,700,500), size= (-1,200))
        self.curdis = wx.StaticBitmap(self, id = wx.ID_ANY, bitmap = scale_bitmap(png,0.4), pos = (225,0))

        # set current display
        updateDisplay = wx.Button(self,id = wx.ID_ANY, size= (200,40),pos = (500,500),label= "Update Display")
        updateDisplay.Bind(wx.EVT_BUTTON,self.updateDisplay)

        # timer for updating
        self.update_time_ms = int(self.update_timeVal.GetValue())
        self.UpdateFlag = False
        self.ChangedFlag = False
        self.timer = wx.Timer(self, id = 2)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id = 2)
        #self.timer.Start(self.update_time_ms)

        self.ImgSeqNum = 0 # Flag to point to different
        
        # Create a second timer for acquiring video frames 
        self.cam_timer = wx.Timer(self, id = 1)
        self.Bind(wx.EVT_TIMER, self.show_camera, id = 1)
        # triggers at 20 frames/sec (every 50 ms)
        self.cam_timer.Start(50)


    def show_camera(self, event):
        self.camera_object.camera.issue_software_trigger()
        frame = self.camera_object.camera.get_pending_frame_or_null()
        if frame is not None:
            image_buffer_copy = np.copy(frame.image_buffer)
            self.curdis.SetBitmap(scale_bitmap(self.arrTObitmap2(image_buffer_copy, 
                                                                 self.camera_object.camera.bit_depth), 0.5))
        

    def updateDisplay(self,event):
        '''
        Calculates hologram for n points and updates the display, or
        calculates a series of single-point holograms and loops through
        displaying them.
        '''

        pts = self.points.GetValue()
        pts = pts.split("\n")
        ptsarr=[]
        for pt in pts:
            if pt != "":
                if str(pt).count("(") == 1 and str(pt).count(")") == 1 and str(pt).count(",") == 2:
                    pt = str(pt).replace("(","").replace(")","").split(",")
                    ptsarr.append([float(pt[0]),float(pt[1]),float(pt[2])])

        #print(float(self.pxVal.GetValue()), float(self.WaveLenVal.GetValue()), float(self.flocalLenVal.GetValue()))
        mySLMengine = pyhot.SLM(self.geo[3],self.geo[2],float(self.pxVal.GetValue()), float(self.WaveLenVal.GetValue()), float(self.flocalLenVal.GetValue()))

        if self.multitrap_rb.GetSelection() == 0: # Simultaneous display
            self.timer.Stop()
            holo = mySLMengine.calc_holo(ptsarr)
            self.curDisplayPic = holo
            data = im.fromarray(holo).convert('RGB')
            data.save('temp.png')
            png = wx.Image('temp.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.holo.updateIMG(png)
            self.curdis.SetBitmap(scale_bitmap(png, 0.4))
        else: # time sharing
            # update timer interval
            self.update_time_ms = int(self.update_timeVal.GetValue())
            self.timer.Start(self.update_time_ms)

            # delete previous tempXX.png files
            png_list = glob.glob('temp[0123456789][0123456789].png')
            for fname in png_list:
                os.remove(fname)

            for pt, ctr in zip(ptsarr, np.arange(len(pts))):
                holo = mySLMengine.calc_holo(np.array([pt])) # single point hologram
                data = im.fromarray(holo).convert('RGB')
                fname = 'temp' + str(ctr).zfill(2) + '.png'
                data.save(fname)

            self.ImageSeqNum = 0
            self.UpdateFlag = True
            self.ChangedFlag = True


    def arrTObitmap(self,array):
        h,w = array.shape[0], array.shape[1]
        #print(len(array.shape))
        if len(array.shape) == 2:
            bw_array = array.copy()
            bw_array.shape = h, w, 1
            color_array = np.concatenate((bw_array,bw_array,bw_array), axis=2)
            data = color_array.tobytes()
        else :
            data = array.tobytes()
        img = wx.ImageFromBuffer(width=w, height=h, dataBuffer=data)
        # png = img.ConvertToBitmap()
        return wx.Bitmap(img)


    def arrTObitmap2(self, array, bits):
        '''
        Convert grayscale Numpy array from Thorlabs camera (2D) to a wx Bitmap object.
        See discussion at
        https://stackoverflow.com/questions/65283588/display-numpy-array-cv2-image-in-wxpython-correctly
        '''
        h, w = array.shape[:2]
        # Input images from camera are uint16, but bit depth is user-settable 
        # Normalize image and convert to 0-255
        data = array.astype(np.float64) / (2**bits - 1) * 255
        data = data.astype(np.uint8)
        # Now need to cast to rgb by duplicating channels
        color_data = np.repeat(data[:, :, np.newaxis], 3, axis = 2)
        return wx.Bitmap.FromBuffer(width = w, height = h, data = color_data)
        


    def OnTimer(self, event):
        if self.UpdateFlag is True:
            # list all files named tempXX.png
            png_list = glob.glob('temp[0123456789][0123456789].png')
            png_list.sort()
            #print(png_list)
            n_imgs = len(png_list)

            if (n_imgs == 1) and (self.ChangedFlag is False):
                return
            else:
                # update displays
                fname = 'temp' + str(self.ImageSeqNum).zfill(2) + '.png'
                png = wx.Image(fname, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                self.holo.updateIMG(png)
                self.curdis.SetBitmap(scale_bitmap(png,0.4))

                # update pointer
                if self.ImageSeqNum == (n_imgs - 1): # cycle back
                    self.ImageSeqNum = 0
                else:
                    self.ImageSeqNum += 1

                self.ChangedFlag = False

class hologram(wx.Frame):
    def __init__(self,parent, pos,size,img):
        super().__init__(parent = parent, pos = pos, size = size, style = wx.NO_BORDER)
        self.curdis = wx.StaticBitmap(self, id = wx.ID_ANY, bitmap = img, pos = (0,0))

    def updateIMG(self,img):
        self.curdis.SetBitmap(img)




# class hologram():
#     def __init__(self,id,px,waveLen,focalLen):
#         self.id = id
#         self.px = px
#         self.waveLen = waveLen
#         self.focalLen = focalLen
#         self.points = []

#     def getId(self):
#         return self.id

#     def getPoints(self):
#         return self.points

#     def clearPoints(self):
#         self.points=[]

#     def addPoint(self,point):
#         self.points.append(point)

#     def calImg(self,height,width):
#         mySLMengine = pyhot.SLM(height,width,self.px, self.waveLen, self.focalLen)
#         img_result = mySLMengine.calc_holo(self.points)
#         return img_result





# def scale_bitmap(bitmap, width, height):
def scale_bitmap(bitmap,ratio):
    # image = wx.ImageFromBitmap(bitmap)
    image =  bitmap.ConvertToImage()
    image = image.Scale(round(bitmap.GetWidth()*0.4), round(bitmap.GetHeight()*0.4), wx.IMAGE_QUALITY_HIGH)
    # image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.Bitmap(image)
    return result

if __name__ == "__main__":
    cam_container = CameraContainer()
    app = MainApp(cam_container)
    app.MainLoop()
