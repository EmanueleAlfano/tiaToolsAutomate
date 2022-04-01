import pandas as pd
import re

# Sheet-->Data Conversion save
# From LEO
RemoteData = None
IOData = None

# From Automate
ParData = None

# Useful list
TrunkList = []

# Out data
TrunkData = None


def sheetLoad(IOexcelPath, parametricExcelPath):
    global RemoteData, IOData, ParData, TrunkList
    #####################
    # Remote sheet Load #
    #####################
    RemoteSheet = pd.read_excel(IOexcelPath, sheet_name=1, header=1)
    RemoteData = RemoteSheet[['ID LINE COMPONENT', 'IP ADDR 1']]
    RemoteData = RemoteData.dropna().reset_index(drop=True)
    IPList = list(RemoteData['IP ADDR 1'])
    ProfinetId = []
    for ip in IPList:
        bytes = ip.split('.')
        ProfinetId.append(int(bytes[-1]))
        # print(ProfinetByte)
    RemoteData['ProfinetId'] = ProfinetId

    #################
    # Io Sheet Load #
    #################

    IOSheet = pd.read_excel(IOexcelPath, sheet_name=2, header=2)
    IOData = IOSheet[['ID LINE COMPONENT', 'SW TAG', 'SIGNAL DESCRIPTION', 'I/O ADDR']]
    IOData.dropna().reset_index(drop=True)

    #########################
    # Parametric Sheet Load #
    #########################

    ParSheet = pd.read_excel(parametricExcelPath, sheet_name=0, header=0)
    ParData = ParSheet[['conv', 'utenza', 'trunk', 'Linea', 'tipo', 'Daisy Chain', 'PCT', 'IsConveyor', 'Id_Obj']]

    TrunkList = list(ParSheet['trunk'].drop_duplicates(keep='first'))


def trunkTableGen():
    global ParData, TrunkData
    trunk3D = []
    for i in TrunkList:
        trunktmp = (re.split('(\d+)', i)[0:-1])
        num = ParData[['IsConveyor', 'trunk']].loc[ParData['trunk'] == i].loc[ParData['IsConveyor'] == True]
        a = (trunktmp[0] + '_' + "%03d" % int(trunktmp[1]))  # Trunk_000 Format
        b = (trunktmp[0] + str(int(trunktmp[1])))  # Trunk0    Format
        c = (len(num))  # Conveyor Count in Trunk
        trunk3D.append([a, b, c])

    TrunkData = pd.DataFrame(trunk3D, columns=['TrunkLongName', 'TrunkName', 'N_conv'])
    return TrunkData


def digIn_PctTrunkRegion():
    global ParData, TrunkData
    col = ['trunk', 'SelAuto', 'Jog', 'Reset', 'Stop', 'DP_com']
    DIGIN_Tr_PCT = []
    for trunk in list(TrunkData['TrunkName']):
        conv = ParData[['conv']].loc[ParData['trunk'] == trunk].loc[ParData['PCT'].notnull()]
        try:
            print(conv.iat[0, 0])
            # TODO: compilare i 5 segnali bene
            DIGIN_Tr_PCT.append([trunk, conv.iat[0, 0], 0, 0, 0])
        except:
            print('noPCT')
            DIGIN_Tr_PCT.append([trunk, 0, 0, 0, 0, 0])

    print(DIGIN_Tr_PCT)
    # Creazione digIn_PctTrunkRegion table
    #TrunkPCTDIG_IN = pd.DataFrame(DIGIN_Tr_PCT, columns=col)
