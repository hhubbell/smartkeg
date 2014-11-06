#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         gui.py
# Purpose:      Display info from the SmartKeg database live.
#
# Author:       Christopher Young
# Created:      11/1/14
#----------------------------------------------------------------------------

# import the wxPython GUI package
import os
import wx
import pprint
import random
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar




class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1000,600))
        #self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar() # A StatusBar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About","Get some info")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit", "Quit the GUI")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        
        #panel additions
        titlePanel = wx.Panel(self)
        titlePanel.SetBackgroundColour((10,110,186))                #blue
        
        titleText= wx.StaticText(titlePanel, label = "SmartKeg")    #make text
        titleFont = wx.Font(120, wx.SWISS, wx.SLANT, wx.LIGHT)      #create font
        titleText.SetFont(titleFont)                                #add font to text
        titleText.SetForegroundColour((255,247,0))                  #yellow
        
        #self.quote = titleText                                      #show text

        self.Show(True)

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Welcome to the future of beverage consumption.", "About SmartKeg", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

app = wx.App(False)
frame = MainWindow(None, "Welcome to SmartKeg")
app.MainLoop()