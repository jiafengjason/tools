#!/usr/bin/env python
# codeing=utf-8

from PIL import Image
import sys
from pyocr import pyocr
from pyocr import tesseract

if __name__ == '__main__':
    print tesseract.get_available_languages()
    tools = pyocr.get_available_tools()[:]
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    print("Using '%s'" % (tools[0].get_name()))
    tools[0].image_to_string(Image.open('test.png'), lang='fra',
                             builder=TextBuilder())
                             