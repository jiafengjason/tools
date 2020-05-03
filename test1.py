#!/usr/bin/env python
# codeing=utf-8

#使用pickle模块从文件中重构python对象

import pprint, pickle

pkl_file = open('data.pkl', 'rb')

data1 = pickle.load(pkl_file)
print data1
pprint.pprint(data1)

print "%%%%%%%%%%%%%"

data2 = pickle.load(pkl_file)
pprint.pprint(data2)

pkl_file.close()
    
    
    