#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import os.path
import shutil
#from shutil import copy

fromDir = ur'D:\android\BlueStacks'
toDir = ur'C:\Program Files\BlueStacks'

os.system("sc stop BstHdAndroidSvc")
os.system("sc stop BstHdLogRotatorSvc")
os.system("taskkill /f /im HD-Agent.exe")

if os.path.exists(toDir+ur'\Android\Data.sparsefs\Store'):
    os.remove(toDir+ur'\Android\Data.sparsefs\Store')
shutil.copy(fromDir+ur'\Android\Data.sparsefs\Store', toDir+ur'\Android\Data.sparsefs')
if os.path.exists(toDir+ur'\Android\SDCard.sparsefs\Store'):
    os.remove(toDir+ur'\Android\SDCard.sparsefs\Store')
shutil.copy(fromDir+ur'\Android\SDCard.sparsefs\Store', toDir+ur'\Android\SDCard.sparsefs')

if os.path.exists(toDir+r'\UserData'):
    shutil.rmtree(toDir+r'\UserData')#删除
shutil.copytree(fromDir+r'\UserData',toDir+r'\UserData')#拷贝
