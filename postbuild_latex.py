#!/usr/bin/python

import os
import sys

rootdir = sys.argv[1]
targetFileName = sys.argv[2]

sourceFilePath = os.path.join(rootdir, "output.pdf")
destFilePath = os.path.join(rootdir, targetFileName + ".pdf")

#rename output file
os.rename(sourceFilePath, destFilePath)
