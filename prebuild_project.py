#!/usr/bin/python

import errno
import os
import shutil
import sys
from sphinx import version_info as sphinx_version


if (sphinx_version[0] < 1 or (sphinx_version[0] == 1 and sphinx_version[1] < 8)):
    # Used for Sphinx < v1.8.5
    userConfs = ['conf_general.py', 'conf_html.py', 'conf_latex_spx10.py']
else:
    # Used for Sphinx >= v1.8.5
    userConfs = ['conf_general.py', 'conf_html.py', 'conf_latex_spx18.py']


def copy(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            print('Directory not copied. Error: %s' % e)


def copyCommonFiles():
    if sys.version_info >= (3, 5):
        sphinxdirs = next(os.walk(thisDir))[1]
    else:
        sphinxdirs = os.walk(thisDir).next()[1]

    for dirn in sphinxdirs:
        sourceDirPath = os.path.join(thisDir, dirn)
        targetDirPath = os.path.join(projectDir, dirn)
        
        if os.path.exists(targetDirPath):
            fileList = os.listdir(sourceDirPath)
            for filen in fileList:
                targetFilePath = os.path.join(targetDirPath, filen)
                sourceFilePath = os.path.join(sourceDirPath, filen)

                if not os.path.exists(targetFilePath):
                    copy(sourceFilePath, targetFilePath)
        else:
            copy(sourceDirPath, targetDirPath)


def mergeConfFile():

    with open(os.path.join(projectDir, 'conf.py'), 'a') as outFile:
        outFile.write('\n')
        for userf in userConfs:
            with open(os.path.join(thisDir, userf)) as inFile:
                for line in inFile:
                    outFile.write(line)
                outFile.write('\n')
                    

projectDir = sys.argv[1]
thisDir = os.path.dirname(os.path.realpath(sys.argv[0]))

copyCommonFiles()
mergeConfFile()
