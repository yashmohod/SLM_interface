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


        self.pxL = wx.StaticText(self, label="px", pos=(20,500))
        self.pxVal = wx.TextCtrl(self, value="", pos=(110,500), size=(100,-1))
        self.flocalLenL = wx.StaticText(self, label="Focal Length", pos=(20,530))
        self.flocalLenVal = wx.TextCtrl(self, value="", pos=(110,530), size=(100,-1))
        self.WaveLenL = wx.StaticText(self, label="Wave Length", pos=(20,560))
        self.WaveLenVal = wx.TextCtrl(self, value="", pos=(110,560), size=(100,-1))




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


    def updateDisplay(self,event):
        pts = self.points.GetValue()
        pts = pts.split("\n")
        ptsarr=[]
        for pt in pts:
            if pt != "":
                if str(pt).count("(") == 1 and str(pt).count(")") == 1 and str(pt).count(",") == 2:
                    pt = str(pt).replace("(","").replace(")","").split(",")
                    ptsarr.append([float(pt[0]),float(pt[1]),float(pt[2])])

        print(float(self.pxVal.GetValue()), float(self.WaveLenVal.GetValue()), float(self.flocalLenVal.GetValue()))
        mySLMengine = pyhot_backup.SLM(self.geo[3],self.geo[2],float(self.pxVal.GetValue()), float(self.WaveLenVal.GetValue()), float(self.flocalLenVal.GetValue()))
        self.curDisplayPic = mySLMengine.calc_holo(ptsarr)
        data = im.fromarray(mySLMengine.calc_holo(ptsarr)).convert('RGB')
        data.save('temp.png')
        png = wx.Image('temp.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.holo.updateIMG(png)
        self.curdis.SetBitmap(scale_bitmap(png,0.4))



    def arrTObitmap(self,array):
        h,w = array.shape[0], array.shape[1]
        print(len(array.shape))
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
    image = image.Scale(round(bitmap.GetWidth()*ratio), round(bitmap.GetHeight()*ratio), wx.IMAGE_QUALITY_HIGH)
    # image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.Bitmap(image)
    return result

if __name__ == "__main__":
    app = MainApp()
    app.MainLoop()
