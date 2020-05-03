#!/usr/bin/env python
# codeing=utf-8

import os
from PIL import Image
import sys
from pyocr import pyocr
from pyocr import tesseract

TESSDATA_POSSIBLE_PATHS = [
    "/usr/local/share/tessdata",
    "/usr/share/tessdata",
    "/usr/share/tesseract/tessdata",
    "/usr/local/share/tesseract-ocr/tessdata",
    "/usr/share/tesseract-ocr/tessdata",
    "/app/vendor/tesseract-ocr/tessdata",  # Heroku
    "/opt/local/share/tessdata",  # OSX MacPorts
    "C:\Users\Administrator\AppData\Local\Tesseract-OCR\\tessdata",
]

TESSDATA_EXTENSION = ".traineddata"

def get_available_languages():
    """
    Returns the list of languages that Tesseract knows how to handle.

    Returns:
        An array of strings. Note that most languages name conform to ISO 639
        terminology, but not all. Most of the time, truncating the language
        name name returned by this function to 3 letters should do the trick.
    """
    langs = []
    for dirpath in TESSDATA_POSSIBLE_PATHS:
        if not os.access(dirpath, os.R_OK):
            continue
        for filename in os.listdir(dirpath):
            if filename.lower().endswith(TESSDATA_EXTENSION):
                lang = filename[:(-1 * len(TESSDATA_EXTENSION))]
                langs.append(lang)
    return langs
    
if __name__ == '__main__':
    print get_available_languages()
    tools = pyocr.get_available_tools()[:]
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    print("Using '%s'" % (tools[0].get_name()))
    tools[0].image_to_string(Image.open('test.png'), lang='fra',
                             builder=TextBuilder())
                             