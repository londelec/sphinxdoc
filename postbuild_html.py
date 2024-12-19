#!/usr/bin/python

from __future__ import print_function
from genericpath import isfile
import fileinput
import os
import shutil
import sys
import warnings
import re
import base64

rootdir = sys.argv[1]
targetFileName = sys.argv[2]
tempdir = sys.argv[3]

sourceFilePath = os.path.join(rootdir, "index.html")
destFilePath = os.path.join(rootdir, targetFileName + ".html")

sys.path.append(os.path.join(os.getcwd(), tempdir))
import conf

staticFilesDir = "_static"
imagesDir = "_images"

cssStyles = '<style type="text/css">'
jsScripts = '<script type="text/javascript">'
imageFiles = []

cssFiles = [
    'default.css',
    'pygments.css',
    'bootstrap.min.css',
    'site.css'
]

jsFiles = [
    'jquery.js',
    'bootstrap.min.js',
    'singlehtml.js',
    'site.js'
]


def encodebase64(filePath, prefix):
    with open(filePath, "rb") as f:
        fileContents = f.read()
        encoded = base64.b64encode(fileContents)
        if sys.version_info >= (3, 5):
            encoded = str(encoded, "utf-8")
        return prefix + encoded

# read file contents and remove trailing tabs and whitespaces from the begining of each line
def readfile(filePath):
    result = ''
    if(isfile(filePath)):
        with open(filePath, 'r') as f:
            fileContents = f.read()
            for sline in fileContents.splitlines():
                whitespace = re.compile('^[\t ]*')
                sline = whitespace.sub('', sline)
                if sline == '':
                    continue;
                #print('DEBUG: empty line', sline)
                result += sline + '\n'
    return result

# get list of image files
for root, directories, files in os.walk(os.path.join(rootdir, imagesDir)):
    for filename in files:
        filepath = os.path.join(root, filename)
        imageFiles.append(filepath)

# merge css styles
for fileName in cssFiles:
    filePath = os.path.join(rootdir, staticFilesDir, fileName)
    cssStyles += readfile(filePath)

"""
for key in cssVariables:
    cssStyles = cssStyles.replace('%' + key + '%', getattr(conf, key, ''))
"""
cssStyles += '</style>'


# merge js scripts
for fileName in jsFiles:
    filePath = os.path.join(rootdir, staticFilesDir, fileName)
    jsScripts += readfile(filePath)

jsScripts += '</script>'


# walk html file
for line in fileinput.input(sourceFilePath, inplace=True):

    # Remove css stylesheet links
    if line.find('rel="stylesheet"') > -1:
        continue

    # Remove js script links
    # FIXME has to be changed for Sphinx v5.3.0
    if (line.find('<script type="text/javascript"') > -1) and (line.find('src=') > -1):
        continue

    # Include inline css and js in page header
    if line.find('</head>') > -1:
        line = cssStyles + jsScripts + line

    # Replace logo.png with base64 value
    if line.find('src="_static/logo.png"') > -1:
        line = line.replace('_static/logo.png', encodebase64(os.path.join(rootdir, staticFilesDir, 'logo.png'), 'data:image/png;base64,'))

    # Replace favicon with base64 value
    if line.find('href="_static/favicon.ico"') > -1:
        line = line.replace('_static/favicon.ico', encodebase64(os.path.join(rootdir, staticFilesDir, 'favicon.ico'), 'data:image/x-icon;base64,'))

    # Replace png images with base64 values
    for filePath in imageFiles:
        searchPath = filePath.replace(rootdir + '/', '')
        if line.find(searchPath) > -1:
            fileExt = searchPath[(len(searchPath) - 4):]
            if (fileExt == '.svg'):
                startIndex = line.find('<img')
                if startIndex > -1:
                    endIndex = line.find('/>')
                    if endIndex > -1:
                        #print('DEBUG: ext=', fileExt)
                        line = line[:startIndex] + readfile(filePath) + line[(endIndex + 2):]
            elif (fileExt == '.png'):
                line = line.replace(searchPath, encodebase64(filePath, 'data:image/png;base64,'))
            break

    # fix references
    if line.find('href="index.html#') > -1:
        line = line.replace('href="index.html#', 'href="#')

    print(line, end='')

#remove unneeded files
shutil.rmtree(os.path.join(rootdir, staticFilesDir))
shutil.rmtree(os.path.join(rootdir, imagesDir))
os.remove(os.path.join(rootdir, 'objects.inv'))
os.remove(os.path.join(rootdir, '.buildinfo'))

#rename output file
os.rename(sourceFilePath, destFilePath)
