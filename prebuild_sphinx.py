#!/usr/bin/python

# TODO rewrite include-file directive as sphinx plugin.
# TODO rewrite include-global directive as sphinx plugin.

from __future__ import print_function
import fileinput
import os
import re
import shutil
import shlex
import sys
import warnings
from genericpath import isfile
from collections import deque

rootdir = sys.argv[1]
arguments = sys.argv[2:]

includeFileSearchString = ".. include-file::"
includeFilePlaceholder = ":include-arg:"

#includeGlobalSearchString = ".. include-global::"
#includeGlobalPlaceholder = ":include-global:"

colspecSearchString = ":spec:"

maxReparseCount = 10
#globalPlaceholdersDict = {}
#references = {}

lineBuffer = deque(['', '', ''])

def walkSourceFiles(walkFileFn):

    reparseFile = False

    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            if file.endswith(".rst"):
                filePath = os.path.join(root, file)
                if(isfile(filePath)):

                    # reparse file if needed
                    if sys.version_info >= (3, 5):
                        for x in range(maxReparseCount):
                            reparseFile = walkFileFn(filePath)
                            if not reparseFile:
                                break
                    else:
                        for x in xrange(maxReparseCount):
                            reparseFile = walkFileFn(filePath)
                            if not reparseFile:
                                break


def walkLines(filePath, walkLineFn):

    for line in fileinput.input(filePath, inplace=True):
        updateLineBuffer(line)
        line = walkLineFn(line)
        print(line, end='')

def updateLineBuffer(line):
    lineBuffer.pop()
    lineBuffer.appendleft(line)

def applyIncludeFiles(filePath):

    fileChanged = False

    for line in fileinput.input(filePath, inplace=True):
        if line.strip().startswith(includeFileSearchString):
            fileChanged = True
            line = getIncludeFileReplacement(line, filePath)

        print(line, end='')

    return fileChanged

def getIncludeFileReplacement(line, sourceFile):

    result = ""
    params = shlex.split(line)[1:]

    # check if content have to be excluded
    if len(params) > 2:
        if params[2] != "":
            if len(arguments) > 0:
                if arguments[0] != params[2]:
                    return result
            else:
                return result

    # get content from included file
    if len(params) > 1:
        filePath = os.path.join(rootdir, params[1])
        if(isfile(filePath)):
            f = open(filePath, 'r')
            result = f.read()
            f.close()
        else:
            warnings.warn("'" + sourceFile + "': Include file '" + filePath + "' not found", stacklevel=3)
            return result

    # replace placeholders with values
    if len(params) > 3:
        for index, param in enumerate(params[3:]):
            placeholder = includeFilePlaceholder + "`" + str(index + 1) + "`"
            result = result.replace(placeholder, param)

    return result

def updateTableSpec(filePath):

    for line in fileinput.input(filePath, inplace=True):

        # search for ":spec:"
        if line.find(colspecSearchString) > -1:
            if sys.version_info >= (3, 5):
                # FIXME this is now broken, since Python 3.11 (used with Sphinx v5.3.0)
                line = re.sub('{([0-9.]*?)}', r'{\dimexpr \1\linewidth-2\\tabcolsep-2\\arrayrulewidth}', line)
            else:
                line = re.sub('{([0-9.]*?)}', r'{\dimexpr \1\linewidth-2\\tabcolsep-2\\arrayrulewidth}', line)

        print(line, end='')

    return False

"""
def collectDefinedGlobalPlaceholders(filePath):

    for line in fileinput.input(filePath, inplace=True):

        # search for global include directive defined placeholders
        if line.strip().startswith(includeGlobalSearchString):
            params = shlex.split(line)
            if len(params) > 3:
                globalPlaceholdersDict[params[2]] = params[3]

            # delete global include directive defined placeholders
            continue

        print(line, end='')

    return False

def applyGlobalPlaceholders(filePath):

    for line in fileinput.input(filePath, inplace=True):
        if line.find(includeGlobalPlaceholder) > -1:
            for key, value in globalPlaceholdersDict.iteritems():
                placeholder = includeGlobalPlaceholder + "`" + key + "`"
                line = line.replace(placeholder, value)

        print(line, end='')

    return False

def collectReferenceIds(filePath):
    walkLines(filePath, findReferenceIds)

def collecReferenceTitles(filePath):
    walkLines(filePath, findReferenceTitles)

def setReferenceTitles(filePath):
    walkLines(filePath, applyReferenceTitles)

def findReferenceIds(line):

    index = line.find(":ref:`<ref-")

    while (index > -1):
        endIndex = line.find(">", index)
        reference = line[(index+7):endIndex]
        references[reference] = '#'
        index = line.find(":ref:`<ref-", endIndex)

    return line

def findReferenceTitles(line):

    index = lineBuffer[2].find(".. _ref-")

    if index > -1 and lineBuffer[1].strip() == "":
        reference = getReferenceFromLabel(lineBuffer[2])
        title = getReferenceTitle(lineBuffer[0])

        if reference in references:
            references[reference] = title

    return line

def applyReferenceTitles(line):

    index = line.find(":ref:`<ref-")

    while (index > -1):
        endIndex = line.find(">", index)
        reference = line[(index+7):endIndex]

        if reference in references:
            placeholder = ":ref:`<" + reference + ">`"
            value = ":ref:`" + references[reference] + "<" + reference + ">`"
            line = line.replace(placeholder, value)

        index = line.find(":ref:`<ref-", endIndex)

    return line

def getReferenceFromLabel(line):

    label = line.strip();
    index = label.find("ref-")
    reference = ""

    if index > -1:
        reference = label[index:-1]

    return reference

def getReferenceTitle(line):

    title = line.strip()

    if title.startswith(":xmlref:"):
        title = title[9:-1]

    return title
"""

walkSourceFiles(applyIncludeFiles)
walkSourceFiles(updateTableSpec)
#walkSourceFiles(collectDefinedGlobalPlaceholders)
#walkSourceFiles(applyGlobalPlaceholders)
#walkSourceFiles(collectReferenceIds)
#walkSourceFiles(collecReferenceTitles)
#walkSourceFiles(setReferenceTitles)
