#!/usr/bin/env python
# codeing=utf-8

import string
import re
import subprocess

if __name__ == '__main__':
    p=subprocess.Popen(["svn","diff","-r","5:6"],stdout=subprocess.PIPE)
    out=p.stdout.read()
    print out
    
    dictdiff = {}
    difflines = []
    
    m = re.match(r'Index:\s*(\S+)', out)
    if m:
        filename = m.group(1)
    lst = out.split("\n")
    for text in lst:
        m = re.match(r'@@\s*-\d+,\d+\s*\+(\d+),(\d+)\s*@@', text)
        if m:
            startline=int(m.group(1))
            lines=int(m.group(2))
            index = lst.index(text)
            
    for text in lst[index+1:index+lines]:
        m = re.match(r'^\+.*', text)
        if m:
            print m.group()
            #print lst.index(text)
            difflines.append(startline)
        startline+=1
    dictdiff[filename]=difflines
    print dictdiff
    
    