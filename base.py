#!/usr/bin/env python
# codeing=utf-8

import os
import re
import sys
import socket
import difflib
import subprocess
import threading
import time
import pickle
import logging
import logging.config
import platform
import tarfile
import shutil
import fnmatch
import struct
import locale
import glob
import json
import stat
from distutils.version import LooseVersion

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig(os.path.join(CUR_DIR,"logging.conf"))

#create logger
logger = logging.getLogger()

'''
CRITICAL:50
ERROR:40
WARNING:30
INFO:20
DEBUG:10
NOTSET:0
logger.debug("debug message")
logger.info("info message")
logger.warn("warn message")
logger.error("error message")
logger.critical("critical message")
'''

def cd(path):
    print 'cd %s' % path
    if not os.path.exists(path):
        print "Can't find path:%s!" % path
        return False
    os.chdir(path)
    return True

def runCmd(cmd):
    if '(' in cmd or ')' in cmd:
        charList = []
        for char in cmd:
            if char=='(' or char==')':
                charList.append('\\')
            charList.append(char)
        cmd = ''.join(charList)
    logger.info(cmd)
    return os.system(cmd)
    
def execute(cmd, fdout=subprocess.PIPE, fderr=subprocess.PIPE):
    logger.info(cmd)
    if fdout and fdout!=subprocess.PIPE:
        fdout=open(fdout, 'w')
    if fderr and fderr!=subprocess.PIPE:
        fderr=open(fderr, 'w')
    child = subprocess.Popen(cmd.split(), stdout=fdout, stderr=fderr)
    out,err = child.communicate()
    ret = child.returncode
    if ret:
        logger.info(err)
        return ret,err
    else:
        logger.info(out)
        return ret,out

def tar(path,tarFile=None):
    curdir=os.getcwd()
    dirName = os.path.dirname(path)
    baseName  = os.path.basename(path)
    cd(dirName)
    if not tarFile:
        tarFile = '%s.tar.gz' % baseName
    runCmd('tar -zcvf %s %s' % (tarFile,baseName))
    cd(curdir)
    return tarFile
        
def unTar(fileName, dirs):
    try:
        t = tarfile.open(fileName)
        t.extractall(path = dirs)
    except Exception, err:
        logger.warn(err)
        runCmd('tar -xvf %s -C %s' % (fileName,dirs))
        
def getVersion(cmd):
    try:
        ret,buf = execute('%s -v' % cmd)
        match = re.search('.*\s+((?:\d+\.)+\d+)\s+',buf)
        if match:
            return match.group(1)
    except Exception, err:
        logger.warn(err)
    return None

def singleton(cls, *args, **kwargs):  
    instances = {}  
    def _singleton():
        if cls not in instances:  
            instances[cls] = cls(*args, **kwargs)  
        return instances[cls]  
    return _singleton  

try:
    import ConfigParser
except Exception, err:
    logger.warn(err)
else:
    class Config(object):
        def __init__(self, path):
            self.path = path
            self.cf = ConfigParser.ConfigParser()
            self.cf.read(self.path)
            
        def get(self, section, option):
            return self.cf.get(section, option).decode('utf8')
            
        def getSection(self, section):
            dict = {}
            for option in self.cf.items(section):
                dict[option[0]]=option[1]
            return dict
            
        def set(self, section, option, value):
            if not self.cf.has_section(section):
                self.cf.add_section(section)
            if option is not None:
                self.cf.set(section, option, value)
            self.cf.write(open(self.path,'w'))

        def remove(self, section, option=None):
            if section is not None:
                if option is None:
                    self.cf.remove_section(section)
                else:
                    if self.cf.has_option(section, option):
                        self.cf.remove_option(section,option)
            self.cf.write(open(self.path,'w'))

class Export:
    @staticmethod
    def getPara(key):
        return os.getenv(key)

    @staticmethod
    def setPara(key, value):
        os.environ[key] = value

class DataStore:
    @staticmethod
    def save(data,file):
        output = open(file, 'wb')
        pickle.dump(data, output, -1)
        output.close()
    
    @staticmethod
    def get(file):
        pkl_file = open(file, 'rb')
        data = pickle.load(pkl_file)
        pkl_file.close()
        return data
    
    @staticmethod
    def combine(fileFrom,fileTo):
        pklFrom = open(fileFrom, 'rb')
        pklTo = open(fileTo, 'rb')
        dataFrom = pickle.load(pklFrom)
        dataTo = pickle.load(pklTo)
        if isinstance(dataFrom,list) and isinstance(dataTo,list):
            dataTo.append(dataFrom)
        if isinstance(dataFrom,dict) and isinstance(dataTo,dict):
            dataTo.update(dataFrom)
        pklFrom.close()
        pklTo.close()
        return dataTo
    
    @staticmethod
    def getJson(jsFile):
        data = {}
        if os.path.exists(jsFile):
            fileObj = open(jsFile, 'r')
            jsObj = fileObj.read()
            data = json.loads(jsObj)
        return data
        
    @staticmethod
    def saveJson(data,jsFile):
        jsObj = json.dumps(data,ensure_ascii=False)
        fileObj = open(jsFile, 'w')
        fileObj.write(jsObj)
        fileObj.close()
    
class KeyStone:
    @staticmethod
    def getUser(ip):
        data = open(os.path.join(CUR_DIR,'key.json')).read()
        items = json.loads(data)
        for item in items:
            if ip==item['ip']:
                return item['username']
        return None
        
    @staticmethod
    def getPwd(ip):
        data = open(os.path.join(CUR_DIR,'key.json')).read()
        items = json.loads(data)
        for item in items:
            if ip==item['ip']:
                return item['password']
        return None

    @staticmethod
    def getValue(ip, key):
        data = open(os.path.join(CUR_DIR,'key.json')).read()
        items = json.loads(data)
        for item in items:
            if ip==item['ip']:
                if key in item:
                    return item[key]
                else:
                    break
        return None

        
class Base:
    """
    Provides an inheritable print overload method that displays
    instance with their class names and a name=value pair for
    each attribute stored on the instance itself (but not attrs
    inherited from its classes). Can be mixed into any class,
    and will work on any instance.
    """
    def __init__(self):
        self.system = platform.system()
        self.cur_dir = CUR_DIR
        self.config_path = os.path.join(self.cur_dir,'config.ini')
        self.package_path = os.path.join(self.cur_dir,'package')
        if self.system == 'Linux':
            self.history_home = os.path.join(self.cur_dir,'history')
            self.kernel = execute('uname -r')[1].split('-')[0]
        else:    
            self.history_home = '/home/tools/history'
        self.config = Config(self.config_path)
        self.python_version = platform.python_version()
        self.lcov_version = getVersion('lcov')
        self.gcov_version = getVersion('gcov')
        #self.in_vm = not os.path.exists("/proc/xen/capabilities")
        self.in_vm = os.path.exists("/sysdisk0")
        if LooseVersion(self.python_version) < LooseVersion('2.7'):
            print('Your python version is too low, you can execute "%s installPython" to install python2.7' % (os.path.abspath(__file__)))
            #self.installPython()
        self.encoding = sys.getdefaultencoding()
        self.locale = locale.getdefaultlocale()[0]+'.'+locale.getdefaultlocale()[1]
        self.ip = self.get_ip_address()            

    def installPkg(self,pkgName,cmds=None):
        logger.info('install %s',pkgName)
        curDir=os.getcwd()
        cd(self.package_path)
        if '.tar.gz' in pkgName:
            unTar(pkgName,'.')
            folder = pkgName.replace('.tar.gz','')
            cd(folder)
            if cmds:
                for cmd in cmds:
                    runCmd(cmd)
            else:
                if(os.path.exists("setup.py")):
                    try:
                        runCmd('python setup.py install')
                    except:
                        runCmd('./configure')
                        runCmd('make')
                        runCmd('make install')
                else:
                    runCmd('./configure')
                    runCmd('make')
                    runCmd('make install')
            cd('..')
            delete(folder)
        if '.exe' in pkgName:
            os.system(pkgName)
        cd(curDir)
    
    def installPython(self):
        logger.info(self.python_version)
        self.installPkg('zlib-1.2.8.tar.gz')
        self.installPkg('Python-2.7.8.tar.gz',['./configure','make','make install'])
        if os.path.exists('/usr/local/bin/python'): 
            runCmd('mv /usr/bin/python /usr/bin/python%s' % self.python_version)
            runCmd('ln -s /usr/local/bin/python /usr/bin/python')
            if os.path.exists('/usr/bin/yum'):
                replace('/usr/bin/yum',open('/usr/bin/yum','r').next().strip(),'#!/usr/bin/python%s\n' % self.python_version)
            if os.path.exists('/usr/sbin/xend'):
                replace('/usr/sbin/xend',open('/usr/sbin/xend','r').next().strip(),'#!/usr/bin/python%s\n' % self.python_version)
            if os.path.exists('/usr/sbin/xm'):
                replace('/usr/sbin/xm',open('/usr/sbin/xm','r').next().strip(),'#!/usr/bin/python%s\n' % self.python_version)
        self.python_version = platform.python_version()
        logger.info(self.python_version)

    def installPythonModule(self,moduleName):
        for file in glob.iglob('%s/*%s*.tar.gz' % (self.package_path,moduleName)):
            print file
            self.installPkg(file)

    def getIpByIfname(self,ifname):
        import fcntl
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

    def parseIfconfig(self):
        eths = {}
        ret,buf = execute("ifconfig")
        
        for line in buf.splitlines():
            match = re.search(r"(\w+):\s+flags=",line)
            if match:
                eth = {}
                eths[match.group(1)] = eth
                continue
            match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)\s+netmask\s+(\d+\.\d+\.\d+\.\d+)",line)
            if match:
                eth["ipv4"] = match.group(1)
                eth["netmask"] = match.group(2)
                ipSegments = eth["ipv4"].split(".")
                ipSegments[3] = "1"
                eth["gateway"] = ".".join(ipSegments)
                continue
            match = re.search(r"ether\s+(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})",line)
            if match:
                eth["mac"] = match.group(1)
                continue
        return eths

    def get_ip_address(self):
        if self.system == 'Windows':
            return socket.gethostbyname(socket.gethostname())
        elif self.system == 'Linux':
            eths = self.parseIfconfig()
            for eth,ethConfig in eths.items():
                if "ipv4" in ethConfig and ethConfig["ipv4"].startswith("10.4"):
                    return ethConfig["ipv4"]
    
    def gatherAttrs(self):
        attrs = []
        for key in sorted(self.__dict__):
            attrs.append('%s=%s' % (key, getattr(self, key)))
        return ','.join(attrs)
    
    def __str__(self):
        return '[%s: %s]' % (self.__class__.__name__, self.gatherAttrs())

base = Base()

class Transport:
    def __init__(self,hostname,username,password,port=22):
        paramiko = tryImport('paramiko')
        
        paramiko.util.log_to_file("paramiko.log")
        
        '''
        logger.info("ssh %s:%s %s/%s" % (hostname,port,username,password))
        
        self.hostname=hostname
        self.port=port
        self.username=username
        self.password=password
        
        self.ssh=paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.tcpsock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.tcpsock.settimeout(None)
        self.tcpsock.connect((self.hostname,self.port),)
        self.trans=paramiko.Transport(self.tcpsock)
        key = None
        #private key
        keyfile='/root/.ssh/id_rsa'
        if os.path.exists(keyfile):
            key=paramiko.RSAKey.from_private_key_file(keyfile)
        self.ssh.connect(self.hostname,self.port,self.username,self.password,pkey=key)
        try:
            self.trans.connect(username=self.username,password=self.password)
        except Exception, err:
            logger.error(err)
            self.trans.connect(username=self.username,pkey=key)
        #vi /etc/ssh/sshd_config
        #Subsystem       sftp    /usr/libexec/openssh/sftp-server
        #/etc/init.d/sshd restart
        self.sftp=paramiko.SFTPClient.from_transport(self.trans)
        '''
        
    def getChan(self,timeout=3):
        if not hasattr(self,'chan') or not self.chan:
            self.chan=self.trans.open_session()
            self.chan.settimeout(timeout)
            self.chan.get_pty()
            self.chan.invoke_shell()
        return self.chan

    def send(self,cmd):
        self.chan.send(cmd+'\n')

    def recv(self,expects=[],size=65535):
        needBreak = False
        while 1:
            try:
                buf=self.chan.recv(size)
                sys.stdout.write(buf)
                sys.stdout.flush()
                buf=buf.strip()
            except socket.timeout,err:
                if not expects:
                    break
            if expects:
                for expect in expects:
                    if buf.endswith(expect):
                        needBreak = True
                if needBreak:
                    break
            
            time.sleep(1)

    def comand(self,cmd,interactives=None):
        print cmd
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        
        if interactives:
            for interactive in interactives:
                stdin.write(interactive+"\n")
        
        if "&" not in cmd:
            out=stdout.read()
            err=stderr.read()
            logger.info(out)
            logger.error(err)
            return out
        return None
    
    def uploadfile(self, local_file, remote_file):
        logger.info("upload from %s to %s" % (local_file, remote_file))
        self.sftp.put(local_file,remote_file)    

    def uploadfolder(self, local_dir, remote_dir):
        logger.info("download from %s to %s" % (local_dir, remote_dir))
        remote_dir = os.path.join(remote_dir,os.path.basename(local_dir))
        self.sftp.mkdir(remote_dir)
        for root,folders,files in os.walk(local_dir):
            for folder in folders:
                local_folder=os.path.join(root,folder)
                foldername=local_folder.replace(local_dir,'')
                foldername=foldername.lstrip('/')
                remote_folder=os.path.join(remote_dir,foldername)
                self.sftp.mkdir(remote_folder)
            for filepath in files:
                local_file=os.path.join(root,filepath)
                filename=local_file.replace(local_dir,'')
                filename=filename.lstrip('/')
                remote_file=os.path.join(remote_dir,filename)
                self.sftp.put(local_file,remote_file)
                logger.info("upload %s to remote %s" % (local_file,remote_file))
                
    def downloadfile(self, remote_file, local_file):
        logger.info("download from %s to %s" % (remote_file, local_file))
        self.sftp.get(remote_file,local_file)
        
    def downloadfolder(self, remote_dir, local_dir):
        logger.info("download from %s to %s" % (remote_dir, local_dir))
        files=self.sftp.listdir(remote_dir)
        for file in files:
            remote_file=remote_dir+'/'+file
            local_file=os.path.join(local_dir,file)
            try:
                self.sftp.get(remote_file, local_file)
            except Exception,err:
                logger.error(err)
                logger.warn("cteate dir %s" % os.path.split(local_file)[0])
                os.mkdir(os.path.split(local_file)[0])
                self.sftp.get(remote_file, local_file)
            logger.info("download %s to local %s" % (remote_file, local_file))
        
    def close_connect(self):
        self.trans.close()
        self.ssh.close()
        self.tcpsock.close()

@singleton
class Jenkins(Transport):
    def __init__(self):
        self.hostname = base.config.get('JENKINS','master')
        username = KeyStone.getUser(self.hostname)
        password = KeyStone.getPwd(self.hostname)
        self.buildNum = None
        if Export.getPara('BUILD'):
            self.buildNum = Export.getPara('BUILD')
        elif Export.getPara('BUILD_NUMBER'):
            self.buildNum = Export.getPara('BUILD_NUMBER')
        self.islocal = (base.ip==self.hostname)
        if self.isRun():
            Transport.__init__(self,self.hostname,username,password)
            self.buildDir = '%s/%s' % (base.history_home,self.buildNum)
            self.tomcatRootUrl = 'http://%s:8080' % (self.hostname)
            #self.comand('if [ ! -d %s ]; then %s/base.py createHistory;fi' % (self.buildDir,base.cur_dir))
        else:
            self.buildDir = '%s/local' % (base.history_home)
        runCmd("mkdir -p %s" % self.buildDir)
        if base.system == 'Linux':
            self.addFolder('PKL')

    def isRun(self):
        if not self.buildNum:
            print 'Build num is None'
            return False
        return True
        
    def getBuildNum(self):
        if self.isRun():
            return self.buildNum
        return None
        
    def getBuildDir(self):
        return self.buildDir

    def getLogFile(self):
        if self.isRun():
            return "%s/jobs/%s/builds/%s/log" % (Export.getPara('JENKINS_HOME'),Export.getPara('JOB_NAME'),Export.getPara('BUILD_NUMBER'))
        return None
        
    def generateTomcatUrl(self,url):
        if self.isRun():
            return '%s/CI/%s/%s' % (self.tomcatRootUrl,self.buildNum,url)
        return None

    def generateResult(self,result,summaryTxt,summaryUrl,detailTxt,detailUrl,attach=None):
        if self.isRun():
            data={}
            data['jobName'] = Export.getPara("JOB_NAME")
            data['jobUrl'] = Export.getPara("JOB_URL")
            data['result'] = result
            if summaryTxt:
                data['summaryTxt'] = summaryTxt
            else:
                data['summaryTxt'] = " "
            if summaryUrl:
                data['summaryUrl'] = summaryUrl
            if detailTxt:
                data['detailTxt'] = detailTxt
            else:
                data['detailTxt'] = " "
            if detailUrl:
                data['detailUrl'] = detailUrl
            if attach:
                data['attach']=attach
            return data
        return None

    def addFolder(self, folder):
        runCmd("mkdir -p %s/%s" % (self.buildDir,folder))
        if self.isRun() and not self.islocal:
            fullPath = '%s/%s' % (self.buildDir,folder)
            self.comand('if [ ! -d %s ]; then mkdir -p %s;fi' % (fullPath,fullPath))            
                
    def linuxPathToSmbPath(self, linux_path):
        if self.isRun():
            return "\\\\%s%s" % (self.hostname,linux_path.replace('/','\\'))
            
    def copyFromSlaveToMaster(self, slave, master=None):
        if self.isRun():
            if master:
                master = '%s/%s' % (self.buildDir,master)
            else:
                master = self.buildDir
            if self.islocal:
                copy(slave,master)    
            else:
                if os.path.isfile(slave):
                    self.uploadfile(slave, master)
                if os.path.isdir(slave):
                    self.uploadfolder(slave, master)
            return master
        return None

    def copyFromMasterToSlave(self, master, slave):
        if self.isRun():
            if self.islocal:
                copy(master,slave)
            else:
                self.downloadfile(master, slave)

    def savePkl(self, data):
        if data:
            if 'jobName' in data:
                pklFile = '%s.pkl' % data['jobName']
                DataStore.save(data, pklFile)
                self.copyFromSlaveToMaster(pklFile,'PKL/%s' % pklFile)
            else:
                print "Can't find jobName in data"
                print data

class Filelist:
    def __init__(self,filename='path.info'):
        self.processInfo = []
        for line in open(os.path.join(base.cur_dir,filename)):
            line = line.strip()
            if not line:
                continue
            items = line.split(':')
            if len(items)==3:
                self.processInfo.append(items)
            else:
                logger.error(items)

    def getAllTeams(self):
        teams = set([item[0] for item in self.processInfo])
        return list(teams)

    def getAllProcesses(self):
        processes = set([item[1] for item in self.processInfo])
        return list(processes)
        
    def checkTeamExists(self,team):
        teams = self.getAllTeams()
        return team in teams
        
    def getProcessesByTeam(self,team):
        processes = set(item[1] for item in self.processInfo if item[0] == team)
        return list(processes)

    def checkProcessExists(self,team,process):
        processes = self.getProcessesByTeam(team)
        return process in processes
        
    def getFilelist(self,team,process=None):
        paths = []
        teams = self.getAllTeams()
        if not self.checkTeamExists(team):
            return paths
            
        if process:
            if not self.checkProcessExists(team,process):
                return paths
            paths = list(set(item[2] for item in self.processInfo if item[0] == team and item[1]== process))
        else:
            paths = list(set(item[2] for item in self.processInfo if item[0] == team))
        return paths

    def getTeamAllFilelist(self,teams='ALL',processes='ALL',ignoreProcesses=[]):
        teamList = []
        processList = []
        teamFilelist = {}

        teams = teams.upper()
        processes = processes.upper()
        if teams == 'ALL':
            teamList = self.getAllTeams()
        else:
            teamList = teams.split(',')
        
        for team in teamList:
            if not self.checkTeamExists(team):
                print "Can't find team %s" % team
                continue
            
            if processes == 'ALL':
                processList = self.getProcessesByTeam(team)
            else:
                for process in processes.split(','):
                    if self.checkProcessExists(team,process):
                        processList.append(process)
                        
            processDetail = {}            
            for process in processList:
                if process in ignoreProcesses:
                    continue
                fileList = self.getFilelist(team,process)
                processDetail[process] = {}
                processDetail[process]['all'] = fileList
            if processDetail: 
                teamFilelist[team] = processDetail

        return teamFilelist
    
filelist = Filelist()
            
def ping(ip):
    count = 0
    print "Testing %s" % ip
    while 1:
        if base.system == 'Linux':
            ret,buf = execute('ping -c 1 %s' % ip)
        else:
            ret,buf = execute('ping -n 1 %s' % ip)
        match = re.search(r"(\d+)%",buf)
        if match:
            lost = int(match.group(1))
            if not lost:
                return True
        count += 1
        if count>2:
            break
        time.sleep(1)    
    return False

def tryImport(moduleName):
    try:
        module = __import__(moduleName)
    except Exception, err:
        logger.error(err)
        pipInstall(moduleName)
        module = __import__(moduleName)
    return module    

def format_path(path):
    if '..' not in path:
        return path
    pathList=path.split(os.path.sep)
    while 1: 
        if '..' in pathList:
            index=pathList.index('..')
            del pathList[index]
            del pathList[index-1]
        else:
            break
    return os.path.sep.join(pathList)

def listdir_nohidden(top,ext=None):
    for file in os.listdir(top):
        if not file.startswith('.') and (not ext or file.endswith(ext)):
            yield file

def search(top, pat):
    for dirpath, dirnames, filenames in os.walk(top):
        for dirname in fnmatch.filter(dirnames, pat):
            yield os.path.join(dirpath, dirname)
        for filename in fnmatch.filter(filenames, pat):
            yield os.path.join(dirpath, filename)

def copy(src,dst):
    print "Copy from %s to %s" % (src,dst)
    curdir=os.getcwd()
    src = os.path.abspath(src)
    if os.path.exists(src):
        if os.path.isfile(src):
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    srcBase = os.path.basename(src)
                    dst = os.path.join(dst,srcBase)
                    os.chmod(dst, stat.S_IREAD|stat.S_IWRITE)
            else:
                dstDir = os.path.dirname(dst)
                if not os.path.exists(dstDir):
                    os.makedirs(dstDir)
            shutil.copyfile(src,dst)
        if os.path.isdir(src):
            if os.path.exists(dst):
                cd(dst)
                dst = os.path.basename(src)
            else:
                dirName = os.path.dirname(dst)
                if os.path.exists(dirName):
                    cd(dirName)
                    dst = os.path.basename(dst)
            shutil.copytree(src,dst)
    cd(curdir)

def delete(item):
    if os.path.exists(item):
        try:
            if os.path.isfile(item):
                os.remove(item)
            if os.path.isdir(item):
                shutil.rmtree(item)
        except Exception, err:
            print(err)
            runCmd('rm -rf %s' % item)
    else:
        print "Can't find %s" % item
    
def encrypt(key, s):
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
    except Exception, err:
        logger.error(err)
        return "failed" 

def replace(file, patten, str):
    if not os.path.exists(file):
        return
    old_content=open(file).read()
    p= re.compile(patten)
    new_content = p.sub(str, old_content)
    if new_content != old_content:
        open(file,'w').write(new_content)

def fuzzyfinder(user_input, collection):
    suggestions = []
    pattern = '.*?'.join(user_input)
    regex = re.compile(pattern)
    for item in collection:
        match = regex.search(item)
        if match:
            suggestions.append((len(match.group()), match.start(), item))
    return [x for _, _, x in sorted(suggestions)]
        
try:
    from optparse import OptionParser 
except Exception, err:
    logger.warn(err)
else:
    class EasyMake:
        def __init__(self,func,help):
            self.func = func
            self.parser = OptionParser(usage = help, version="%prog 1.0")
            
        def addOption(self, *args, **kwargs):
            self.parser.add_option(*args,**kwargs)
            
        def getCmd(self,args):
            (self.options, self.args) = self.parser.parse_args(args)
            return self.func(self.options, self.args)

try:
    import telnetlib
except Exception, err:
    logger.warn(err)
else:
    class MyTelnet:
        def __init__(self,ip,port,timeout=None):
            self.timeout = timeout
            self.child = telnetlib.Telnet(ip,port,self.timeout)
        
        def setTimeout(self,timeout=None):
            self.timeout = timeout
        
        def write(self,cmd):
            self.child.write(cmd)
        
        def expect(self,expectList,timeout=None):
            if not timeout:
                timeout = self.timeout
            index,match,buf = self.child.expect(expectList,timeout)
            print buf
            return index,match,buf

class SSH:
    def __init__(self,hostname,username='root',password='zte123'):
        pexpect = tryImport('pexpect')
        self.hostname=hostname
        self.username=username
        self.password=password
        
        sshStr='ssh %s@%s' % (self.username, self.hostname)
        logger.info(sshStr)
        self.xen = pexpect.spawn(sshStr)
        try:
            ret = self.xen.expect([']#','password:', 'continue connecting (yes/no)?'], timeout=3)
            logger.info(ret)
            if ret == 0 :
                pass
            elif ret == 1 :
                self.sendline(self.password+'\n')
            elif ret == 2:
                self.sendline('yes\n')
                self.xen.expect('password: ')
                self.sendline(self.password)
        except pexpect.EOF:
            logger.error('Connection closed.')
            self.xen = None
        except pexpect.TIMEOUT:
            logger.warn('Connet to ' + hostname + ' time out.')
            self.xen = None
    
    def sendline(self,cmd):
        logger.info(cmd)
        self.xen.sendline(cmd)
        
    def boot_to_oam(self,boot_dir):
        if self.xen:
            self.xen.sendline('telnet 127.0.0.1 10000')
            self.xen.expect('login:')
            self.xen.sendline('zte')
            self.xen.expect('password:')
            self.xen.sendline('zte')
            self.xen.expect('Successfully login into ushell!')
            self.xen.sendline('\n')
            self.xen.expect('admin]#')
            #time.sleep(30) 
            self.xen.sendline('kill 0')
            self.xen.sendline('\n')
    
    def close(self):
        self.xen.close()

try:
    import smtplib
    from base64 import b64encode
    from email.MIMEText import MIMEText
    from email.MIMEMultipart import MIMEMultipart
    rpyc = tryImport('rpyc')
    from rpyc import Service
    from rpyc.utils.server import ThreadedServer
except Exception, err:
    logger.warn(err)
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
else:
    class MailService(Service):
        def addFrom(self, sender):
            self.msgRoot['From'] = sender
            
        def addTo(self, to):
            if isinstance(to, list):
                self.msgRoot['To'] = ','.join(to)
            else:
                self.msgRoot['To'] = to
        
        def addSubject(self, subject):
            self.msgRoot['Subject'] = '=?%s?B?%s?='%('gbk',b64encode(subject))
        
        def addContent(self, content):
            # Encapsulate the plain and HTML versions of the message body in an
            # 'alternative' part, so message agents can decide which they want to display.
            msgAlternative = MIMEMultipart('alternative')
            self.msgRoot.attach(msgAlternative)

            if os.path.isfile(content):
                ext=os.path.splitext(content)[1]
                content=open(content).read()
        
                if ext=='.txt':
                    msgText = MIMEText(content,'text','utf-8')
                elif ext=='.html':
                    msgText = MIMEText(content, 'html', 'utf-8')
            else:
                msgText = MIMEText(content,'text','utf-8')
            msgAlternative.attach(msgText)
        
        def addAttach(self, attachName, attachContent):
            msgFile = MIMEText(attachContent, 'base64', 'utf-8')
            msgFile["Content-Type"] = 'application/octet-stream'
            msgFile["Content-Disposition"] = 'attachment; filename="%s"' % attachName
            self.msgRoot.attach(msgFile)
            
        def addAttachFile(self, attachFile):
            if os.path.isfile(attachFile):
                attachName = os.path.basename(attachFile)
                attachContent = open(attachFile, 'rb').read()
                self.addAttach(attachName, attachContent)
            
        def exposed_send(self, receiver, subject, content, attach=None):
            self.server = smtplib.SMTP()
            self.server.set_debuglevel(1) 
            
            self.server.connect(base.config.get('SMTP','hostname')) 
            #self.server.login(base.config.get('SMTP','username'),base.config.get('SMTP','password'))
            self.sender = base.config.get('SMTP','from')
            self.receiver = receiver
            if receiver:
                if isinstance(receiver, list):
                    self.receiver = receiver
                elif isinstance(receiver, str):
                    if ',' in receiver:
                        self.receiver = receiver.split(',')
                    if ';' in receiver:
                        self.receiver = receiver.split(';')
            self.msgRoot = MIMEMultipart()
            
            self.addFrom(self.sender)
            self.addTo(self.receiver)
            self.addSubject(subject)
            self.addContent(content)
            
            if attach:
                if isinstance(attach, dict):
                    for attachName,attachContent in attach.items():
                        self.addAttach(attachName, attachContent)
                elif isinstance(attach, list):
                    for attachFile in attach:
                        self.addAttachFile(attachFile)
                else:
                    self.addAttachFile(attach)
            
            self.msg = self.msgRoot.as_string()
            self.server.sendmail(self.sender, self.receiver, self.msg)  
            #self.server.close()
            #self.server.quit()
    
class History:
    @staticmethod
    def addByTime():
        history_reserve_count = int(base.config.get('BASE','history_reserve_count'))
        history=os.path.join(os.getcwd(),"history", time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time())))
        if not os.path.exists(history):
            os.makedirs(history)
        historys = []
        for item in listdir_nohidden("history"):
            if os.path.isdir(os.path.join(os.getcwd(),"history",item)):
                historys.append(item)
        if len(historys)>history_reserve_count:
            historys.sort(key=lambda x:time.mktime(time.strptime(x,"%Y%m%d_%H%M%S")),reverse=True)
            for item in historys[history_reserve_count:]:
                delete(os.path.join("history",item))
        return history

    @staticmethod
    def addByBuild(buildNum):
        if not buildNum:
            print "BUILD_NUM is None"
            return
        history_reserve_count = int(base.config.get('BASE','history_reserve_count'))
        history=os.path.join(base.history_home, buildNum)
        if not os.path.exists(history):
            os.makedirs(history)
        historys = []
        for item in listdir_nohidden(base.history_home):
            if os.path.isdir(os.path.join(base.history_home,item)):
                historys.append(int(item))
        if len(historys)>history_reserve_count:
            historys.sort(reverse=True)
            for item in historys[history_reserve_count:]:
                delete(os.path.join(base.history_home,str(item)))
        return history
            
class Svn:
    def __init__(self, baseUrl,username=None,password=None):
        self.baseUrl = baseUrl
        self.username = username
        self.password = password
        if not self.username:
            self.getAuth()
        self.auth = self.getConnectionString()
        self.getInfo()
    
    def getAuth(self):
        auths = {}
        for file in search('/root/.subversion/auth/svn.simple', '*'):
            auth = {}
            current = None
            key = None
            for line in open(file, 'r'):
                if line.strip() == 'END':
                    break
                match=re.match('K\s(\d+)', line)
                if match:
                    current = 'key'
                    continue
                match=re.match('V\s(\d+)', line)
                if match:
                    current = 'value'
                    continue
                if current == 'key':
                    key = line.strip()
                elif current == 'value':
                    auth[key] = line.strip()
            auths[os.path.basename(file)] = auth
        for file,auth in auths.items():
            if 'svn:realmstring' in auth:
                match=re.match('<(\S+//(\d+\.\d+\.\d+\.\d+)\S+)>\s', auth['svn:realmstring'])
                if match:
                    auth['root'] = match.group(1)
                    auth['ip'] = match.group(2)
        for file,auth in auths.items():
            if 'ip' in auth:
                if auth['ip'] in self.baseUrl:
                    self.username = auth['username']
                    self.password = auth['password']
    
    def getConnectionString(self):
        str = ""
        if self.username:
            str+="--username %s " % self.username
        if self.password:
            str+="--password %s " % self.password
        return str
    
    def getInfo(self, file=None):
        info = {}
        url=self.baseUrl
        if file:
            url=url+'/'+file
        cmd = "svn info %s %s" % (url,self.auth)
        #logger.info(cmd)
        child=subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        for line in child.stdout.read().split("\n"):
            if not line.strip():
                continue
            if ":" in line:
                index=line.find(":")
                info[line[:index]]=line[index+1:].strip()
        self.revision = info['Revision']
        self.url = info['URL']
        self.root = info['Repository Root']
        return info
        
    def update(self):
        cmd = "svn up %s %s" % (self.root,self.auth)
        #logger.info(cmd)
        subprocess.call(cmd.split())
        self.getInfo()
        
    def getLog(self, revision, file=None):
        url=self.baseUrl
        if file:
            url=url+'/'+file
        cmd = "svn log %s -v -r %s %s" % (url, revision, self.auth)
        #logger.info(cmd)
        child=subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        self.logs={}
        for log in child.stdout.read().split("------------------------------------------------------------------------"):
            if len(log.strip()) == 0:
                continue
            find=re.findall('r(\d+)\s*\|\s*(\S+)\s*\|\s*(\d+-\d+-\d+\s+\d+:\d+:\d+).*\sChanged paths:\s((\s*\w\s.*\n)+)\s*(.*)', log)
            if find:
                log={}
                log['revision']=find[0][0]
                log['author']=find[0][1]
                log['date']=find[0][2]
                log["message"]=find[0][5]
                if log['author']=='merge':
                    match=re.match('\[AUTO_MERGE\](\S+)\s+merge from', log["message"])
                    if match:
                        log['author'] = match.group(1)
                changeFiles=[]
                files=find[0][3]
                for file in files.strip().split("\n"):
                    file=file.strip().split()
                    dicFile={}
                    dicFile["action"]=file[0]
                    dicFile["filename"]=file[1]
                    changeFiles.append(dicFile)
                log['changes']=changeFiles
                self.logs[find[0][0]]=log
        return self.logs
    
    def cat(self, file, revision=None):
        url=self.baseUrl
        file = file.strip('/')
        url=url+'/'+file
        if revision:
            cmd = "svn cat -r %s %s %s" % (revision,url,self.auth)
        else:
            cmd = "svn cat %s %s" % (self.url,self.auth)
        #logger.info(cmd)
        child=subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        return child.stdout.read()
        
    def getRevByDate(self, date):
        cmd = "svn log %s -r {%s} %s" % (self.root,date,self.auth)
        logger.info(cmd)
        child=subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        log=child.stdout.read()
        #logger.info(log)
        match=re.findall('r(\d+)', log)
        if match:
            rev = match[0]
            return rev
        return 0
        
    def getRevByRange(self, startDate, endDate):
        startRev = 0
        endRev = 0
        cmd = "svn log %s -r {%s}:{%s} %s" % (self.root,startDate,endDate,self.auth)
        #logger.info(cmd)
        child=subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        for line in child.stdout.read().split("\n"):
            match=re.match('^r(\d+)', line)
            if match:
                rev = int(match.group(1))
                if not startRev:
                    startRev = rev
                if not endRev:
                    endRev = rev
                if rev<startRev:
                    startRev = rev
                if rev>endRev:
                    endRev = rev
        return startRev,endRev
        
    def getDiff(self, revision, file):
        cmd = "svn diff -r %s %s %s" % (revision,os.path.join(self.baseUrl,file),self.auth)
        #logger.info(cmd)
        p=subprocess.Popen(cmd.split(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdoutdata,stderrdata = p.communicate()
        if p.returncode==0:
            if not stdoutdata or stdoutdata.strip()=='':
                return None
            return stdoutdata.split('\n')
        else:
            logger.warn("returncode:%s,error:%s" % (p.returncode,stderrdata))
            if 'Unable to find repository location' in stderrdata:
                return 'Add'

class Git:
    def __init__(self, path,username=None,password=None):
        self.path = path
        self.username = username
        self.password = password
        self.auth = self.getAuth()
        cd(path)
        
    def getAuth(self):
        str = ""
        if self.username:
            str+="--username %s " % self.username
        if self.password:
            str+="--password %s " % self.password
        return str
        
    def getLog(self,since=None,until=None,after=None,before=None):
        cmd = 'git log --stat'
        if since:
            cmd = '%s %s' % (cmd,since)
        if until:
            cmd = '%s..%s' % (cmd,until)
        if after:
            cmd = '%s --after="%s"' % (cmd,after)
        if before:
            cmd = '%s --before="%s"' % (cmd,before)
        logger.info(cmd)
        child=subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
        
        self.logs={}
        buf = child.stdout.read()
        match=re.findall('commit\s*(\w+)\s*Author:\s*.+\s*<(.+)@.+>\s*Date:\s*(.+)\s*(.+)\s*((?:.+\s*\|\s*\d+\s*[\+-]*\s*)*)\s*(\d+)\s*files\s*changed,\s*(\d+)\s*insertions\(\+\),\s*(\d+)\s*deletions\(-\)', buf)
        if match:
            for item in match:
                log={}
                log['commit']=item[0]
                log['author']=item[1]
                log['date']=item[2]
                log['message']=item[3]
                log["add"]=int(item[6])
                log["del"]=int(item[7])
                self.logs[log['commit']]=log
        return self.logs

class Compare:
    def __init__(self, oldContent, newContent):
        self.lineAdd=0
        self.lineDel=0
        oldList = self.convert(oldContent)
        newList = self.convert(newContent)
        lineDiff = difflib.unified_diff(oldList,newList)
        addPatten = re.compile('\+\s*[^\+\s]+')
        delPatten = re.compile('-\s*[^-\s]+')
        for line in lineDiff:
            if re.match(addPatten,line):
                self.lineAdd += 1
            if re.match(delPatten,line):
                self.lineDel += 1
        logger.info("Add:%d,Del:%d" % (self.lineAdd, self.lineDel))
        
    def convert(self, content):
        list = []
        for line in content.split('\n'):
            line = ' '.join(line.split())
            if line == '':
                continue
            list.append(line)
        return list

class Thread(threading.Thread):
    def __init__(self,threadName,threadTarget,threadArgs):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.func = threadTarget
        self.args = threadArgs
        self.ret = 0
        self.thread_stop=False
    
    def getRet(self):
        return self.ret
    
    def run(self):
        #print 'starting', self.name, 'at:', time.ctime()
        logger.info("Start thread %s" % (self.threadName))
        ret = apply(self.func, self.args)
        if isinstance(ret,tuple):
            ret = ret[0]
        self.ret += ret
        print "############%s###############" % self.ret
        #print self.name, 'finished at:', time.ctime()
    
    def stop(self):
        self.thread_stop=True
        
class Threads:
    def __init__(self):
        self.threads = {}
    
    def add(self,threadName,threadTarget,threadArgs,isDaemon=False):
        thread = Thread(threadName,threadTarget,threadArgs)
        thread.setDaemon(isDaemon)
        self.threads[threadName]=thread
      
    def startAll(self):
        for thread in self.threads.values():
            thread.start()
    
    def joinAll(self):
        print self.threads.values()
        for thread in self.threads.values():
            thread.join()

    def getRet(self):
        ret = 0
        for thread in self.threads.values():
            ret += thread.getRet()
        return ret   

class UdpSock:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.addr = (self.hostname,self.port)
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def bind(self):
        try:
            self.socket.bind(self.addr)
        except Exception, err:
            logger.error(err)
    
    def send(self,data):
        self.socket.sendto(data,self.addr)

    def receive(self,bufsize):
        try:
            data,addr = self.socket.recvfrom(bufsize)
            return data
        except Exception, err:
            logger.error(err)
            return None
    
class Excel:
    def __init__(self, filename):
        xlwt = tryImport('xlwt')
        self.wb = xlwt.Workbook(encoding='utf-8')
        self.style=xlwt.XFStyle()
        font=xlwt.Font()
        #'SimSun'
        font.name='Times New Roman'
        '''
        12*12 7
        16*16 13
        18*18 16
        '''
        font.height=16*16
        font.bold=True
        self.style.font = font
        self.filename = filename
    
    def addSheet(self,sheetName,data):
        column = {}
        columnIndex = 0
        rowIndex = 1
        ws=self.wb.add_sheet(sheetName,cell_overwrite_ok=True)
        for key,item in data.items():
            for columnName,value in item.items():
                if columnName not in column:
                    ws.write(0,columnIndex,columnName,self.style)
                    column[columnName] = columnIndex
                    columnIndex += 1
                ws.write(rowIndex,column[columnName],value)
            rowIndex += 1
        
        self.wb.save(self.filename)

class Module:
    def __init__(self):
        self.moduleType = type(sys)
        self.modules = {}
    
    def load(self, fullpath, env={}):
        try:
            code = open(fullpath).read()
        except IOError:
            raise ImportError, 'No module named %s' %fullpath

        filename = os.path.basename(fullpath)

        try:
            return self.modules[filename]
        except KeyError:
            pass

        m = self.moduleType(filename)
        m.__module_class__ = self.moduleType
        m.__file__ = fullpath

        m.__dict__.update(env)

        exec compile(code, filename, 'exec') in m.__dict__
        self.modules[filename] = m

        return m
    
    def unload(self, m):
        filename = os.path.basename(m.__file__)
        del self.modules[filename]
        return None
    
    def reload(self, m):
        fullpath = m.__file__

        try:
            code = open(fullpath).read()
        except IOError:
            raise ImportError, 'No module named  %s' %fullpath

        env = m.__dict__
        module_class = m.__module_class__
        filename = os.path.basename(fullpath)
        m = module_class(filename)

        m.__file__ = fullpath
        m.__dict__.update(env)
        m.__module_class__ = module_class

        exec compile(code, filename, 'exec') in m.__dict__
        self.modules[filename] = m

        return m

try:
    import win32clipboard
    import win32con
except Exception, err:
    logger.warn(err)
else:
    class Clipboard:
        @staticmethod
        def getText():
            win32clipboard.OpenClipboard()
            content = win32clipboard.GetClipboardData(win32con.CF_TEXT)
            win32clipboard.CloseClipboard()
            return content
         
        @staticmethod
        def setText(str):
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_TEXT, str)
            win32clipboard.CloseClipboard()
    
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

def readPkl(pklFile):
    print DataStore.get(pklFile)

def env():
    print(base)
    
def installPython():
    base.installPython()

def configDns():
    buf = open("/etc/resolv.conf").read()
    obj = open("/etc/resolv.conf","a+")
    if "10.41.132.9" not in buf:
        obj.write("nameserver 10.41.132.9\n")
    if "10.41.70.9" not in buf:
        obj.write("nameserver 10.41.70.9\n")

def installPip():
    ret = runCmd('pip -V')
    if ret:
        base.installPythonModule('setuptools')
        base.installPythonModule('pip')

def pipInstall(module):
    if not ping("mirrors.zte.com.cn"):
        configDns()
    installPip()
    runCmd("pip install %s -i http://mirrors.zte.com.cn/pypi/simple/ --trusted-host mirrors.zte.com.cn" % module)

def createHistory():
    History.addByTime()

def startTomcat():
    ret = 0
    if os.path.exists(base.config.get('BASE','tomcat_home')):
        ret = runCmd(os.path.join(base.config.get('BASE','tomcat_home'),'bin/startup.sh'))
    return ret

def deleteEarliest(root,num,fileOrDir=None):
    files = []
    for item in os.listdir(root):
        if not fileOrDir or fileOrDir=='file':
            if os.path.isfile(item):
                path = os.path.join(root,item)
                files.append(path)
        if not fileOrDir or fileOrDir=='dir':
            if os.path.isdir(item):
                path = os.path.join(root,item)
                files.append(path)
                
    if len(files)>num:
        files.sort(key=lambda file:os.path.getmtime(file),reverse=True)
        for file in files[num:]:
            delete(file)

def startMailService():
    s = ThreadedServer(MailService, port=12299, auto_register=False)
    s.start()

def sendMail(recipient, subject, content, attach=None):
    rpyc = tryImport('rpyc')
    c=rpyc.connect('10.46.244.244',12299)
    c.root.send(recipient, subject, content, attach)
    c.close()

if __name__ == '__main__':
    if len(sys.argv)<2:
        sys.exit()
    else:
        func = eval(sys.argv[1])
        args = sys.argv[2:]
        func(*args)

    
