# -*- coding:utf-8 -*-
import os
import sys
import codecs
import locale

reload(sys)
sys.setdefaultencoding('utf-8')

def p(f):
    print '%s.%s(): %s' % (f.__module__, f.__name__, f())
    
p(sys.getdefaultencoding)
html = codecs.open('index.html', 'w', "utf-8")
#html.write(codecs.BOM_UTF8.decode("utf-8"))
html.write(u"""
<html>
<head>
  <title>中文</title>
  <style>img{float:left;margin:5px;}</style>
</head>
<body>
""".encode("utf-8").decode("gbk"))
html.write(u"""<p>body 元素的内容会显示在浏览器中。</p>""".encode("utf-8").decode("gbk"))
html.write('</body></html>')
html.close()