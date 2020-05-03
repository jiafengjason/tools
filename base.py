#!/usr/bin/env python
# codeing=utf-8

import os
import sys
import smtplib
import time
import threading
import datetime
import zipfile
import ConfigParser
import win32clipboard as w
import win32con
import xlrd #http://pypi.python.org/pypi/xlrd
import xlwt  #http://pypi.python.org/pypi/xlwt
import xlutils #http://pypi.python.org/pypi/xlutils
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
        
def encrypt(key, s): 
    """
    加密
    """
    b = bytearray(str(s).encode("gbk")) 
    n = len(b)
    c = bytearray(n*2) 
    j = 0 
    for i in range(0, n): 
        b1 = b[i] 
        b2 = b1 ^ key
        c1 = b2 % 16 
        c2 = b2 // 16 
        c1 = c1 + 65 
        c2 = c2 + 65
        c[j] = c1 
        c[j+1] = c2 
        j = j+2 
    return c.decode("gbk") 
 
def decrypt(key, s): 
    """
    解密
    """
    c = bytearray(str(s).encode("gbk")) 
    n = len(c)
    if n % 2 != 0 : 
        return "" 
    n = n // 2 
    b = bytearray(n) 
    j = 0 
    for i in range(0, n): 
        c1 = c[j] 
        c2 = c[j+1] 
        j = j+2 
        c1 = c1 - 65 
        c2 = c2 - 65 
        b2 = c2*16 + c1 
        b1 = b2^ key 
        b[i]= b1 
    try: 
        return b.decode("gbk") 
    except: 
        return "failed"
        
class Zip():
    def __init__(self, obj):
        #如果mode为'w'或'a'则表示要写入一个 zip 文件如果是写入，则还可以跟上第三个参数：compression=zipfile.ZIP_DEFLATED 或zipfile.ZIP_STORED
        self.obj=obj
        if os.path.isfile(obj):
            self.zipObj= zipfile.ZipFile(obj, mode='r')
        if os.path.isdir(obj):
            self.zipObj = zipfile.ZipFile(obj.split("/")[-1] +".zip", 'w')
        
    def unzip(self):
        for file in self.zipObj.namelist():
            self.zipObj.extract(file,".")
            
    def zip(self):
        for file in os.listdir(self.obj):
            self.zipObj.write(self.obj+os.path.sep+file)
        
class Clipboard():
    def getText(self):
        w.OpenClipboard()
        d = w.GetClipboardData(win32con.CF_TEXT)
        w.CloseClipboard()
        return d

    def setText(self, aString):
        w.OpenClipboard()
        w.EmptyClipboard()
        w.SetClipboardData(win32con.CF_TEXT, aString)
        w.CloseClipboard()
        
class Excel():
    def __init__(self, name):
        self.name = name
        self.wb = xlwt.Workbook(encoding = 'ascii')
        self.ws = self.wb.add_sheet('sheet1')
    def write(self, row, col, value):
        self.ws.write(row, col, value)
    
    def save(self):
        self.wb.save(self.name)
        
class Config():
    def __init__(self, file):
        self.file=file
        self.config = ConfigParser.ConfigParser()
        self.config.read(file)
        
    def get(self, section, option):
        return self.config.get(section, option)
        
    def set(self, section, option=None, value=None):
        if not self.config.has_section(section):
            self.config.add_section(section)
        if option is not None:
            self.config.set(section, option, value)
        self.config.write(open(self.file, "w"))
            
    def remove(self, section, option=None):
        if section is not None:
            if option is None:
                if self.config.has_section(section):
                    self.config.remove_section(section)
            else:
                self.config.remove_option(section, option)
        self.config.write(open(self.file, "w"))
        
class Mail():
    def __init__(self):
        self.smtp=smtplib.SMTP()
        #连接SMTP服务器，此处用的163的SMTP服务器 
        self.smtp.connect('smtp.163.com') 
        #用户名密码 
        self.smtp.login('jiafengjason@163.com', decrypt(96, 'KAGABEGFIFJFEFGFAF'))
        self.sender='jiafengjason@163.com'
        self.receiver=['jia.feng@zte.com.cn']

    def send(self, subject, content, file=None):
        #创建一个带附件的实例
        main_msg = MIMEMultipart()
        
        #加邮件头
        main_msg['From'] = self.sender
        main_msg['To'] =  ";".join(self.receiver)
        main_msg['Subject'] = Header(subject, 'utf-8')
        main_msg['date']=time.strftime('%a, %d %b %Y %H:%M:%S %z')   
        
        #中文需参数‘utf-8’，单字节字符不需要
        text_msg = MIMEText(content,'plain','utf-8')
        main_msg.attach(text_msg)
        
        #构造附件
        if file is not None:
            file_msg = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
            file_msg["Content-Type"] = 'application/octet-stream'
            file_msg["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(file)
            main_msg.attach(file_msg)

        #发送邮件
        self.smtp.sendmail(self.sender, self.receiver, main_msg.as_string())
        #self.smtp.close

class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def getResult(self):
        return self.res

    def run(self):
        self.res = apply(self.func, self.args)
        
class Color(object):
    DEBUG = '\033[35m'
    INFO = '\033[32m'
    ERROR = '\033[31m'
    ENDC = '\033[0m'
    
    @classmethod
    def _deco(cls, msg, color):
        return '%s%s%s' % (color, msg, cls.ENDC)
    
    @classmethod
    def debug(cls, msg):
        return cls._deco(msg, cls.DEBUG)
    @classmethod
    def info(cls, msg):
        return cls._deco(msg, cls.INFO)
    @classmethod
    def error(cls, msg):
        return cls._deco(msg, cls.ERROR)

class Logger(object):    
    def debug(self, msg):
        self._stdout(Color.debug("DEBUG: %s\n" % msg))
    
    def log(self, msg):
        self._stdout("%s\n" % (msg))
    
    def info(self, msg):
        self._stdout(Color.info('%s\n' % msg))
        
    def error(self, msg):
        self._stderr(Color.error("ERROR: %s\n" % msg))
        
    def _stdout(self, msg):
        sys.stdout.write(msg)
        sys.stdout.flush()
    def _stderr(self, msg):
        sys.stderr.write(msg)
        sys.stderr.flush()

logger = Logger()

if __name__ == '__main__':
    '''
    cb=Clipboard()
    #cb.setText('zte')
    print(cb.getText())
    
    xls=Excel('test.xls')
    xls.write(0,0,'zte')
    xls.write(0,1,'cgn')
    xls.save()
    
    mail=Mail()
    mail.send('Test', 'haha', 'base.py')
    
    cf=Config('config.ini')
    cf.set('TT', 'T1',456)
    print cf.get('TT', 'T1')
    '''
    ZipFileobj=Zip("subversion-1.7.18.rar")
    ZipFileobj.unzip()