import numpy as np
import slmpy
from screeninfo import get_monitors
import pyhot
import threading
import time
from PIL import Image as im

class displayCMD():

    def __init__(self):
        self.monitorsRequired = 1
        self.monitor = get_monitors()[self.monitorsRequired-1]
        self.width = self.monitor.width
        self.height = self.monitor.height
        self.penColor = [255, 255, 255]
        self.traps = []
        self.showTrapBool = True
        self.commandStack = []
        self.curTrap = ""
        self.drawnState = np.zeros((self.height,self.width,3),dtype=np.uint8)
        self.toDraw = []


    # geometries
    def calCircle(self,radius,x,y):
        r = radius
        m = np.zeros((round(2*r+2),round(2*r+2),3),dtype=np.uint8)
        a, b = r, r
        for row in range(0, m.shape[0]):
            for col in range(0, m.shape[1]):
                if (col-a)**2 + (row-b)**2 >= (r**2)*0.9 and (col-a)**2 + (row-b)**2 <= r**2:
                    m[row,col] =self.penColor
        temp = np.zeros((self.height,self.width,3),dtype=np.uint8)
        temp[round(y):round(y+2+r*2),round(x):round(x+2+r*2)] = m
        return temp

    # app utilites
    def decoder(self,cmd):
        if cmd.count("(") > 1 :
            print("Syntax error: extra '(' ")
        elif cmd.count(")") > 1:
            print("Syntax error: extra ')' ")
        elif cmd.count("(") < 1 :
            print("Syntax error: missing '(' ") 
        elif cmd.count(")") < 1 :
            print("Syntax error: missing ')' ") 
        else:
            command = cmd.split("(")[0]
            args = cmd.split("(")[1].replace(")","").split(",")
            match command:
                case "circle":
                    exceptedNoArgs = 4
                    if len(args) == exceptedNoArgs:
                        return True,"circle",args
                    else: 
                        print("Recived number of args:"+ str(len(args))+" Expected number of args:" +str(exceptedNoArgs))
                case "move":
                    exceptedNoArgs = 3
                    if len(args) == exceptedNoArgs:
                        return True,"move",args
                    else: 
                        print("Recived number of args:"+ str(len(args))+" Expected number of args:" +str(exceptedNoArgs))
                case "resize":
                    exceptedNoArgs = 2
                    if len(args) == exceptedNoArgs:
                        return True,"resize",args
                    else: 
                        print("Recived number of args:"+ str(len(args))+" Expected number of args:" +str(exceptedNoArgs))
                case "listObjects":
                    return True, "listObjects",[]
                case "trap":
                    exceptedNoArgs = 4
                    if len(args) == exceptedNoArgs:
                        return True,"trap",args
                    else: 
                        print("Recived number of args:"+ str(len(args))+" Expected number of args:" +str(exceptedNoArgs))
                case "addPoint":
                    exceptedNoArgs = 4
                    if len(args) == exceptedNoArgs:
                        return True,"addPoint",args
                    else: 
                        print("Recived number of args:"+ str(len(args))+" Expected number of args:" +str(exceptedNoArgs))
                case "setTrap":
                    exceptedNoArgs = 1
                    if len(args) == exceptedNoArgs:
                        return True,"setTrap",args
                    else: 
                        print("Recived number of args:"+ str(len(args))+" Expected number of args:" +str(exceptedNoArgs))
                case "clearPoints":
                    exceptedNoArgs = 1
                    if len(args) == exceptedNoArgs:
                        return True,"clearPoints",args
                    else: 
                        print("Recived number of args:"+ str(len(args))+" Expected number of args:" +str(exceptedNoArgs))
                case "exit":
                    return True,"exit",[]
                case _:
                    print("Command not recognized!")

        return False,"",[]


    # returns True if an object with the same key exits
    def checkDuplicate(self,toCheck):
        for item in self.toDraw:
            if item[1] == toCheck:
                return True
        return False    
    def checkDuplicateTraps(self,toCheck):
        for item in self.traps:
            if item.getId() == toCheck:
                return True
        return False   

        

    def updateExecutor(self,cmd,args):
        match cmd:
            case "circle":
                if not self.checkDuplicate(args[0]):
                    self.toDraw.append(["circle",args[0],float(args[1]),float(args[2]),float(args[3])])
                else:
                    print("Objet already exits. Can't create another object with the same key!\nTry listObjects() to view all currently drawn objects.")
            case "move":
                for item in  self.toDraw:
                    if item[1] == args[0]:
                        item[3] = float(args[1])
                        item[4] = float(args[2])
            case "resize":
                for item in  self.toDraw:
                    if item[1] == args[0]:
                        item[2] = float(args[1])
            case "listObjects":
                    print("All objects:")
                    count = 0
                    for item in self.toDraw:
                        count+=1
                        print("#"+str(count)+" "+item[1])
            case "trap":
                    # trap(idpx,waveLen,focalLen)
                    if not self.checkDuplicateTraps(args[0]):
                        trapInstance = trap(args[0],float(args[1]),float(args[2]),float(args[3])) 
                        self.traps.append(trapInstance)
                        self.curTrap = args[0]
                    else: 
                        print("Trap with id '"+args[0]+"' already exsits!")
            case "addPoint":
                    # trap(idpx,waveLen,focalLen)  
                    for i in self.traps:
                        if args[0] == i.getId():
                            i.addPoint([float(args[1]),float(args[2]),float(args[3])])
            case "clearPoints":
                    # trap(idpx,waveLen,focalLen)  
                    for i in self.traps:
                        if args[0] == i.getId():
                            i.clearPoints()
            case "setTrap":
                if  self.checkDuplicateTraps(args[0]):
                    self.curTrap = args[0]
                else:
                    print("Not trap with id '"+args[0]+"' was not found!")
            case "exit":
                self.slt.end()
                exit()
            case _:
                print("Command not recognized:"+str(cmd)+"\nSomthing went wrong in decoding!")
        
        self.drawer()
                

    def drawer(self):
        self.drawnState = np.zeros((self.height,self.width,3),dtype=np.uint8)
        if self.showTrapBool:
            for i in self.traps :
                if self.curTrap == i.getId():
                    self.drawnState = i.calImg()
        else:
            for item in self.toDraw:
                match item[0]:
                    case 'circle':
                        self.drawnState += self.calCircle(item[2],item[3],item[4])
                    case _:
                        print("Geometry not recognized:"+str(item[0])+"\nSomething went wrong in updateExecutor!")



    # CMD main app loop
    def mainLoop(self):
        appRunpre = True
        appRun = False
        resetTry = 0
        while appRunpre:
            print("Welcome to SLMP CMD version!")
            uinput = input("Press enter 'y' if ready or 'n' to exit now: ")

            if uinput == "y":
                if len(get_monitors()) < self.monitorsRequired:
                    print("*****************************************************")
                    print("Please make sure you have a second screen connected! ")
                    input("*****************************************************")
                else: 
                    appRunpre = False
                    appRun = True
            elif uinput == "n":
                print("Good Bye!")
                exit()
            else:
                print("Please try again...")

        try:
            slm = slmpy.SLMdisplay()
            
            # monitor = get_monitors()[1]
            # width = monitor.width
            # height = monitor.height
            print("Display Ready!")
            print("Ready for inputs:")
        except:
            print("Something went wrong app resetting...")
            if resetTry > 2:
                print("Too many reset tries...\nApp shutting down...")
                exit()
            resetTry+=1
            self.mainLoop()

        # screen update thread
        # self.slt = screenLoop()
        # self.slt.start(slm,self.drawnState)

        # app loop
        while appRun:
            cmd = input()
            needUpdate = False
            needUpdate,cmd,args = self.decoder(cmd)
            if needUpdate:
                # # stop the screen update thread
                # self.slt.stop()
                # # update toDraw
                self.updateExecutor(cmd,args)
                slm.updateArray(self.drawnState)
                # # # restart screen thread
                # self.slt.start(slm,self.drawnState)
            

class trap():
    def __init__(self,id,px,waveLen,focalLen):
        self.id = id
        self.monitorsRequired = 1
        self.monitor = get_monitors()[self.monitorsRequired-1]
        self.width = self.monitor.width
        self.height = self.monitor.height 
        self.point = []
        self.mySLMengine = pyhot.SLM(self.height,self.width,px, waveLen, focalLen)
    
    def getId(self):
        return self.id

    def clearPoints(self):
        self.point=[]

    def addPoint(self,point):
        self.point.append(point)
    
    def calImg(self):
        img_result = self.mySLMengine.calc_holo(self.point)
        return img_result



# class screenLoop():
#     def screenUpdate(self):
#         while True:
#             self.slm.updateArray( self.drawnState)
#             time.sleep(1)
#             if self.screenUpdateBool:
#                 # slm.close()
#                 break
#     def start(self,slm,drawnState):
#         self.screenUpdateBool = False
#         self.slm = slm
#         self.drawnState = drawnState
#         self.screenThread = threading.Thread(target=self.screenUpdate )
#         self.screenThread.daemon = True
#         self.screenThread.start()
#     def stop(self):
#         self.screenUpdateBool = True
#         self.screenThread.join()
#     def end(self):
#         self.stop()
#         self.slm.close()





if __name__ == "__main__":
    app = displayCMD()
    app.mainLoop()




"""
syntax:

Command                                     Description
circle(id,radius,posX,posY)                 creates circle on screen
trap(id,px,waveLen,focalLen)                sets up screen for a trap, points needs to be add!

exit()                                      To end program
undo()                                      To undo last command

"""