import os
import re


def loadText(f_path):
    f = open(f_path, "r")
    textModel = f.read()
    f.close()
    return textModel


# Carica il file facendo di ogni linea una lista, e ogni 'tab' nella linea
# una sotto lista, considera '#' e '/' a inizio riga come commento
def loadDoubleList(f_path, minColon=0):
    f = open(f_path, "r")
    repLists = []
    for line in f:
        repLine = line.strip('\n')
        if len(repLine) > 0:
            if repLine[0] == "/" or repLine[0] == "#":
                continue
            repLine = repLine.replace("\n", "")
            line_list = repLine.split("\t")
            if len(line_list) >= minColon or minColon == 0:
                repLists.append(line_list)
    f.close()
    return repLists


def saveString(path_write, outStr):
    text_file = open(path_write, "w")
    n = text_file.write(outStr)
    text_file.close()

    if (len(outStr) != n):
        print("ATTENTION, not all string was saving in the '" + path_write + "' file")


def generateBlock(textModel, repLists):
    out = ""
    for repLine in repLists:
        newText = textModel
        for i in range(len(repLine)):
            repStr = "<rep{index}>".format(index=i)
            newText = newText.replace(repStr, repLine[i])
        out = out + newText
    print(out)
    return out


def generateFindReplace(textToReplace, frLists):
    out = textToReplace
    for sList in frLists:
        out = out.replace(sList[0], sList[1])
    return out


def get_trailing_number(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None
