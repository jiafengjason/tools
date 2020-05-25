#!/usr/bin/env python
#-*-coding:utf-8 -*-

import sys
import os
import time 
import pyautogui
import pyperclip
import datetime

from PIL import Image
import timeit
  
 
def to_position(file_name2):
    # 系统找图速率做对比
    res = pyautogui.locateCenterOnScreen(file_name2)
 
def get_position(small,big):
    """
    传入需要获得坐标的小图路径
    返回值为空表示没找到
    """
 
    im1 = Image.open(big)
    im2 = Image.open(small)
    pix1 = im1.load()
    pix2 = im2.load()
    width1 = im1.size[0]
    height1 = im1.size[1]
    width2 = im2.size[0]
    height2 = im2.size[1]
 
    rgb2 = pix2[0, 0][:3]  # 左上角起始点
    for x in range(width1):
        for y in range(height1):
            rgb1 = pix1[x, y][:3]
            if rgb1 == rgb2:
                # 判断剩下的点是否相同
                status = 0
                # 图二的坐标是(s, j) --- (s-x, j-y)
                for s in range(x, x + width2):
                    for j in range(y, y + height2):
                        # 设置阈值范围
                        if abs(pix2[s-x,j-y][0]-pix1[s,j][0]) > 60 and  abs(pix2[s-x,j-y][1]-pix1[s,j][:3][1]) > 60 and abs(pix2[s-x,j-y][1]-pix1[s,j][:3][1]) > 60:
                            status = 1
                if status:
                    continue
                else:
                    return x + round(0.5 * width2), y + round(0.5 * height2)

#pyautogui.PAUSE = 1.5
pyautogui.FAILSAFE = True

pyautogui.moveTo((59,105))
pyautogui.click()
pyperclip.copy('test')
pyautogui.hotkey('ctrl', 'v')
for i in range(10):
      pyautogui.moveTo(300, 300, duration=0.25)
      pyautogui.moveTo(400, 300, duration=0.25)
      pyautogui.moveTo(400, 400, duration=0.25)
      pyautogui.moveTo(300, 400, duration=0.25)
      
pyautogui.size()
# (1400, 900)
width, height = pyautogui.size()
print width, height

x, y = pyautogui.position()
print x, y
'''
im = pyautogui.screenshot()
print im
# 获得某个坐标的像素
im.getpixel((50, 200))
# (30, 132, 153)
 
# 判断屏幕坐标的像素是不是等于某个值
print pyautogui.pixelMatchesColor(50, 200, (30, 132, 153))
# True

pyautogui.moveTo((59,105),duration=2)
pyautogui.click()
pyautogui.typewrite('https://wwww.baidu.com')
pyautogui.keyDown('shift');pyautogui.press('4');pyautogui.keyUp('shift')
pyautogui.screenshot('all.png')

pyautogui.locateOnScreen('vnc.png', region=(600,5,180,120))
'''
starttime = datetime.datetime.now()
while 1:
    vnclocation = pyautogui.locateOnScreen('vnc.jpg', grayscale=True, confidence=0.9)
    if vnclocation:
        break
    time.sleep(1)
endtime = datetime.datetime.now()
print (endtime - starttime).microseconds/1000
print vnclocation
vncx,vncy = pyautogui.center(vnclocation)
print vncx,vncy

starttime = datetime.datetime.now()
vnclocation = pyautogui.locateOnScreen('7.jpg', grayscale=True, confidence=0.9)
endtime = datetime.datetime.now()
print (endtime - starttime).microseconds/1000
print vnclocation
vncx,vncy = pyautogui.center(vnclocation)
print vncx,vncy

pyautogui.alert(text='1', title='2', button='OK')
#pyautogui.doubleClick(vncx,vncy)

#print get_position('all.png','vnc.png')
#print get_position('7.jpg','all.png')
#print get_position('yellow7.jpg','all.png')

#x, y = pyautogui.center((643, 745, 70, 29))  # 获得中心点
#pyautogui.click(x, y)

#pyautogui.scroll(-2000)

#pyautogui.click(867, 14, button='left')

'''
for i in range(10):
    pyautogui.moveTo(300, 300, duration=0.25)
    pyautogui.moveTo(400, 300, duration=0.25)
    pyautogui.moveTo(400, 400, duration=0.25)
    pyautogui.moveTo(300, 400, duration=0.25)
'''
