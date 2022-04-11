#!/usr/bin/env python


import sys
import utilsLib
import excelFunction as ex

# Default variable
outPath = "signalFind_gen.txt"
idLineComponentFilter = "\w"  # Regular Expression for all


def help():
    print("Error argv, argument passed was:")
    print(sys.argv)
    print(
        "Correct usage:\n\tsignalFind.py <IOExcel.xls path> <replaceSignal.txt path> [out.xls path] [ID LINE COMPONENT filterText (Regular Expression Sintax)]")
    print("replaceSignal.txt := First Columns ReplaceName (Find); Second Columns Description to search in IOExcel.xls")
    print("To install dependence: \n pip3 install pandas openpyxl")
    exit(-1)


if __name__ == '__main__':
    # Input Read
    if (len(sys.argv) < 3):
        help()
    IOexcelPath = sys.argv[1]
    replaceSignalPath = sys.argv[2]
    if (len(sys.argv) >= 4):
        outPath = sys.argv[3]

    # Data Load
    searchList = utilsLib.loadDoubleList(replaceSignalPath, minColon=2)

    # Sheet Data Load
    ex.sheetLoadIO(IOexcelPath)

    signalFindList = []
    for signal in searchList:
        replace = signal[0]
        if len(signal) >= 3:
            ioFilter = signal[2]
        else:
            ioFilter = "\w"
        tag = ex.signalFound([signal[1]], idLineComponentFilter, defaultTag=signal[0], ioAddrFilter=ioFilter)
        signalFindList.append([replace, tag[0]])

    # Save
    out = ""
    for line in signalFindList:
        out += line[0] + "\t" + line[1] + "\n"
    print(out)
    utilsLib.saveString(outPath, out)
