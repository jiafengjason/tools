#!/usr/bin/env python
#-*-coding:utf-8 -*-

import sys
import os
import time 
import pyautogui
import pyperclip
import datetime
import json
import math
from skimage.measure import compare_ssim
import cv2
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

SID=0
LDFolder = 'LD2'
stat = {}
if os.path.exists('stat.json'):
    jsObj = open('stat.json').read()
    stat = json.loads(jsObj)

width, height = pyautogui.size()
print('Current width:%s, height:%s' % (width, height))

def pos():
    x, y = pyautogui.position()
    print('Point x:%s, y:%s' % (x, y))

def saveJson(data,jsFile):
    jsObj = json.dumps(data,ensure_ascii=False)
    fileObj = open(jsFile, 'w')
    fileObj.write(jsObj)
    fileObj.close()

def findAllPics(image,expect,cfd=0.7):
    timeout = 1
    while 1:
        points = []
        count = 0
        for location in pyautogui.locateAllOnScreen(image, grayscale=True, confidence=cfd):
            count+=1
            x,y = pyautogui.center(location)
            similar = False
            if points:
                for point in points:
                    if abs(point[0]-x)<10 and abs(point[1]-y)<10:
                        similar = True
                        break
            if not similar:
                points.append((x,y))
        if timeout>1:
            time.sleep(1)
        if len(points)==expect:
            break
    print(points)
    print("Total:%s, filter:%s" % (count, len(points)))
    return points

def findPic(image,timeout=3,cfd=0.7):
    starttime = datetime.datetime.now()
    for i in range(timeout):
        location = pyautogui.locateOnScreen(image, grayscale=True, confidence=cfd)
        if location:
            endtime = datetime.datetime.now()
            duration = (endtime - starttime).microseconds/1000
            print('Find image %s duration:%s' % (image,duration))
            return location
        if timeout>1:
            time.sleep(1)
    print("Can't find %s" % image)
    return None

def click(location,double=1):
    if not location:
        return
    xPoint,yPoint = pyautogui.center(location)
    print("Click (%s,%s)" % (xPoint,yPoint))
    pyautogui.click(x=xPoint,y=yPoint,clicks=double)
    return xPoint,yPoint

def startLD():
    location=findPic('ld.jpg')
    click(location,2)

def startVM(id):
    location=findPic(os.path.join(LDFolder,'lddkq.jpg'),cfd=0.5)
    if not location:
        startLD()
        location=findPic(os.path.join(LDFolder,'lddkq.jpg'),cfd=0.5)
    pyautogui.click(location)
    '''
    for id in range(37):
        imageFile = os.path.join('num','%s.jpg' % id)
        location = findPic(imageFile,1,0.99)
        print('%s:%s' % (id,location))
    '''
    imageFile = os.path.join(LDFolder,'%s.jpg' % id)
    
    step = 300
    while 1:
        location = findPic(imageFile,1,0.99)
        if location:
            x,y = pyautogui.center(location)
            #pyautogui.click(x+324,y)
            pyautogui.click(x+370,y)
            print("Start VM%s" % (id))
            break
        for i in range(0,50,5):
            imagei = os.path.join(LDFolder,'%s.jpg' % i)
            locationi = findPic(imagei,1,0.99)
            if locationi:
                if id>i:
                    pyautogui.scroll(0-step)
                else:
                    pyautogui.scroll(step)
                break

def closeVM():
    location=findPic(os.path.join(LDFolder,'close.jpg'),3,0.9)
    click(location)
    location = findPic(os.path.join(LDFolder,'logo.jpg'),1,0.9)
    if location:
        location=findPic(os.path.join(LDFolder,'close.jpg'),3,0.9)
        click(location)

def startAPP(appName):
    imageFile = os.path.join('APP','%s.jpg' % appName)
    location=findPic(imageFile,100)
    click(location)

def returnHome():
    while 1:
        pyautogui.press('esc')
        if findPic(os.path.join('APP','GAME.jpg'),1):
            break

def clean():
    location=findPic('switch.jpg')
    click(location)
    location=findPic('clean.jpg')
    click(location)

def getJson(node, count, rev=False):
    if os.path.exists('config.json'):
        jsObj = open('config.json').read()
        config = json.loads(jsObj)
        dic = config[node]
        if not os.path.exists('stat.json'):
            for key in dic.keys():
                stat[key] = 0
        if not stat:
            print("sys.exit()")
            sys.exit()
        for item in sorted(stat.items(), key=lambda stat: stat[1], reverse = rev):
            name = item[0]
            if item[1]<count:
                yield name,dic[name]

def test():
    while 1:
        print('.')
        sys.exit()
    '''
    while 1:
        startAPP('JR')
        time.sleep(1)
        returnHome()
    
    for id in range(41):
        startVM(id)
    
    for point in findAllPics(os.path.join('QQ','coin.jpg'),1,0.9):
        pyautogui.moveTo(point[0],point[1])
        print(point[0],point[1])
    '''
    
def cakes():
    sucCount = 0
    cannot = False
    
    allVMs = list(range(14,39))
    if 30 in allVMs:
        allVMs.remove(30)
    if 23 in allVMs:
        allVMs.remove(23)
    for id in allVMs:
        startVM(id)
        cake()
        #closeVM()

def cake():
    sucCount = 0
    items = getJson('cake',10)
    while 1:
        try:
            name,line = next(items)
        except:
            break
        print(name,line)
        #pyautogui.hotkey('ctrl', 'v')
        imageFile = os.path.join('APP','JD.jpg')
        location=findPic(imageFile,100)
        if location:
            pyperclip.copy(line)
        startAPP('JD')
        location=findPic(os.path.join('JD','view.jpg'),100)
        click(location)
        while 1:
            location=findPic(os.path.join('JD','help.jpg'),1)
            if location:
                click(location)
                location=findPic(os.path.join('JD','success.jpg'))
                if location:
                    click(location)
                    sucCount+=1
                    stat[name] += 1
                    saveJson(stat, 'stat.json')
                    print('sucCount:%s' % sucCount)
                else:
                    print('Fail')
                break
            location=findPic(os.path.join('JD','cannot.jpg'),1)
            if location:
                pyautogui.press('f1')
                break
            time.sleep(1)
        if sucCount>=5:
            break
        else:
            pyautogui.press('f1')

def zd():
    sucCount = 0
    cannot = False
    
    allVMs = list(range(14,43))
    if 30 in allVMs:
        allVMs.remove(30)
    if 23 in allVMs:
        allVMs.remove(23)
    for id in allVMs:
        startVM(id)
        sucCount = 0
        items = getJson('zd',20)
        while 1:
            try:
                name,line = next(items)
            except:
                closeVM()
                break
            print(name,line)
            pyperclip.copy(line)
            #pyautogui.hotkey('ctrl', 'v')
            startAPP('JD')
            location=findPic(os.path.join('JD','view.jpg'),100)
            click(location)
            for i in range(10):
                location=findPic(os.path.join('JD','success2.jpg'),1,0.9)
                if location:
                    click(location)
                    sucCount+=1
                    stat[name] += 1
                    saveJson(stat, 'stat.json')
                    print('sucCount:%s' % sucCount)
                    break
                if findPic(os.path.join('JD','finish.jpg'),1):
                    del stat[name]
                    saveJson(stat, 'stat.json')
                    break
                if findPic(os.path.join('JD','limit.jpg'),1):
                    sucCount = 3
                    break
                time.sleep(1)
            
            returnHome()
            
            #pyautogui.press('f1')
            if sucCount>=3:
                closeVM()
                break
        print(stat)

def coin():
    allVMs = list(range(27,38))
    
    for id in allVMs:
        startVM(id)
        startAPP('QQ')
        time.sleep(30)
        location=findPic(os.path.join('QQ','dd.jpg'),100)
        if location:
            click(location)
            time.sleep(8)
            sucCount = 0
            while 1:
                for point in findAllPics(os.path.join('QQ','coin.jpg'),3):
                    #pyautogui.moveTo(point[0],point[1])
                    print(point[0],point[1])
                    for i in range(3):
                        pyautogui.click(point[0],point[1])
                        location=findPic(os.path.join('QQ','success.jpg'),30)
                        if location:
                            sucCount+=1
                            print('sucCount:%s' % sucCount)
                            pyautogui.press('esc')
                            time.sleep(1)
                            break
                        pyautogui.press('esc')
                        time.sleep(1)
                if sucCount>=1:
                    closeVM()
                    break
    '''
    for i in range(5):
        pyautogui.scroll(200)
        time.sleep(1)
    
    sucCount = 0
    while 1:
        for location in pyautogui.locateAllOnScreen('jx.jpg', grayscale=True, confidence=0.62):
            click(location)
            for i in range(10):
                location=findPic('jx_success.jpg',1)
                if location:
                    sucCount+=1
                    break
                location=findPic('jxnc.jpg',1)
                if location:
                    sucCount+=1
                    break
                time.sleep(1)
            pyautogui.press('esc')
        for i in range(10):
            pyautogui.scroll(200)
            time.sleep(1)
        if sucCount>=6:
            break
    #location=findPic('jx_success.jpg',10)
    #location=findPic('jxnc.jpg',10)
    '''
    
def jt():
    allVMs = list(range(21,43))
    if 9 in allVMs:
        allVMs.remove(9)
    if 10 in allVMs:
        allVMs.remove(10)
    sucCount = 0
    for id in allVMs:
        startVM(id)
        sucCount = 0
        items = getJson('jt',100)
        while 1:
            try:
                name,line = next(items)
            except:
                closeVM()
                break
            print(name,line)
            pyperclip.copy(line)
            startAPP('JR')
            location=findPic(os.path.join('JR','join.jpg'),100)
            click(location)
            
            for i in range(15):
                location=findPic(os.path.join('JR','open.jpg'),1)
                if location:
                    click(location)
                    location=findPic(os.path.join('JR','view.jpg'),5)
                    if location:
                        sucCount+=1
                        if name not in stat:
                            stat[name] = 0
                        stat[name] += 1
                        saveJson(stat, 'stat.json')
                        break
                time.sleep(1)
            if sucCount>=3:
                closeVM()
                break
            
            returnHome()
        print(stat)

def yjt():
    allVMs = list(range(2,37))
    if 30 in allVMs:
        allVMs.remove(30)
    if 7 in allVMs:
        allVMs.remove(7)
    
    for id in allVMs:
        startVM(id)
        sucCount = 0
        items = getJson('yjt',12)
        while 1:
            try:
                name,line = next(items)
            except:
                closeVM()
                break
            print(name,line)
            pyperclip.copy(line)
            startAPP('JR')
            location=findPic(os.path.join('JR','viewdetail.jpg'),100)
            click(location)
            for i in range(10):
                location=findPic(os.path.join('JR','success.jpg'),1)
                if location:
                    sucCount+=1
                    if name not in stat:
                        stat[name] = 0
                    stat[name] += 1
                    saveJson(stat, 'stat.json')
                    break
                location=findPic(os.path.join('JR','fail.jpg'),1)
                if location:
                    sucCount = 2
                    break
                location=findPic(os.path.join('JR','limit.jpg'),1)
                if location:
                    sucCount = 2
                    break
                time.sleep(1)
            if sucCount>=1:
                closeVM()
                break
            pyautogui.press('f1')
        print(stat)

def fruit():
    allVMs = list(range(1,43))
    #allVMs.reverse()
    if 9 in allVMs:
        allVMs.remove(9)
    if 10 in allVMs:
        allVMs.remove(10)
    if 23 in allVMs:
        allVMs.remove(23)
    for id in allVMs:
        startVM(id)
        sucCount = 0
        items = getJson('fruit',50)
        while 1:
            try:
                name,line = next(items)
            except:
                closeVM()
                break
            print(name,line)
            pyperclip.copy(line)
            startAPP('JX')
            while 1:
                location=findPic(os.path.join('JX','view.jpg'),1)
                if location:
                    break
                else:
                    location=findPic(os.path.join('JX','view2.jpg'),1)
                    if location:
                        break
                    else:
                        time.sleep(1)
                        continue
            click(location)
            for i in range(15):
                if findPic(os.path.join('JX','finish.jpg'),1) or findPic(os.path.join('JX','finish1.jpg'),1) or findPic(os.path.join('JX','finish2.jpg'),1) or findPic(os.path.join('JX','finish3.jpg'),1):
                    del stat[name]
                    saveJson(stat, 'stat.json')
                    break
                if findPic(os.path.join('JX','limit.jpg'),1):
                    suc2Count = 3
                    break
                if findPic(os.path.join('JX','limit2.jpg'),1):
                    break
                if findPic(os.path.join('JX','success.jpg'),1) or findPic(os.path.join('JX','success2.jpg'),1) or findPic(os.path.join('JX','success3.jpg'),1):
                    sucCount+=1
                    '''
                    if '1' in name:
                        suc1Count+=1
                    if '2' in name:
                        suc2Count+=1
                    print('suc1Count:%s, suc2Count:%s,' % (suc1Count,suc2Count))
                    '''
                    print('sucCount:%s' % (sucCount))
                    stat[name] += 1
                    saveJson(stat, 'stat.json')
                    break
                time.sleep(1)
            if sucCount>=3:
                closeVM()
                break
            returnHome()
        print(stat)

def island():
    if SID==0 and os.path.exists('stat.json'):
        os.remove('stat.json')
    allVMs = list(range(1,43))
    if 9 in allVMs:
        allVMs.remove(9)
    if 10 in allVMs:
        allVMs.remove(10)
    if 23 in allVMs:
        allVMs.remove(23)
    allVMs.reverse()
    for id in allVMs:
        if id<SID:
            continue
        startVM(id)
        sucCount = 0
        items = getJson('island',50, True)
        while 1:
            try:
                name,line = next(items)
            except:
                closeVM()
                break
            print(name,line)
            pyperclip.copy(line)
            startAPP('JX')
            while 1:
                location=findPic(os.path.join('JX','view.jpg'),1)
                if location:
                    break
                else:
                    location=findPic(os.path.join('JX','view2.jpg'),1)
                    if location:
                        break
                    else:
                        time.sleep(1)
                        continue
            click(location)
            for i in range(15):
                if findPic(os.path.join('JX','island_success.jpg'),1):
                    sucCount+=1
                    print('sucCount:%s' % sucCount)
                    stat[name] += 1
                    saveJson(stat, 'stat.json')
                    break
                if findPic(os.path.join('JX','island_finish.jpg'),1):
                    del stat[name]
                    saveJson(stat, 'stat.json')
                    break
                time.sleep(1)
            if sucCount>=1:
                closeVM()
                break
            returnHome()
        print(stat)
        
def tt():
    if SID==0 and os.path.exists('stat.json'):
        os.remove('stat.json')
    allVMs = list(range(1,9))+list(range(14,43))
    if 23 in allVMs:
        allVMs.remove(23)
    for id in allVMs:
        if id<SID:
            continue
        startVM(id)
        sucCount = 0
        items = getJson('tt',33)
        while 1:
            try:
                name,line = next(items)
            except:
                closeVM()
                break
            print(name,line)
            pyperclip.copy(line)
            startAPP('JS')
            location=findPic(os.path.join('JS','view.jpg'),100)
            click(location)
            while 1:
                location=findPic(os.path.join('JS','finish.jpg'),1)
                if location:
                    del stat[name]
                    saveJson(stat, 'stat.json')
                    break
                location=findPic(os.path.join('JS','cannot.jpg'),1)
                if location:
                    returnHome()
                    break
                location=findPic(os.path.join('JS','help.jpg'),1)
                if location:
                    click(location)
                    location=findPic(os.path.join('JS','success.jpg'),10)
                    if location:
                        click(location)
                        sucCount+=1
                        stat[name] += 1
                        saveJson(stat, 'stat.json')
                        print('sucCount:%s' % sucCount)
                        break
                time.sleep(1)
            if sucCount>=3:
                closeVM()
                break
            returnHome()
            print(stat)

def wx():
    allVMs = list(range(25,42))
    allVMs.append(13)
    allVMs.append(14)
    allVMs.remove(26)
    allVMs.remove(30)
    allVMs.remove(31)
    allVMs.remove(38)
    allVMs.sort()
    for id in allVMs:
        startVM(id)
        startAPP('WX')
        time.sleep(60)
        closeVM()

def compare_image(path_image1, path_image2):
    imageA = cv2.imread(path_image1)
    imageB = cv2.imread(path_image2)

    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    (score, diff) = compare_ssim(grayA, grayB, full=True)
    print("SSIM: {}".format(score))
    return score

if __name__ == '__main__':
    if len(sys.argv)<2:
        sys.exit()
    else:
        args = sys.argv[2:]
        if len(sys.argv)>2:
            SID=int(sys.argv[2])
            args = sys.argv[3:]
        func = eval(sys.argv[1])
        func(*args)
