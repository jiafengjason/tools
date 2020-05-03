#!/usr/bin/env python
# codeing=utf-8

import string
from base import Clipboard

if __name__ == '__main__':
    cb=Clipboard()
    data=[]
    for line in cb.getText().split('\n'):
        data.append(line.lstrip('zte:'))
    test=string.join(data, '\n')
    cb.setText(test)
    
    print test
    
    
    