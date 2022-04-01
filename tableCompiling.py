#!/usr/bin/env python

# programma per leggere su un excel e poi fare una query sullo stesso e scriverlo su un nuovo foglio excel
# parametricData costruzione del file excel dal word specifico del PLC di nostro interesse
# pip3 install dipendenza di pandas pip3 install pandas
# pip3 install pandas openpyxl


import sys
import utilsLib
import excelFunction as ex
import pandas as pd
import re

# Default variable
outPath = "CompileTable_gen.xlsx"


def help():
    print("Error argv, argument passed was:")
    print(sys.argv)
    print("Correct usage:\n\ttableCompiling.py <IOexcel.xls path> <parametricExcel.xls path> [out.xls path]")
    exit(-1)


if __name__ == '__main__':
    # Input Read
    if (len(sys.argv) < 3):
        help()
    IOexcelPath = sys.argv[1]
    parametricExcelPath = sys.argv[2]
    if (len(sys.argv) >= 4):
        outPath = sys.argv[3]

    # Remote sheet Load

    RemoteSheet = pd.read_excel(IOexcelPath, sheet_name=1, header=1)
    # RemoteData nuovo foglio con tutti i dati utili alla compilazione del TIA
    RemoteData = RemoteSheet[['ID LINE COMPONENT', 'IP ADDR 1']]
    RemoteData = RemoteData.dropna().reset_index(drop=True)

    IPList = list(RemoteData['IP ADDR 1'])
    ProfinetByte = []
    for ip in IPList:
        byte = ip.split('.')
        ProfinetByte.append(int(byte[-1]))
        # print(ProfinetByte)

    RemoteData['ProfinetLastByte'] = ProfinetByte

    # print(RemoteData)

    ##SheetLoad

    # apriamo il file e ne prendiamo il foglio numero 1 (poiché il progressivo segue l'array che inizi da zero) nominato L278 Io List, header=2 La riga di nostra interesse
    IOSheet = pd.read_excel(IOexcelPath, sheet_name=2, header=2)

    # IOData
    IOData = IOSheet[['ID LINE COMPONENT', 'SW TAG', 'SIGNAL DESCRIPTION', 'I/O ADDR']]
    IOData = IOData.dropna().reset_index(drop=True)

    # Trunk sheet generate

    parametricSheet = pd.read_excel(parametricExcelPath, sheet_name=0, header=0)
    parametricData = parametricSheet[
        ['conv', 'utenza', 'trunk', 'Linea', 'tipo', 'Daisy Chain', 'PCT-allignment', 'IsConveyor', 'Id_Obj']]

    # eliminazione riche con lo stesso trunk
    TrunkList = list(parametricData['trunk'].drop_duplicates(keep='first'))

    trunk3D = []
    for i in TrunkList:
        trunktmp = (re.split('(\d+)', i)[0:-1])
        num = parametricData[['IsConveyor', 'trunk']].loc[parametricData['trunk'] == i].loc[
            parametricData['IsConveyor'] == True]
        a = (trunktmp[0] + '_' + "%03d" % int(trunktmp[1]))
        b = (trunktmp[0] + str(int(trunktmp[1])))
        c = (len(num))
        trunk3D.append([a, b, c])

    # NewTable_trunkSheet

    TrunkData = pd.DataFrame(trunk3D, columns=['TrunkLongName', 'TrunkName', 'N_conv'])

    TrunkData.to_excel(outPath, index=False, header=True)

    # Conv Data Sheet Generate
    col = ['trunk', 'SelAuto', 'Jog', 'Reset', 'Stop', 'DP_com']
    TrunkPCTDIG_IN = pd.DataFrame(TrunkData, columns=col)
