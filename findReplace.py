#!/usr/bin/env python
import sys
import utilsLib

# Default variable
outPath = "findReplaced.txt"


def help():
    print("Error argv, argument passed was:")
    print(sys.argv)
    print("Correct usage:\n\tfindReplace <source.txt path> <findReplaceList.txt path> [out.txt path]")
    exit(-1)



if __name__ == '__main__':
    # Input Read
    if (len(sys.argv) < 3):
        help()
    sourcePath = sys.argv[1]
    findReplaceList = sys.argv[2]
    if (len(sys.argv) >= 4):
        outPath = sys.argv[3]

    ## Command exe
    # Data Load
    textSource = utilsLib.loadText(sourcePath)
    dList = utilsLib.loadDoubleList(findReplaceList)

    # Prendo solo le linee da 2 elementi, 1° colonna find, 2° colonna replace
    findRepList = []
    for sList in dList:
        if len(sList) == 2:
            findRepList.append(sList)

    # Execute Find Replace
    out = utilsLib.generateFindReplace(textSource, findRepList)
    # Save
    utilsLib.saveString(outPath, out)
