#!/usr/bin/python

from __future__ import print_function
import fileinput
import re
import sys
from sphinx import version_info as sphinx_version

##########################################

# import logging
#   
# log = logging.getLogger('')
# log.setLevel(logging.DEBUG)
# format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#   
# ch = logging.StreamHandler(sys.stdout)
# ch.setFormatter(format)
# log.addHandler(ch)

# usage:
# log.debug("debug info")
##########################################


texFile = sys.argv[1]
captionSearchString = "\caption{\DUspan"

multirowSearchPattern = re.compile("multirow{([0-9]*?)}")
foundMultirow = False
tableSearchString = "\\begin{tabulary}"
longtableSearchString = "\\begin{longtable}"
foundTable = False
hlineSearchString = "\\hline"
foundHline = False
multirowCount = 0
multirowColCount = 0


def searchMultirow(line):
    match = multirowSearchPattern.search(line)
    if match and match.lastindex > 0:
        return True, int(match.group(1), 10)

    return False, 0        


for line in fileinput.input(texFile, inplace=True): 

# Fix captions with highlighted text
# DUspan is used only for Sphinx < v1.8.5
    if line.find(captionSearchString) > -1:
        line = line.replace(captionSearchString, "\caption{\protect\DUspan")

# Add background color to table header
    if not foundTable:
        if line.find(longtableSearchString) > -1:
            foundTable = True
            # required to remove underfull warnings
            line = line.replace(longtableSearchString, longtableSearchString + "[l]")
        else:
            if line.find(tableSearchString) > -1:
                foundTable = True
    else:
        if line.find("\\end{longtable}") > -1 or line.find("\\end{tabulary}") > -1:
            foundTable = False
        else:
            # This is used only for Sphinx < v1.8.5
            # \sphinxstyletheadfamily is used now to set background color to table header cells
            if (sphinx_version[0] < 1 or (sphinx_version[0] == 1 and sphinx_version[1] < 8)):
                if line.find(hlineSearchString) > -1:
                    line = line + "\\rowcolor{tableheadercolor}"
                    foundTable = False

# Fix rowspans is required only for Sphinx <= v1.2.2
# FIXME no longer works properly since 'Default' (value column) was introduced
    if (sphinx_version[0] < 1 or (sphinx_version[0] == 1 and sphinx_version[1] <= 2)):
        if not foundMultirow:
            foundMultirow, multirowCount = searchMultirow(line)
        else:
            if not foundHline and line.find("&") > -1:
                multirowColCount += 1

            # if multirowCount > 1:
            #     if line.find("\\\\") > -1:
            #         line = line.replace("\\\\", "")

            if line.find(hlineSearchString) > -1:
                foundHline = True
                multirowCount = multirowCount - 1
                if multirowCount > 0:
                    #line = line.replace(hlineSearchString, "\\\\* \cline{2" + "-" + str(multirowColCount) + "}")
                    line = line.replace(hlineSearchString, "\cline{2" + "-" + str(multirowColCount) + "}")
                else:
                    foundMultirow, multirowCount = searchMultirow(line)
                    foundHline = False
                    multirowColCount = 0

    print(line, end='')
