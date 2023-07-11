import wx
class ExamplePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.quote = wx.StaticText(self, label="Your quote :", pos=(20, 30))

        # A button
        self.button =wx.Button(self, label="Save", pos=(200, 325))

    self.lblname = wx.StaticText(self, label="Your name :", pos=(20,60))
    self.editname = wx.TextCtrl(self, value="Enter here your name", pos=(150, 60), size=(140,-1))


app = wx.App(False)
frame = wx.Frame(None)
panel = ExamplePanel(frame)
frame.Show()
app.MainLoop()