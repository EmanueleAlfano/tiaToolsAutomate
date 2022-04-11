#!/usr/bin/env python

# programma per leggere su un excel e poi fare una query sullo stesso e scriverlo su un nuovo foglio excel
# parametricData costruzione del file excel dal word specifico del PLC di nostro interesse
# pip3 install pandas openpyxl


import sys
import utilsLib
import excelFunction as ex

# Default variable
outPath = "CompileTable_gen.xlsx"


def help():
    print("Error argv, argument passed was:")
    print(sys.argv)
    print("Correct usage:\n\ttableCompiling.py <IOExcel.xls path> <parametricExcel.xls path> [out.xls path]")
    print("To install dependence: \n pip3 install pandas openpyxl")
    exit(-1)


if __name__ == '__main__':
    # Input Read
    if (len(sys.argv) < 3):
        help()
    IOexcelPath = sys.argv[1]
    ParExcelPath = sys.argv[2]
    if (len(sys.argv) >= 4):
        outPath = sys.argv[3]

    # Sheet Data Load
    ex.sheetLoadIO(IOexcelPath)
    ex.sheetLoadParamExcel(ParExcelPath)

    ##################################
    # Table Generation and Save Zone #
    ##################################

    with ex.pd.ExcelWriter(outPath, mode='w') as writer:
        # TrunkData-gen Sheet Generate and Save
        ex.trunkTableGen().to_excel(writer, index=False, header=True, sheet_name='TrunkData-gen')
        # DigIn-TrunkPCT Sheet Generate and Save
        ex.digIn_PctTrunkRegion().to_excel(writer, index=False, header=True, sheet_name='DigIn-TrunkPCT')
        # DigIn-ConvInput Sheet Generate and Save
        ex.InputCONVEYOR_SEW_MOVIGEAR_Region().to_excel(writer, index=False, header=True, sheet_name='DigIn-ConvInput')
        # DigIn-ConvInput Sheet Generate and Save
        ex.DIGOut_LightOut_Region().to_excel(writer, index=False, header=True, sheet_name='DigOut-LightOutput')
