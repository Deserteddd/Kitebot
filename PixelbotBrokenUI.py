import json
import time
import keyboard
import win32api, win32con
import datetime
from PIL import Image, ImageEnhance, ImageGrab
import os
import time
from tkinter import *
from PIL import ImageTk, Image


global debug
debug = False

class ValueTool:
    def __init__(self):
        with open("values.json") as f:
            self.values = json.load(f)
    
    def isclose(self, v1: float, v2: float, tolerance: float = 20):
        if type(v1) is tuple:
            v1 = v1[0]
        if type(v2) is tuple:
            v2 = v2[0]
        return abs(v1 - v2) <= tolerance
    
    def closestMatch(self, targetvalues: list):
        # initialize bestmatch as a tuple: index 0 is the current best guess and index 1 the number of matches in bestmatch
        bestmatch = (None, 0)

        # loop through all possible numbers and their values and compare targetvalues
        for key, valueslist in self.values.items():
            #at the start of loop init cmatches to 0
            currentmatches = 0

            #loop through current number values and compare to target
            for i in range(13):
                if self.isclose(valueslist[i], targetvalues[i], 20):
                    currentmatches += 1
            
            #if better than best assign as best and repeat
            if currentmatches >= bestmatch[1]:
                bestmatch = (int(key), currentmatches)

        #return bestmatch number
        return bestmatch[0]
    
    def img_to_guess(self, imag: Image.Image):
    
        #convert to grayscale
        image = imag.convert("L")
        
        #contrast
        imgcontr = ImageEnhance.Contrast(image).enhance(20)

        #crop to middle line
        croppedimg = imgcontr.crop((3, 0, 4, 13))

        #colorvalues to list
        imagevalues = []
        for i in range(13):
            imagevalues.append(croppedimg.getpixel((0, i)))
        #return guess
        return self.closestMatch(imagevalues)
    
    def as_getter(self):
        img1 = ImageGrab.grab((585, 1038, 592, 1051))
        img1.convert("L")
        n1 = self.img_to_guess(img1)

        img2 = ImageGrab.grab((595, 1038, 602, 1051))
        img2.convert("L")
        n2 = self.img_to_guess(img2)

        img3 = ImageGrab.grab((602, 1038, 609, 1051))
        img3.convert("L")
        n3 = self.img_to_guess(img3)

        attackspeed = float(f'{n1}.{n2}{n3}')
        if debug:
            return 2.5
        return attackspeed
    
    def totalwindup(self, bWinduptime, cAttackTime, WindupPercent, WindupModifier):
        return bWinduptime + ((cAttackTime * WindupPercent) - bWinduptime) * WindupModifier

class PixelBot:

    def __init__(self):

        self.ValueTool = ValueTool()

        with open("champstats.json") as f:
            self.champstats = json.load(f)

    def initVariables(self, stats):
        self.wu_Perc = stats[0]
        self.wu_Mod = stats[1]
        self.baseAS = stats[2]

        self.cAT = 1/self.ValueTool.as_getter()
        self.bWT = self.wu_Perc / self.baseAS

        self.totalWindup = self.ValueTool.totalwindup(self.bWT, self.cAT, self.wu_Perc, self.wu_Mod)

        self.lastUp = time.perf_counter()
        print(f"Champion: {self.champion.capitalize()}\n   Base attack speed: {self.baseAS}\n   Windup percent: {self.wu_Perc}\n   Windup modifier: {self.wu_Mod}")

    def setchampion(self, champion):
        if champion.lower() in [key.lower() for key in self.champstats.keys()]:
            self.champion = champion
            champstats = self.getstats(self.champion)
            self.initVariables(champstats)

    def getstats(self, champion: str):
        for key, value in self.champstats.items():
            if key.lower() == champion.lower():
                return value

    def clicker(self, timeadjust):
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP,0,0)
        # print("Attack move click\n\n")

        windupsleeptime = self.totalWindup + 0.075
        # print(f"Windup time: {windupsleeptime}")
        time.sleep(windupsleeptime) 


        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
        # print("Move click\n\n")

        attacktimersleeptime = self.cAT - self.totalWindup - 0.1 - timeadjust
        print(f"Remainder of attacktime: {attacktimersleeptime}")

        if attacktimersleeptime > 0:
            time.sleep(attacktimersleeptime)

    def updateAttacktime(self):
        self.cAT = 1/self.ValueTool.as_getter()
        self.totalWindup = self.ValueTool.totalwindup(self.bWT, self.cAT, self.wu_Perc, self.wu_Mod)

    def updatetimer(self, asUpdateFreq):
        self.timefromlastUp = time.perf_counter() - self.lastUp
        if self.timefromlastUp >= asUpdateFreq:
            print("Updated Attackspeed!")
            self.lastUp = time.perf_counter()
            return True
        return False


class UI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Christian Kiting")

        self.e = Entry(self.root, width=20)
        self.e.grid(row=8, column=6)

        self.scriptRunning = False

        self.buttoncreation()


    def start(self):
        self.scriptRunning = True

    def select(self, Champ):
        self.e.delete(0, END)
        self.e.insert(0, str(Champ))

    def select_new(self):
        self.scriptRunning = False

    def buttoncreation(self):
        self.buttons = {
        "Start" : Button(self.root, text="START", command=lambda: self.start(), width=20, height=2).grid(row=8, column=4),
        "Stop" : Button(self.root, text="Select new", command=lambda: self.select_new(), width=20, height=2).grid(row=8, column=5),
        "Akshan" : Button(self.root, text="Akshan", command=lambda: self.select('Akshan'), width=20, height=2).grid(row=2, column=2),
        "Aphelios" : Button(self.root, text="Aphelios", command=lambda: self.select('Aphelios'), width=20, height=2).grid(row=2, column=3),
        "Ashe" : Button(self.root, text="Ashe", command=lambda: self.select('Ashe'), width=20, height=2).grid(row=2, column=4),
        "Caitlyn" : Button(self.root, text="Caitlyn", command=lambda: self.select('Caitlyn'), width=20, height=2).grid(row=2, column=5),
        "Corki" : Button(self.root, text="Corki", command=lambda: self.select('Corki'), width=20, height=2).grid(row=2, column=6),
        "Draven" : Button(self.root, text="Draven", command=lambda: self.select('Draven'), width=20, height=2).grid(row=3, column=2),
        "Ezreal" : Button(self.root, text="Ezreal", command=lambda: self.select('Ezreal'), width=20, height=2).grid(row=3, column=3),
        "Gnar" : Button(self.root, text="Gnar", command=lambda: self.select('Gnar'), width=20, height=2).grid(row=3, column=4),
        "Graves" : Button(self.root, text="Graves", command=lambda: self.select('Graves'), width=20, height=2).grid(row=3, column=5), 
        "Jayce" : Button(self.root, text="Jayce", command=lambda: self.select('Jayce'), width=20, height=2).grid(row=3, column=6),
        "Jhin" : Button(self.root, text="Jhin", command=lambda: self.select('Jhin'), width=20, height=2).grid(row=4, column=2),
        "Jinx" : Button(self.root, text="Jinx", command=lambda: self.select('Jinx'), width=20, height=2).grid(row=4, column=3),
        "KaiSa" : Button(self.root, text="Kai'Sa", command=lambda: self.select("Kai'Sa"), width=20, height=2).grid(row=4, column=4),
        "Kalista" : Button(self.root, text="Kalista", command=lambda: self.select('Kalista'), width=20, height=2).grid(row=4, column=5),
        "Kayle" : Button(self.root, text="Kayle", command=lambda: self.select('Kayle'), width=20, height=2).grid(row=4, column=6),
        "Kennen" : Button(self.root, text="Kennen", command=lambda: self.select('Kennen'), width=20, height=2).grid(row=5, column=2),
        "Kindred" : Button(self.root, text="Kindred", command=lambda: self.select('Kindred'), width=20, height=2).grid(row=5, column=3),
        "KogMaw" : Button(self.root, text="Kog'Maw", command=lambda: self.select("Kog'Maw"), width=20, height=2).grid(row=5, column=4),
        "Lucian" : Button(self.root, text="Lucian", command=lambda: self.select('Lucian'), width=20, height=2).grid(row=5, column=5),
        "MissFortune" : Button(self.root, text="Miss Fortune", command=lambda: self.select('Miss Fortune'), width=20, height=2).grid(row=5, column=6),
        "Quinn" : Button(self.root, text="Quinn", command=lambda: self.select('Quinn'), width=20, height=2).grid(row=6, column=2),
        "Samira" : Button(self.root, text="Samira", command=lambda: self.select('Samira'), width=20, height=2).grid(row=6, column=3),
        "Senna" : Button(self.root, text="Senna", command=lambda: self.select('Senna'), width=20, height=2).grid(row=6, column=4),
        "Sivir" : Button(self.root, text="Sivir", command=lambda: self.select('Sivir'), width=20, height=2).grid(row=6, column=5),
        "Teemo" : Button(self.root, text="Devil", command=lambda: self.select('Teemo'), width=20, height=2).grid(row=6, column=6),
        "Tristana" : Button(self.root, text="Tristana", command=lambda: self.select('Tristana'), width=20, height=2).grid(row=7, column=2),
        "TwistedFate" : Button(self.root, text="Twisted Fate", command=lambda: self.select('Twisted Fate'), width=20, height=2).grid(row=7, column=3),
        "Twitch" : Button(self.root, text="Twitch", command=lambda: self.select('Twitch'), width=20, height=2).grid(row=7, column=4),
        "Varus" : Button(self.root, text="Varus", command=lambda: self.select('Varus'), width=20, height=2).grid(row=7, column=5),
        "Vayne" : Button(self.root, text="Vayne", command=lambda: self.select('Vayne'), width=20, height=2).grid(row=7, column=6),
        "Xayah" : Button(self.root, text="Xayah", command=lambda: self.select('Xayah'), width=20, height=2).grid(row=8, column=2),
        "Zeri" : Button(self.root, text="Zeri", command=lambda: self.select('Zeri'), width=20, height=2).grid(row=8, column=3),
        }

class Program:
    def __init__(self):
        self.UI = UI()
        self.PixelBot = PixelBot()
        self.run()

    
    def scan_active(self):
        return keyboard.is_pressed("space")

    def run(self):
        self.ButtonlastTickvalue = "init"
        while True:
            self.UI.root.update_idletasks()
            self.UI.root.update()

            if self.UI.scriptRunning:
                if self.scan_active():

                    timerstart = time.perf_counter()
                    if self.PixelBot.updatetimer(1):
                        self.PixelBot.updateAttacktime()

                    timediff = time.perf_counter() - timerstart


                    self.PixelBot.clicker(0)


            if not self.UI.scriptRunning:
                if self.UI.e.get() != self.ButtonlastTickvalue:
                    self.PixelBot.setchampion(self.UI.e.get())

                self.ButtonlastTickvalue = self.UI.e.get()



Program()




