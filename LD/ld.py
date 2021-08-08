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
import requests
from skimage.measure import compare_ssim
import cv2
import win32con
import win32gui

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

SID=0
EID=76
LDFolder = 'LD4'
VmInfo = {}
TaskStat = {}
VmStat = {}
Config = {}
LDConsle = "J:\leidian\ldconsole.exe"
APPS = {
    "QQ" : "com.tencent.mobileqq",
    "WX" : "com.tencent.mm",
    "JD" : "com.jingdong.app.mall",
    #"JR" : "com.jd.jrapp",
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
    
def checkVMRunning(id):
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

def getAllVMsInfo():
    p=os.popen("%s list2" % (LDConsle))
    buf=p.read()
    for line in buf.splitlines():
        items = line.split(",")
        VmInfo[items[0]]=items[1]
    p.close()

def getRunVMsNum():
    p=os.popen("%s runninglist" % (LDConsle))
    buf=p.read()
    print(len(buf.splitlines()))
    p.close()

def minVM(id):
    hwnd = win32gui.FindWindow("LDPlayerMainFrame", VmInfo[str(id)])

    if hwnd == 0:
        print("Can't find window:%s" % VmInfo[str(id)])
        return
    
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWMINIMIZED)
    win32gui.SetForegroundWindow(hwnd)  # 设置前置窗口
    
def normalVM(id):
    hwnd = win32gui.FindWindow("LDPlayerMainFrame", VmInfo[str(id)])

    if hwnd == 0:
        print("Can't find window:%s" % VmInfo[str(id)])
        return
    
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.SetForegroundWindow(hwnd)  # 设置前置窗口

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
        allIds = list(range(2,7)) + list(range(9,EID))
        removeIds = [10, 12, 43, 47, 53]
    if app=="JS":
        allIds = list(range(2,10))+list(range(13,EID))+ [11]
        removeIds = [7, 8, 43, 47, 53]
    if app=="JR":
        allIds = list(range(2,EID))
        removeIds = [10, 27, 43]
    if app=="JX":
        allIds = list(range(7,53))
        removeIds = [9, 10, 23, 34, 38] + list(range(41,44))
    if app=="WX":
        allIds = [2,3,6,13,14]+list(range(25,40))+list(range(44,70))
        removeIds = [26, 30, 31, 34, 38] + list(range(54,59))
    allIds = list(set(allIds) - set(removeIds))
    allIds = [id for id in allIds if id>=SID]
    allIds.sort()
    if reverse:
        allIds.reverse()
    print(allIds)
    print(len(allIds))
    return allIds

def handleError():
    if findPic(os.path.join(LDFolder, "error.jpg"),1):
        location=findPic(os.path.join(LDFolder, "ok.jpg"),1)
        if location:
            click(location)

def shutdown():
    os.system("shutdown -s -t 0")

def sendWechatMsg(title, msg):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/57.0.2987.133 Safari/537.36'
    }
    url = "http://sc.ftqq.com/%s.send?text=%s&desp=%s" % ("SCU158650T62000825c439e9943dec882afcd51314601e0c3e70306", title, msg)
    session = requests.Session()
    response = session.get(url, headers=header, allow_redirects=False)
    body = json.loads(str(response.content, encoding = "utf-8"))
    if int(body["errno"]):
        print("Send wechat message error:%s" % body["errmsg"])
    else:
        print("Send wechat message success!")

def template(appName, task, pics, maxHitCount=100, maxHelpCount=3, rev=False):
    allVMs = getList(appName, rev)
    
    id = allVMs[0]
    startVM(allVMs[0])
    del allVMs[0]
    for nextId in allVMs:
        waitTime = 60
        limit = 0
        firstLoad = True
        startVM(nextId)
        checkVMRunning(id)
        normalVM(id)
        minVM(nextId)
        handleError()
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
        id = nextId
        if not TaskStat:
            break
    closeAllVM()
    sendWechatMsg(task, "finish!")

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
    sendWechatMsg("ZD", "finish")

def batch():
    zg()
    cleanStat()
    dg()
    cleanStat()
    fxj()
    shutdown()

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
    template('JD', 'qm', pics, 58, 1)

def lxj():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'lxj_help.jpg'
    pics['success'] = 'lxj_success.jpg'
    pics['finish'] = 'lxj_finish.jpg'
    template('JD', 'lxj', pics, 45, 3)
    
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
    template('JD', 'fxj', pics, 55, 3)

def hb():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'hb_help.jpg'
    pics['success'] = ['hb_success.jpg']
    pics['finish'] = 'hb_finish.jpg'
    template('JD', 'hb', pics, 25, 4)

def dgs():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'hb_help.jpg'
    pics['success'] = ['hb_success.jpg', 'hb_success1.jpg']
    pics['finish'] = 'hb_finish.jpg'
    template('JD', 'dgs', pics, 21, 1)

def ydh():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'ydh_help.jpg'
    pics['success'] = ['ydh_success.jpg', 'ydh_success1.jpg']
    pics['finish'] = 'ydh_finish.jpg'
    template('JD', 'ydh', pics, 10, 3)

def by():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'ydh_help.jpg'
    pics['success'] = ['ydh_success.jpg', 'ydh_success1.jpg']
    pics['finish'] = 'ydh_finish.jpg'
    template('JD', 'by', pics, 100, 3)

def qjd():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'qjd_help.jpg'
    pics['success'] = ['qjd_success.jpg']
    pics['finish'] = 'qjd_finish.jpg'
    template('JD', 'qjd', pics, 100, 3)

#打工
def dg():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'help.jpg'
    pics['success'] = ['dg_success.jpg', 'dg_success1.jpg', 'dg_success2.jpg', 'dg_success3.jpg']
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
    
def sqdyj():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'sqdyj_help.jpg'
    pics['success'] = ['sqdyj_success.jpg', 'sqdyj_success1.jpg']
    pics['finish'] = 'sqdyj_finish.jpg'
    template('JS', 'sqdyj', pics, 100, 1)

def sqdyjtx():
    pics = {}
    pics['view'] = 'view.jpg'
    pics['help'] = 'sqdyjtx_help.jpg'
    pics['success'] = 'sqdyjtx_success.jpg'
    #pics['finish'] = 'sqdyj_finish.jpg'
    template('JS', 'sqdyjtx', pics, 50, 3)
    
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

            for i in range(10):
                pyperclip.copy(line)
                runApp(id, 'JS')
                location=findPic(os.path.join('JS','view.jpg'),30)
                if location:
                    click(location)
                    break
                returnHome(id, "JS")

            for i in range(10):
                location=findPic(os.path.join('JS','finish.jpg'),1)
                if location:
                    if name in TaskStat:
                        del TaskStat[name]
                    break
                location=findPic(os.path.join('JS','cannot.jpg'),1)
                if location:
                    returnHome(id, "JS")
                    break
                location=findPic(os.path.join('JS','help.jpg'),1)
                if location:
                    click(location)
                    suc = False
                    for i in range(30):
                        location=findPic(os.path.join('JS','ts1.jpg'),1)
                        if location:
                            click(location)
                        location=findPic(os.path.join('JS','ts2.jpg'),1)
                        if location:
                            click(location)
                        location=findPic(os.path.join('JS','ts3.jpg'),1)
                        if location:
                            click(location)
                        location=findPic(os.path.join('JS','ts4.jpg'),1)
                        if location:
                            click(location)
                        location=findPic(os.path.join('JS','success.jpg'),1)
                        if location:
                            click(location)
                            TaskStat[name] += 1
                            VmStat[id][name]=1
                            suc = True
                            break
                        location=findPic(os.path.join('JS','success1.jpg'),1)
                        if location:
                            click(location)
                            TaskStat[name] += 1
                            VmStat[id][name]=1
                            suc = True
                            break
                        location=findPic(os.path.join('JS','finish.jpg'),1)
                        if location:
                            if name in TaskStat:
                                del TaskStat[name]
                            break
                    if suc:
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
    allVMs = getList("WX")
    '''
    for i in range(0,len(allVMs),3):
        group=allVMs[i:i+3]
        for id in group:
            startVM(id)
            runApp(id, "WX")
        time.sleep(60)
        for id in group:
            closeVM(id)
    '''
    index = 0
    for id in allVMs:
        startVM(id)
        runApp(id, "WX")
        if index>=2:
            closeVM(allVMs[index-2])
        time.sleep(30)
        index += 1
    time.sleep(60)
    closeAllVM()

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
        getAllVMsInfo()
        func = eval(sys.argv[1])
        func(*args)
