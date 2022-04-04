import math

import pandas as pd
import re

####################################
# Sheet-->DataFrame Conversion save
# From LEO
RemoteData = None
IOData = None

# From Automate
ParData = None

####################################
# Generate Here
# Useful list
TrunkList = []

# Out data
TrunkData = None
TrunkPCT_DIG_IN = None
InputConvSewMoviGear_DIGIN = None


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
    ParData = ParSheet[['conv', 'utenza', 'trunk', 'Linea', 'tipo', 'Daisy Chain MCP','Daisy Chain CAL', 'PCT', 'IsConveyor', 'Id_Obj']]

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


def signalFound(descriptionList, IDLINEfilter):
    global IOData
    swTagList = []
    rows = IOData[['ID LINE COMPONENT', 'SW TAG', 'SIGNAL DESCRIPTION']].loc[IOData['ID LINE COMPONENT'] == IDLINEfilter]
    for description in descriptionList:
        tag = "0"
        try:
            signalRow = rows.loc[IOData['SIGNAL DESCRIPTION'].str.contains(description) == True]
            tag = "\"" + signalRow['SW TAG'].iat[0] + "\""
        except Exception as e:
            print(e)
        swTagList.append(tag)
    return swTagList


def digIn_PctTrunkRegion():
    global ParData, RemoteData, TrunkData,TrunkPCT_DIG_IN
    col = ['trunk', 'SelAuto', 'Jog', 'Reset', 'Stop', 'DP_com', 'conv']
    DIGIN_Tr_PCT = []

    if TrunkData is None:
        trunkTableGen()

    for trunk in list(TrunkData['TrunkName']):
        conv = ParData[['conv']].loc[ParData['trunk'] == trunk].loc[ParData['PCT'].notnull()]

        # Se il trunk non ha associata una PCT è vuota
        if (len(conv) == 0):
            #print('noPCT')
            DIGIN_Tr_PCT.append([trunk, 0, 0, 0, 0, 0, "No-Conv"])
            continue

        # Il trunk ha un conveyr e possiamo estrarne i dati
        conv = conv.iat[0, 0]
        try:
            rowMount = [trunk]

            signalSearch = ["MANUAL/AUTOMATIC", "START PUSH BUTTON", "RESET PUSH BUTTON", "STOP PUSH BUTTON"]
            ret = signalFound(signalSearch, conv)
            rowMount.extend(ret)

            profinetId = RemoteData['ProfinetId'].loc[RemoteData['ID LINE COMPONENT'] == conv].iat[0]
            rowMount.extend([profinetId])

            rowMount.extend([conv])

            DIGIN_Tr_PCT.append(rowMount)
        except Exception as e:
            print(e)

    # Creazione digIn_PctTrunkRegion table
    TrunkPCT_DIG_IN = pd.DataFrame(DIGIN_Tr_PCT, columns=col)
    return TrunkPCT_DIG_IN


def InputCONVEYOR_SEW_MOVIGEAR_Region():
    global ParData, RemoteData, IOData
    # Ph= fotocellula
    col = ['utenza', 'conveyor', 'DP_com', 'safetyBreak', 'Ph1', 'Ph2', 'GeneralSwitch', 'DaisyChainStatus',
           'DaisyChainAllarm']

    GeneralSwitchTag = "0"

    try:
        Row = IOData.loc[IOData['SIGNAL DESCRIPTION'].str.contains('400VAC power supply: Disconnector Switch Status') == True]
        GeneralSwitchTag = "\"" + Row['SW TAG'].iat[0] + "\""
    except Exception as e:
        print(e)

    print(GeneralSwitchTag)

    #SEWtable=[]
    a = ParData.loc[ParData['utenza'].notna()]
    print(a)

    for index,Row in a.iterrows() :
        print(index,Row['Daisy Chain MCP'])
        print(type(Row), type(Row['Daisy Chain MCP']))

        RowMount = [Row['utenza'],Row['conv']]

        print(math.isnan(Row['Daisy Chain MCP']))
        if  not math.isnan(Row['Daisy Chain MCP']):
            print('ok')
        else:
            print('no ok')



    # InputConvSewMoviGear_DIGIN = pd.DataFrame(, columns=col)


