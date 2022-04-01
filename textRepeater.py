#!/usr/bin/env python
import sys
import utilsLib

# Default variable
outPath = "textReplace_gen.txt"


def help():
    print("Error argv, argument passed was:")
    print(sys.argv)
    print("Correct usage:\n\ttextRepeater.py <model.txt path> <replace.txt path> [out.txt path]")
    exit(-1)


if __name__ == '__main__':
    # Input Read
    if (len(sys.argv) < 3):
        help()
    modelTextPath = sys.argv[1]
    replaceListPath = sys.argv[2]
    if (len(sys.argv) >= 4):
        outPath = sys.argv[3]

    ## Command exe
    # Data Load
    textModel = utilsLib.loadText(modelTextPath)
    repLists = utilsLib.loadDoubleList(replaceListPath)
    # Execute Replace
    out = utilsLib.generateBlock(textModel, repLists)
    # Save
    utilsLib.saveString(outPath, out)
