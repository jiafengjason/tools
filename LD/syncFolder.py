import os
import hashlib
import datetime
import shutil
import json

pathFrom = 'J:\leidian'
pathTo = 'L:\leidian'
ldJson='LD.json'
ldMD5s = {}

if os.path.exists(ldJson):
    with open(ldJson,'r',encoding='utf8')as fp:
        ldMD5s = json.load(fp)

print(len(ldMD5s))

def getFileMD5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = open(filename,'rb')
    while True:
        buf = f.read(8096)
        if not buf:
            break
        myhash.update(buf)
    f.close()
    return myhash.hexdigest()

def create_file_list(path):
    for filename in os.listdir(path):
        file = path+os.sep+name
        if os.path.isdir(file):
            create_file_list(file)
        else:
            print('Calc %s MD5'% file)
            starttime = datetime.datetime.now()
            #md5 = getFileMD5(file)
            md5 = hashlib.md5(open(file,'rb').read()).hexdigest()
            endtime = datetime.datetime.now()
            print('Duration:%ds'%((endtime-starttime).seconds))
            ldMD5s[filename] = md5
    with open(ldJson,'w') as file_obj:
        json.dump(ldMD5s,file_obj)

def copy_file(srcPath,dstPath):
    for filename in os.listdir(srcPath):
        srcFile = os.path.join(srcPath,filename)
        dstFile = os.path.join(dstPath,filename)
        
        if os.path.isdir(srcFile):
            if not os.path.exists(dstFile):
                os.mkdir(dstFile)
            copy_file(srcFile,dstFile)
        else:
            srcMD5 = hashlib.md5(open(srcFile,'rb').read()).hexdigest()
            if not os.path.exists(dstFile):
                print('Copy from %s to %s' % (srcFile,dstFile))
                shutil.copyfile(srcFile, dstFile)
                ldMD5s[filename] = srcMD5
            else:
                '''
                srcMtime = os.path.getmtime(srcFile)
                dstMtime = os.path.getmtime(dstFile)
                if srcMtime!=dstMtime:
                    print('Copy from %s to %s' % (srcFile,dstFile))
                    shutil.copyfile(srcFile, dstFile)
                    #os.system('xcopy /Y "%s" "%s"' % (srcFile, dstFile))
                else:
                    print('[%s:%s] "%s"\'s MD5 already exists! ' % (srcMtime,dstMtime,dstFile))
                '''
                if srcFile in ldMD5s:
                    if srcMD5!=ldMD5s[srcFile]:
                        print('Copy from %s(%s) to %s(%s)' % (srcFile,srcMD5,dstFile,ldMD5s[srcFile]))
                        shutil.copyfile(srcFile, dstFile)
                        ldMD5s[srcFile] = srcMD5
                    else:
                        print('[*] "%s"\'s MD5 already exists! ' % dstFile)
                else:
                    print('Copy from %s(%s) to %s' % (srcFile,srcMD5,dstFile))
                    shutil.copyfile(srcFile, dstFile)
                    ldMD5s[srcFile] = srcMD5
    print('Save:%d' % len(ldMD5s))
    with open(ldJson,'w') as file_obj:
        json.dump(ldMD5s,file_obj)

if __name__ == '__main__':
    for (root, dirs, files) in os.walk(pathFrom):
        for file in files:
            if '.log' in file.lower():
                path = os.path.join(root,file)
                print(path)
                shutil.rmtree(path)
        for dir in dirs:
            if 'log' in dir.lower():
                path = os.path.join(root,dir)
                print(path)
                shutil.rmtree(path)

    for (root, dirs, files) in os.walk(pathTo):
        for file in files:
            if '.log' in file.lower():
                path = os.path.join(root,file)
                print(path)
                shutil.rmtree(path)
        for dir in dirs:
            if 'log' in dir.lower():
                path = os.path.join(root,dir)
                print(path)
                shutil.rmtree(path)

    print("Start copy_file")
    copy_file(pathFrom,pathTo)
