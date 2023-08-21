import wx 
from screeninfo import get_monitors
import numpy as np 
from PIL import Image as im
import pyhot

class MainApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt = True)

        # init frames
        self.InitAppFrame()

    def InitAppFrame(self):
        self.main_display = wx.Display(0)
        self.cur_display_geometry = self.main_display.GetGeometry()
        self.scree_size = 0.7
        self.X = round(self.cur_display_geometry[2]/2 - self.cur_display_geometry[2]*self.scree_size/2)
        self.Y = round(self.cur_display_geometry[3]/2 - self.cur_display_geometry[3]*self.scree_size/2)
        self.Xsize = round(self.cur_display_geometry[2]*self.scree_size)
        self.Ysize = round(self.cur_display_geometry[3]*self.scree_size)
        gui = appFrame(parent=None, 
                       title="SLM", 
                       pos=(self.X,self.Y), 
                       size=(self.Xsize,self.Ysize),
                       )
        gui.Show()

class appFrame(wx.Frame):
    def __init__(self,parent,title, pos,size):
        super().__init__(parent = parent, title = title, pos = pos, size = size)
        self.OnInit()

    def OnInit(self):
        guiPanel = appPanel(parent=self)

class appPanel(wx.Panel):
    def __init__(self,parent):
        super().__init__(parent = parent)
        self.holograms=[]
        self.OnInit()

    def OnInit(self):
        self.monitor_count = wx.Display.GetCount()
        self.curDisplay = 0
        self.secondDisplayGeo = wx.Display(self.curDisplay).GetGeometry()
        self.height = self.secondDisplayGeo[3]
        self.width = self.secondDisplayGeo[2]
        self.curDisplayPic = np.zeros((self.height,self.width,3),dtype=np.uint8)
        
        mainHbox =  wx.BoxSizer(wx.HORIZONTAL) 

        # hologams 
        holoGramBox = wx.BoxSizer(wx.VERTICAL)

        # languages = ['C', 'C++', 'Java', 'Python', 'Perl', 'JavaScript', 'PHP', 'VB.NET','C#']   
        self.hologramList = wx.ListBox(self,size = (200,300), style = wx.LB_SINGLE)
        self.hologramList.Bind(wx.EVT_LISTBOX, self.selectHologram)
        holoGramBox.Add(self.hologramList,0,wx.ALIGN_CENTER_HORIZONTAL)

        addHologram = wx.Button(self,id = wx.ID_ANY, size= (100,40),label= "Add hologram")
        addHologram.Bind(wx.EVT_BUTTON,self.addhologram)
        holoGramBox.Add(addHologram,1,wx.ALIGN_CENTER_HORIZONTAL)

        mainHbox.Add(holoGramBox,0)
        # points
        pointsBox = wx.BoxSizer(wx.VERTICAL)

        self.pointsList = wx.ListBox(self,size = (200,300), style = wx.LB_SINGLE)
        pointsBox.Add(self.pointsList,0,wx.ALIGN_CENTER_HORIZONTAL)

        addPoints = wx.Button(self,id = wx.ID_ANY, size= (100,40),label= "Add Points")
        pointsBox.Add(addPoints,1,wx.ALIGN_CENTER_HORIZONTAL)


        mainHbox.Add(pointsBox,1)

        # display status
        displayBox = wx.BoxSizer(wx.VERTICAL)
        # png = img.ConvertToBitmap()
        png =self.arrTObitmap(self.curDisplayPic)
 
        # png = wx.Image("./test.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # curdis = wx.StaticBitmap(self, id = wx.ID_ANY, bitmap = scale_bitmap(png,700,500), size= (-1,200))
        self.curdis = wx.StaticBitmap(self, id = wx.ID_ANY, bitmap = scale_bitmap(png,0.5))
        displayBox.Add(self.curdis,0,wx.ALIGN_CENTER_HORIZONTAL)

        allopt =  wx.BoxSizer(wx.HORIZONTAL)
        # set current display
        curdisplayOp1 = wx.BoxSizer(wx.VERTICAL)
        curDisplayText = wx.StaticText(self,id= wx.ID_ANY,label ="None", size = (-1,40))
        curdisplayOp1.Add(curDisplayText,0,wx.ALIGN_CENTER_HORIZONTAL)
        setCurDisplay = wx.Button(self,id = wx.ID_ANY, size= (200,40),label= "Set as Current Display")
        curdisplayOp1.Add(setCurDisplay,1,wx.ALIGN_CENTER_HORIZONTAL)
        allopt.Add(curdisplayOp1,1)

        curdisplayOp2 = wx.BoxSizer(wx.VERTICAL)
        displayNoTextBox = wx.TextCtrl(self,id = wx.ID_ANY,size=(60,40))
        curdisplayOp2.Add(displayNoTextBox,0,wx.ALIGN_CENTER_HORIZONTAL)
        setDisplay = wx.Button(self,id = wx.ID_ANY, size= (200,40),label= "Set Display")
        curdisplayOp2.Add(setDisplay,1,wx.ALIGN_CENTER_HORIZONTAL)
        allopt.Add(curdisplayOp2,2)
        displayBox.AddSpacer(10)
        displayBox.Add(allopt,1,wx.ALIGN_CENTER_HORIZONTAL)
        


        mainHbox.Add(displayBox,2)

        self.SetSizer(mainHbox)

    def selectHologram(self,event):
        holoID = event.GetEventObject().GetStringSelection()
        for holos in self.holograms:
            if holos.getId() == holoID:
                h = wx.Display(self.curDisplay).GetGeometry()[3]
                w = wx.Display(self.curDisplay).GetGeometry()[2]
                self.curHolo = holoID
                self.curDisplayPic = holos.calImg(h,w)
                self.curdis.SetBitmap(self.arrTObitmap(self.curDisplayPic))
                for point in holos.getPoints():
                    self.pointsList.Append("("+str(point[0])+","+str(point[1])+","+str(point[2])+")")

    
    def addhologram(self, event):
        addHoloDiologBox = addNupdateHologram(self)
        addHoloDiologBox.ShowModal()
        if addHoloDiologBox.approved:
            id = addHoloDiologBox.id
            px = addHoloDiologBox.px
            waveLen = addHoloDiologBox.WaveLen
            focalLen = addHoloDiologBox.flocalLen
            self.holograms.append(hologram(id,px,waveLen,focalLen))
            self.hologramList.Append(id)
        else:
            # self.log.AppendText("No Input found\n")
            pass
        addHoloDiologBox.Destroy()

    def arrTObitmap(array):
        h,w = array.shape[0], array.shape[1]

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
        

class addNupdateHologram(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Name Input", size= (250,300))
        self.panel = wx.Panel(self,wx.ID_ANY)

        self.idL = wx.StaticText(self.panel, label="ID", pos=(20,20))
        self.idVal = wx.TextCtrl(self.panel, value="", pos=(110,20), size=(100,-1))
        self.pxL = wx.StaticText(self.panel, label="px", pos=(20,60))
        self.pxVal = wx.TextCtrl(self.panel, value="", pos=(110,60), size=(100,-1))
        self.flocalLenL = wx.StaticText(self.panel, label="Flocal Length", pos=(20,100))
        self.flocalLenVal = wx.TextCtrl(self.panel, value="", pos=(110,100), size=(100,-1))
        self.WaveLenL = wx.StaticText(self.panel, label="Wave Length", pos=(20,140))
        self.WaveLenVal = wx.TextCtrl(self.panel, value="", pos=(110,140), size=(100,-1))
        self.saveButton =wx.Button(self.panel, label="Create", pos=(30,180))
        self.closeButton =wx.Button(self.panel, label="Cancel", pos=(140,180))
        self.saveButton.Bind(wx.EVT_BUTTON, self.SaveConnString)
        self.closeButton.Bind(wx.EVT_BUTTON, self.OnQuit)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Show()

    def OnQuit(self, event):
        self.approved = None
        self.Destroy()

    def SaveConnString(self, event):
        self.approved = True
        self.id = self.idVal.GetValue()
        self.px = self.pxVal.GetValue()
        self.flocalLen = self.flocalLenVal.GetValue()
        self.WaveLen = self.WaveLenVal.GetValue()
        self.Destroy()



class hologram():
    def __init__(self,id,px,waveLen,focalLen):
        self.id = id
        self.px = px
        self.waveLen = waveLen
        self.focalLen = focalLen
        self.points = []
    
    def getId(self):
        return self.id
    
    def getPoints(self):
        return self.points

    def clearPoints(self):
        self.points=[]

    def addPoint(self,point):
        self.points.append(point)
    
    def calImg(self,height,width):
        mySLMengine = pyhot_backup.SLM(height,width,self.px, self.waveLen, self.focalLen)
        img_result = mySLMengine.calc_holo(self.points)
        return img_result





# def scale_bitmap(bitmap, width, height):
def scale_bitmap(bitmap,ratio):
    # image = wx.ImageFromBitmap(bitmap)
    image =  bitmap.ConvertToImage()
    image = image.Scale(round(bitmap.GetWidth()*ratio), round(bitmap.GetHeight()*ratio), wx.IMAGE_QUALITY_HIGH)
    # image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.Bitmap(image)
    return result

if __name__ == "__main__":
    app = MainApp()
    app.MainLoop()