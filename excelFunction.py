import math

import pandas as pd
import utilsLib
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

# Out data
TrunkData = None
TrunkPCT_DIG_IN = None
InputConvSewMoviGear_DIGIN = None
DIGOut_Light = None


def sheetLoadIO(IOexcelPath):
    global RemoteData, IOData
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


def sheetLoadParamExcel(parametricExcelPath):
    global ParData
    #########################
    # Parametric Sheet Load #
    #########################

    ParSheet = pd.read_excel(parametricExcelPath, sheet_name=0, header=0)
    ParData = ParSheet[
        ['conv', 'utenza', 'trunk', 'Linea', 'tipo', 'Daisy Chain MCP', 'Daisy Chain CAL', 'PCT', 'IsConveyor',
         'Id_Obj']]


def trunkTableGen():
    global ParData, TrunkData
    TrunkList = list(ParData['trunk'].drop_duplicates(keep='first'))
    trunk3D = []
    for i in TrunkList:
        trunktmp = (re.split('(\d+)', i)[0:-1])

        # Trunk# Format
        trunkShort = (trunktmp[0] + str(int(trunktmp[1])))

        # Trovo il conveyor associato alla PCT
        conv = ParData[['conv']].loc[ParData['trunk'] == trunkShort].loc[ParData['PCT'].notnull()]
        # Se il trunk non ha associata una PCT è vuota
        if (len(conv) == 0):
            # print('noPCT')
            pctConv = "PCT_" + trunkShort
        else:
            pctConv = conv.iat[0, 0]

        # Trunk_### Format
        trunkLong = (trunktmp[0] + '_' + "%03d" % int(trunktmp[1]))

        # Conveyor Count in Trunk
        num = len(
            ParData[['conv', 'IsConveyor', 'trunk']].loc[ParData['trunk'] == i].loc[ParData['IsConveyor'] == True])

        trunk3D.append([pctConv, trunkShort, trunkLong, num])

    TrunkData = pd.DataFrame(trunk3D, columns=['conv-PCT', 'TrunkName', 'TrunkLongName', 'N_conv'])
    return TrunkData


def signalFound(descriptionList, IdLINEfilter, defaultTag="FALSE", ioAddrFilter="\w"):
    global IOData
    swTagList = []
    rows = IOData.loc[IOData['ID LINE COMPONENT'].str.contains(IdLINEfilter, case=False) == True].loc[
        IOData['I/O ADDR'].str.contains(ioAddrFilter) == True]
    for description in descriptionList:
        tag = defaultTag
        try:
            signalRow = rows.loc[IOData['SIGNAL DESCRIPTION'].str.contains(description, case=False) == True]
            tag = "\"" + signalRow['SW TAG'].iat[0] + "\""
        except Exception as e:
            if type(e) == IndexError:
                print(
                    "[signalFound] SwTag of := ('" + description + "'; '" + IdLINEfilter + "') Not found, please Check.")
            else:
                print("[signalFound] unexpected error: " + str(e))
        swTagList.append(tag)
    return swTagList


def digIn_PctTrunkRegion():
    global ParData, RemoteData, TrunkData, TrunkPCT_DIG_IN
    col = ['trunk', 'SelAuto', 'Jog', 'Reset', 'Stop', 'DP_com', 'conv']
    DIGIN_Tr_PCT = []
    notFoundTag = "FALSE"
    if TrunkData is None:
        trunkTableGen()

    for index, Row in TrunkData.iterrows():
        conv = ParData[['conv']].loc[ParData['trunk'] == Row['TrunkName']].loc[ParData['PCT'].notnull()]

        # Se il trunk non ha associata una PCT è vuota
        if (len(conv) == 0):
            # print('noPCT')
            DIGIN_Tr_PCT.append(
                [Row['TrunkName'], notFoundTag, notFoundTag, notFoundTag, notFoundTag, notFoundTag, "No-Conv"])
            print("[digIn_PctTrunkRegion] PCT of '" + Row['TrunkName'] + "' Not found, please Check.")
            continue

        # Il trunk ha un conveyr e possiamo estrarne i dati
        conv = conv.iat[0, 0]
        try:
            rowMount = [Row['TrunkName']]

            signalSearch = ["MANUAL/AUTOMATIC", "START PUSH BUTTON", "RESET PUSH BUTTON", "STOP PUSH BUTTON"]
            ret = signalFound(signalSearch, conv)
            rowMount.extend(ret)

            profinetId = RemoteData['ProfinetId'].loc[RemoteData['ID LINE COMPONENT'] == conv].iat[0]
            rowMount.extend([profinetId])

            rowMount.extend([conv])

            DIGIN_Tr_PCT.append(rowMount)
        except Exception as e:
            print(
                "[digIn_PctTrunkRegion] During extraction data of conveyor:='" + conv + "' reach unexpected error: " +
                str(e))

    # Creazione digIn_PctTrunkRegion table
    TrunkPCT_DIG_IN = pd.DataFrame(DIGIN_Tr_PCT, columns=col)
    return TrunkPCT_DIG_IN


def get_trailing_numberOfSeries(s):
    for ind, value in s.iteritems():
        m = re.search(r'\d+$', value)
        s.update(pd.Series([int(m.group()) if m else None], index=[ind]))
    return s


def pctStopMemValue(utenza, trunk):
    global ParData
    # Filtro le righe che sono conveyor
    convRows = ParData.loc[ParData['IsConveyor'] == True]
    convRowsSort = convRows.sort_values(by='utenza', key=lambda elem: get_trailing_numberOfSeries(elem))
    convRowsSort.reset_index(drop=True)

    # Testo Primo Assoluto e Ultimo Assoluto
    if convRowsSort.iloc[0]['utenza'] == utenza:
        return "FALSE"  # First Assoluto
    elif (convRowsSort.iloc[-1]['utenza'] == utenza):
        return "FALSE"  # Last Assoluto

    # Calcolo i potenziali Trunk_Next e Trunk_Prev
    myTrunkRows = convRowsSort.loc[convRowsSort['trunk'] == trunk]
    myTrunkRows.reset_index(drop=True)

    indexMyTrunkRow = TrunkData.index[TrunkData['TrunkName'] == trunk][0]
    prevTrunk = "\"" + TrunkData['TrunkName'].iloc[max(indexMyTrunkRow - 1, 0)] + "\".StopPctMem"
    nextTrunk = "\"" + TrunkData['TrunkName'].iloc[min(indexMyTrunkRow + 1, len(TrunkData) - 1)] + "\".StopPctMem"

    # In base alla logica di confine, compongo il codice
    numRow = len(myTrunkRows)
    if numRow == 1:
        return prevTrunk + " OR " + nextTrunk  # Or di Entrambi
    if myTrunkRows.iloc[0]['utenza'] == utenza:
        return prevTrunk  # First tronco
    if myTrunkRows.iloc[-1]['utenza'] == utenza:
        return nextTrunk  # Last tronco"

    # Conveyor interno a un tronco (Non su confine)
    return "FALSE"  # Nessuno


def DigIn_ConvInput_Region():
    global ParData, RemoteData, IOData, InputConvSewMoviGear_DIGIN
    # Ph= fotocellula
    col = ['utenza', 'conveyor', 'DP_com', 'safetyBreak', 'pctStopMem', 'Ph1', 'Ph2', 'GeneralSwitch',
           'DaisyChainStatus',
           'DaisyChainAllarm']

    SEWtable = []

    # Trovo subito l'interruttore generale, poichè comune a tutti
    GeneralSwitchTag = "0"
    try:
        Row = IOData.loc[
            IOData['SIGNAL DESCRIPTION'].str.contains('400VAC power supply: Disconnector Switch Status') == True]
        GeneralSwitchTag = "\"" + Row['SW TAG'].iat[0] + "\""
    except Exception as e:
        if type(e) == IndexError:
            print(
                "[InputCONVEYOR_SEW_MOVIGEAR_Region] '400VAC power supply: Disconnector Switch Status' Not found, please Check.")
        else:
            print("[InputCONVEYOR_SEW_MOVIGEAR_Region] unexpected error: " + str(e))
    # Cerco i dati di ogni utenza
    parDataFilter = ParData.loc[ParData['utenza'].notna()]

    for index, Row in parDataFilter.iterrows():
        # Utenza e Conveyor della riga
        RowMount = [Row['utenza'], Row['conv']]

        # DP_com del conveyor
        profinetId = 0
        try:
            profinetId = RemoteData['ProfinetId'].loc[RemoteData['ID LINE COMPONENT'] == Row['conv']].iat[0]
        except Exception as e:
            if type(e) == IndexError:
                print(
                    "[InputCONVEYOR_SEW_MOVIGEAR_Region] the conveyoer :'" + Row[
                        'conv'] + "' was not found in 'Remote List', please Check.")
            else:
                print("[InputCONVEYOR_SEW_MOVIGEAR_Region] unexpected error: " + str(e))

        RowMount.extend([profinetId])

        # Safety Break del conveyor
        safeBreakTag = signalFound(["SAFETY SWITCH POWER SUPPLY 400V"], Row['conv'], "TRUE")
        RowMount.extend(safeBreakTag)

        # creazione colonna pctStopMem
        pctStopMemReplace = pctStopMemValue(Row['utenza'], Row['trunk'])
        RowMount.extend([pctStopMemReplace])

        # Ph1 e Ph2
        photoTag = signalFound(["Photocell 1", "Photocell 2"], Row['conv'])
        RowMount.extend(photoTag)

        # General switch common for all
        RowMount.extend([GeneralSwitchTag])

        # Trovo in quale Daisy Chain sono
        daisyNum = 1
        if not math.isnan(Row['Daisy Chain MCP']):
            daisyFilter = "MCP_[0-9.,_]"  # Regular Expression per ammettere dopo solo numeri o spazi
            daisyNum = int(Row['Daisy Chain MCP'])
        elif not math.isnan(Row['Daisy Chain CAL']):
            daisyFilter = "MCP_CAL_[0-9.,_]"  # Regular Expression per ammettere dopo solo numeri o spazi
            daisyNum = int(Row['Daisy Chain CAL'])
        else:
            print('No Daisy for user ' + Row['utenza'] + ' in Row:=' + str(index) + ' , please check again')
            daisyNum = 0  # Non troverà nula e metterà false

        daisyListSearch = ["400VAC power supply: Status - Daisy Chain " + str(daisyNum),
                           "400VAC power supply:Circuit Breaker Alarm - Daisy Chain " + str(daisyNum)]

        daisyTag = signalFound(daisyListSearch, daisyFilter, defaultTag="TRUE")
        RowMount.extend(daisyTag)
        SEWtable.append(RowMount)

    InputConvSewMoviGear_DIGIN_unorder = pd.DataFrame(SEWtable, columns=col)
    InputConvSewMoviGear_DIGIN = InputConvSewMoviGear_DIGIN_unorder.sort_values(by='utenza', key=lambda
        elem: get_trailing_numberOfSeries(elem))
    return InputConvSewMoviGear_DIGIN


def DIGOut_LightOut_Region():
    global ParData, RemoteData, IOData, TrunkData, DIGOut_Light
    col = ['trunk', 'buzzer', 'red', 'green', 'white', 'blue', 'conv']
    notFoundTag = "// \"NotFoundTag\""
    DIGOut_Tr_PCT = []

    if TrunkData is None:
        trunkTableGen()

    # for trunk in list(TrunkData['TrunkName']):
    for index, Row in TrunkData.iterrows():
        conv = ParData[['conv']].loc[ParData['trunk'] == Row['TrunkName']].loc[ParData['PCT'].notnull()]

        # Se il trunk non ha associata una PCT è vuota
        if (len(conv) == 0):
            # print('noPCT')
            DIGOut_Tr_PCT.append(
                [Row['TrunkName'], notFoundTag, notFoundTag, notFoundTag, notFoundTag, notFoundTag, "No-Conv"])
            print("[DIGOut_LightOut_Region] PCT of '" + Row['TrunkName'] + "' Not found, please Check.")
            continue

        conv = conv.iat[0, 0]
        try:
            rowMount = [Row['TrunkName']]

            signalSearch = ['STACK LIGHT - BUZZER', 'STACK LIGHT - RED', 'STACK LIGHT - GREEN',
                            'START PUSH BUTTON LIGHT WHITE', 'RESET PUSH BUTTON LIGHT BLUE']
            ret = signalFound(signalSearch, conv, notFoundTag)
            rowMount.extend(ret)

            rowMount.extend([conv])

            DIGOut_Tr_PCT.append(rowMount)
        except Exception as e:
            print(e)

    # Creazione digIn_PctTrunkRegion table
    DIGOut_Light = pd.DataFrame(DIGOut_Tr_PCT, columns=col)
    return DIGOut_Light
