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
import subprocess
from skimage.measure import compare_ssim
import cv2
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

SID=0
EID=67
LDFolder = 'LD4'
TaskStat = {}
VmStat = {}
Config = {}
LDConsle = "J:\leidian\ldconsole.exe"
APPS = {
    "QQ" : "com.tencent.mobileqq",
    "WX" : "com.tencent.mm",
    "JD" : "com.jingdong.app.mall",
    "JR" : "com.jd.jrapp",
    "JS" : "com.jd.jdlite",
    "JX" : "com.jd.pingou",
    "SN" : "com.suning.mobile.ebuy"
}

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

def cleanStat():
    if os.path.exists('taskStat.json'):
        os.remove('taskStat.json')
    if os.path.exists('vmStat.json'):
        os.remove('vmStat.json')
    TaskStat = {}
    VmStat = {}

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
    start = time.time()
    for i in range(timeout):
        location = pyautogui.locateOnScreen(image, grayscale=True, confidence=cfd)
        if location:
            end = time.time()
            duration = end - start
            print('Find image %s duration:%s' % (image,duration))
            return location
        if timeout>1:
            time.sleep(0.5)
    print("Can't find %s" % image)
    return None

def click(location,double=1):
    if not location:
        return
    xPoint,yPoint = pyautogui.center(location)
    print("Click (%s,%s)" % (xPoint,yPoint))
    pyautogui.click(x=xPoint,y=yPoint,clicks=double)
    return xPoint,yPoint

def clickPic(image,timeout=3,cfd=0.7,double=1):
    location = findPic(image,timeout,cfd)
    return click(location)

def inAndroid(id):
    cmd = "%s list2" % (LDConsle)
    #print(cmd)
    p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    out,err = p.communicate()
    sp = out.splitlines()
    #print(sp[id])
    if id>=len(sp):
        print(id, len(sp))
        return 0
    line = sp[id]
    #print(line)
    flag = str(line,'gb2312').split(",")[4]
    return int(flag)

def createVM(id):
    os.system("%s add" % (LDConsle))

def newVM():
    cmd = "%s list2" % (LDConsle)
    p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    out,err = p.communicate()
    sp = out.splitlines()
    id = len(sp)
    
    createVM(id)
    startVM(id)
    for appName,packagename in APPS.items():
        installApp(id, appName)

def startVM(id):
    os.system("%s launch --index %d" % (LDConsle, id))
    while 1:
        flag=inAndroid(id)
        if flag:
            break
        time.sleep(0.5)

def closeVM(id):
    os.system("%s quit --index %d" % (LDConsle, id))

def rebootVM(id):
    os.system("%s reboot --index %d" % (LDConsle, id))

def closeAllVM():
    os.system("%s quitall" % (LDConsle))

def runApp(id, appName):
    os.system("%s runapp --index %d --packagename %s" % (LDConsle, id, APPS[appName]))

def killApp(id, appName):
    os.system("%s killapp --index %d --packagename %s" % (LDConsle, id, APPS[appName]))

def installApp(id, appName):
    os.system("%s installapp --index %d --filename apk/%s.apk" % (LDConsle, id, appName))

def returnHome(id, appName):
    '''
    os.system("%s action --index %d --key call.keyboard --value home" % (LDConsle, id))
    if findPic(os.path.join('APP','GAME.jpg'),1):
        break
    '''
    waitTime = 10
    isKill = False
    isReboot = False
    start = time.time()
    while 1:
        end = time.time()
        duration = end - start
        print(duration)
        if (not isKill) and (not isReboot):
            os.system("%s action --index %d --key call.keyboard --value back" % (LDConsle, id))
            #pyautogui.press('esc')
        if (not isKill) and duration>10:
            print("killApp %s" % appName)
            killApp(id, appName)
            waitTime = 60
            isKill = True
            start = time.time()
        elif isKill and (not isReboot) and duration>10:
            print("rebootVM %s" % appName)
            rebootVM(id)
            waitTime = 60
            isReboot = True
            start = time.time()
        if findPic(os.path.join('APP','GAME.jpg'),1):
            break

    return waitTime

def clean():
    location=findPic(os.path.join(LDFolder,'switch.jpg'))
    click(location)
    location=findPic(os.path.join(LDFolder,'clean.jpg'))
    click(location)

def tokenIter(task, id, count=100, rev=False):
    dic =  Config[task]
    if not os.path.exists('taskStat.json'):
        for key in dic.keys():
            TaskStat[key] = 0
        saveJson(TaskStat, 'taskStat.json')
    print(TaskStat)
    if id not in VmStat:
        VmStat[id] = {}
        for key in dic.keys():
            VmStat[id][key] = 0
        saveJson(VmStat, 'vmStat.json')
    for item in sorted(TaskStat.items(), key=lambda TaskStat: TaskStat[1], reverse = rev):
        name = item[0]
        if item[1]<count and VmStat[id][name]==0:
            yield name,dic[name]
        elif item[1]>=count:
            if name in TaskStat:
                del TaskStat[name]
                saveJson(TaskStat, 'taskStat.json')

def picIter(pics):
    count = 0
    while 1:
        index = count%len(pics)
        yield pics[index]
        count += 1
        
def failIter(task, id):
    for name,suc in VmStat[id].items():
        if name in TaskStat and not suc:
            yield name, Config[task][name]

def getList(app, reverse=False):
    allIds = []
    if app=="JD":
        allIds = list(range(13,EID)) + [2, 5]
        removeIds = [23, 43, 53]
    if app=="JS":
        allIds = list(range(2,10))+list(range(14,EID))
        removeIds = [3, 4, 6, 7, 8, 23, 27, 29, 43, 47, 53]
    if app=="JR":
        allIds = list(range(2,EID))
        removeIds = [10, 27, 43]
    if app=="JX":
        allIds = list(range(7,53))
        removeIds = [9, 10, 23, 34, 38] + list(range(41,44))
    allIds = list(set(allIds) - set(removeIds))
    allIds = [id for id in allIds if id>=SID]
    allIds.sort()
    if reverse:
        allIds.reverse()
    print(allIds)
    return allIds

def template(appName, task, pics, maxHitCount=100, maxHelpCount=3, rev=False):
    allVMs = getList(appName, rev)
    
    for id in allVMs:
        waitTime = 60
        limit = 0
        firstLoad = True
        startVM(id)
        items = tokenIter(task, id, maxHitCount, rev)
        failItems = failIter(task, id)
        while 1:
            try:
                name,line = next(items)
            except StopIteration:
                try:
                    name,line = next(failItems)
                except StopIteration:
                    closeVM(id)
                    break
            print(name,line)
            if findPic(os.path.join(LDFolder, "error.jpg"),1):
                location=findPic(os.path.join(LDFolder, "ok.jpg"),1)
                if location:
                    click(location)
            pyperclip.copy(line)
            runApp(id, appName)
            start = time.time()
            location = None
            while not location:
                end = time.time()
                duration = end - start
                print("duration:%d(%d)" % (duration,firstLoad))
                if duration>waitTime:
                    pyperclip.copy(line)
                    waitTime = returnHome(id, appName)
                    start = time.time()
                    runApp(id, appName)
                location=findPic(os.path.join(appName,pics['view']),1)
                if location:
                    waitTime = 10
                    start = time.time()
                    break
                if 'update' in pics:
                    updateLocation = findPic(os.path.join(appName,pics['update']),1)
                    if updateLocation:
                        click(updateLocation)
                time.sleep(0.5)
            click(location)
            if 'help' in pics:
                for i in range(10):
                    location=findPic(os.path.join(appName,pics['help']))
                    if location:
                        click(location)
                        break
            isSuc = False
            for i in range(25):
                if isinstance(pics['success'],str):
                    if findPic(os.path.join(appName,pics['success']),1):
                        if name in TaskStat:
                            TaskStat[name] += 1
                        VmStat[id][name]=1
                        break
                elif isinstance(pics['success'],list):
                    for pic in pics['success']:
                        if findPic(os.path.join(appName,pic),1):
                            if name in TaskStat:
                                TaskStat[name] += 1
                            VmStat[id][name]=1
                            isSuc = True
                            break
                    if isSuc:
                        break
                if 'finish' in pics:
                    if findPic(os.path.join(appName,pics['finish']),1):
                        if name in TaskStat:
                            del TaskStat[name]
                        break
                if 'limit' in pics:
                    if findPic(os.path.join(appName,pics['limit']),1):
                        limit = 1
                        break
                time.sleep(0.5)
            else:
                VmStat[id][name]=0
            print(TaskStat)
            sucCount = list(VmStat[id].values()).count(1)
            print('sucCount:%s' % sucCount)
            saveJson(TaskStat, 'taskStat.json')
            saveJson(VmStat, 'vmStat.json')
            if sucCount>=maxHelpCount or limit:
                closeVM(id)
                break
            returnHome(id, appName)
        
        closeVM(id)
        print(VmStat)
        if not TaskStat:
            break
    closeAllVM()

def tx():
    #pics = ['ktx.jpg', 'wxlq.jpg', 'ty.jpg', 'wzdl.jpg']
    pics = ['ktx.jpg', 'wxlq.jpg', 'wzdl.jpg']
    it = picIter(pics)
    pic = next(it)
    while 1:
        location=findPic(os.path.join('JD',pic),1)
        if location:
            print(pic)
            click(location)
            pic = next(it)
        time.sleep(0.5)

def test():
    returnHome(1, "JD")

def batch():
    island()
    cleanStat()
    lxj()
    cleanStat()
    qm()

#种豆
def zd():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['success'] = 'success2.jpg'
    pics['finish'] = 'finish.jpg'
    pics['limit'] = 'limit.jpg'
    template('JD', 'zd', pics, 9)

def qm():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['success'] = ['qm_success.jpg', 'qm_success1.jpg']
    template('JD', 'qm', pics, 58, 2)

def lxj():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'lxj_help.jpg'
    pics['success'] = 'lxj_success.jpg'
    #pics['finish'] = 'lxj_finish.jpg'
    template('JD', 'lxj', pics, 100, 3)
    
def wxj():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['success'] = ['wxj_success.jpg', 'wxj_success1.jpg']
    template('JD', 'wxj', pics, 21, 1)

def ysq():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['success'] = 'ysq_success.jpg'
    template('JD', 'ysq', pics, 29, 1, True)

#炸年兽
def zns():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'zns_help.jpg'
    pics['success'] = 'zns_success.jpg'
    pics['finish'] = 'zns_finish.jpg'
    template('JD', 'zns', pics, 10)

#守护
def sh():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'zns_help.jpg'
    pics['success'] = 'zns_success.jpg'
    pics['finish'] = 'zns_finish.jpg'
    template('JD', 'sh', pics, 100, 5)

#城城
def fxj():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['success'] = ['fxj_success.jpg', 'fxj_success1.jpg']
    template('JD', 'fxj', pics, 50, 3)

#打工
def dg():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'help.jpg'
    pics['success'] = ['dg_success.jpg', 'dg_success1.jpg']
    pics['finish'] = 'dg_finish.jpg'
    template('JX', 'dg', pics, 5, 1)

#招工
def zg():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['update'] = 'update.jpg'
    pics['success'] = ['zg_success.jpg', 'zg_success1.jpg']
    template('JX', 'zg', pics)
    
#财富岛
def island():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['update'] = 'update.jpg'
    pics['success'] = 'island_success.jpg'
    pics['finish'] = 'island_finish.jpg'
    template('JX', 'island', pics, 100, 1)

def ttN():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'help.jpg'
    pics['finish'] = 'finish.jpg'
    pics['success'] = 'success.jpg'
    template('JS', 'tt', pics)
    
def tt():
    '''
    for id in [11,12,13]:
        startVM(id)
        runApp('JS')
        location=findPic(os.path.join('JS','ttzq.jpg'),20)
        if location:
            click(location)
            location=findPic(os.path.join('JS','lktb.jpg'),20)
            if location:
                click(location)
                location=findPic(os.path.join('JS','lktb.jpg'),20)
                if location:
                    pyautogui.press('esc')
                    closeVM(id)
    '''
    allVMs = getList("JS")
    
    for id in allVMs:
        startVM(id)
        items = tokenIter('tt', id, 100)
        failItems = failIter('tt',id)
        while 1:
            try:
                name,line = next(items)
            except StopIteration:
                try:
                    name,line = next(failItems)
                except StopIteration:
                    closeVM(id)
                    break
            print(name,line)
            pyperclip.copy(line)
            runApp(id, 'JS')
            location=findPic(os.path.join('JS','view.jpg'),100)
            while not location:
                pyperclip.copy(line)
                returnHome(id, "JS")
                runApp(id, 'JS')
                location=findPic(os.path.join('JS','view.jpg'),3)
            click(location)
            for i in range(10):
                location=findPic(os.path.join('JS','finish.jpg'),1)
                if location:
                    del TaskStat[name]
                    break
                location=findPic(os.path.join('JS','cannot.jpg'),1)
                if location:
                    returnHome(id, "JS")
                    break
                location=findPic(os.path.join('JS','help.jpg'),1)
                if location:
                    click(location)
                    location=findPic(os.path.join('JS','success.jpg'),30)
                    if location:
                        click(location)
                        TaskStat[name] += 1
                        VmStat[id][name]=1
                        break
                time.sleep(1)
            else:
                VmStat[id][name]=0
            print(TaskStat)
            sucCount = list(VmStat[id].values()).count(1)
            print('sucCount:%s' % sucCount)
            saveJson(TaskStat, 'taskStat.json')
            saveJson(VmStat, 'vmStat.json')
            if sucCount>=3:
                closeVM(id)
                break
            returnHome(id, "JS")
        print(VmStat)
        if not TaskStat:
            break

def wx():
    allIds = [13,14]+list(range(25,40))+list(range(44,64))
    removeIds = [26, 30, 31, 34, 38] + list(range(54,59))
    allIds = list(set(allIds) - set(removeIds))
    allIds = [id for id in allIds if id>=SID]
    allIds.sort()
    for id in allIds:
        startVM(id)
        while 1:
            if findPic(os.path.join('APP','GAME.jpg'),1):
                location = findPic(os.path.join('APP','WX.jpg'),1)
                if location:
                    click(location)
                    time.sleep(60)
                    break
            time.sleep(1)
        closeVM(id)

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
        if SID==0:
            cleanStat()
        if os.path.exists('taskStat.json'):
            jsObj = open('taskStat.json').read()
            TaskStat = json.loads(jsObj)
        if os.path.exists('vmStat.json'):
            jsObj = open('vmStat.json').read()
            VmStat = json.loads(jsObj)
        if os.path.exists('config.json'):
            jsObj = open('config.json').read()
            Config = json.loads(jsObj)
        func = eval(sys.argv[1])
        func(*args)
