#!/usr/bin/env python
import sys
import utilsLib

# Default variable
outPath = "filledList-gen.txt"


def help():
    print("Error argv, argument passed was:")
    print(sys.argv)
    print("Correct usage:\n\tlistFiller.py <baseText> <findReplaceList.txt path> [out.txt path]")
    print(
        "findReplaceList.txt := First Columns DifferentName; Second Columns have to contain at the end of the string the index")
    exit(-1)


if __name__ == '__main__':
    # Input Read
    if (len(sys.argv) < 3):
        help()
    baseText = sys.argv[1]
    replaceListPath = sys.argv[2]
    if (len(sys.argv) >= 4):
        outPath = sys.argv[3]

    # Data Load
    holeList = utilsLib.loadDoubleList(replaceListPath, minColon=2)
    holeList.sort(key=lambda elem: utilsLib.get_trailing_number(elem[1]))

    # Command Exe
    nextSetPtr = 0
    startIndex = utilsLib.get_trailing_number(holeList[nextSetPtr][1])
    endIndex = utilsLib.get_trailing_number(holeList[-1][1])

    filledList = []
    for i in range(startIndex, endIndex + 1):
        if i != utilsLib.get_trailing_number(holeList[nextSetPtr][1]):
            filledList.append(baseText + str(i))
        else:
            filledList.append(holeList[nextSetPtr][0])
            nextSetPtr += 1

    # Save
    out = "\n".join(filledList)
    print(out)
    utilsLib.saveString(outPath, out)
