import os

def loadModel(f_path):
    f = open(f_path, "r")
    textModel = f.read()
    f.close()
    return textModel


def loadReplace(f_path):
    f = open(f_path, "r")
    repLists = []
    for line in f:
        repLine = line.strip('\n')
        if repLine[0] == "/" or repLine[0] == "#":
            continue
        repLine = repLine.replace("\n", "")
        line_list = repLine.split("\t")
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

"""
repLists := Lista di liste
        <rep0> = Nome file E primo replace, nel file modello e replace tenere conto di ciò 
"""
def generateDbs(textModel, repLists, outPathDir):
    # Files save
    os.makedirs(outPathDir, exist_ok=True)
    print("The '" + outPathDir + "' directory is created!")

    for repLine in repLists:
        newText = textModel
        for i in range(len(repLine)):
            repStr = "<rep{index}>".format(index=i)
            newText = newText.replace(repStr, repLine[i])
        print(newText)
        print("#"*15)
        saveString(outPathDir + "/" + repLine[0] + ".db", newText)
    print("§" * 15)


