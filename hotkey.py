#coding=utf-8
'''
Created on 2010-10-12
@author: lxd
'''
import wx
import win32con
import time
import threading
import os

class WorkThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        
    def stop(self):
        self.timeToQuit.set()
    def run(self):
        while True:
            if not self.timeToQuit.isSet():
                print 'work'
                time.sleep(1)
            else:
                break
                        
class FrameWithHotKey(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.regHotKey()
        self.Bind(wx.EVT_HOTKEY, self.OnHotKeyStart, id=self.hotKeyId_start)
        self.Bind(wx.EVT_HOTKEY, self.OnHotKeyEnd, id=self.hotKeyId_end)
        self.Bind(wx.EVT_HOTKEY, self.OnHotKeyQuit, id=self.hotKeyId_quit)
        self.Bind(wx.EVT_HOTKEY, self.OnHotKeyOpen, id=self.hotKeyId_open)
        self.work = None
        
    def regHotKey(self):
        self.hotKeyId_start = 100
        self.RegisterHotKey(self.hotKeyId_start, win32con.MOD_ALT, win32con.VK_F1)
        self.hotKeyId_end = 101
        self.RegisterHotKey(self.hotKeyId_end, win32con.MOD_ALT, win32con.VK_F2)
        self.hotKeyId_quit = 102
        self.RegisterHotKey(self.hotKeyId_quit, win32con.MOD_ALT, win32con.VK_F3)
        self.hotKeyId_open = 103
        self.RegisterHotKey(self.hotKeyId_open, win32con.MOD_ALT, win32con.VK_F4)
                
    def OnHotKeyStart(self, evt):
        if not self.work:
            self.work = WorkThread()
            self.work.setDaemon(True)            
            self.work.start()
        
    def OnHotKeyEnd(self, evt):
        if self.work:
            self.work.stop()
            self.work = None
            
    def OnHotKeyQuit(self, evt):
        exit()
     
    def OnHotKeyOpen(self, evt):
        os.startfile("C:\Program Files\Tencent\QQ\Bin\QQ.exe")
        
app = wx.App()
FrameWithHotKey(None)
app.MainLoop()