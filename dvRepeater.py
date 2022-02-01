import sys
import utilsLib

# Default variable
outPathDir = "dbRepeatDir"


def help():
    print("Error argv, argument passed was:")
    print(sys.argv)
    print("Correct usage:\n\t./DbRepeater <model.db path> <replaceDb.txt path> [outDir path]")
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
    textModel = utilsLib.loadModel(modelTextPath)
    repLists = utilsLib.loadReplace(replaceListPath)

    utilsLib.generateDbs(textModel, repLists, outPathDir)

