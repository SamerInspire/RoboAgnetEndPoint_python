import pyperclip

from Core.Config import settings
from Core.SchemaBuilder.schemaUtils import isEmpty
from Core.Utils.UtilsFunctions import getEstNumber, ArrangeAndGetEstInfo, exitMethodWithText, sortAndGetInsertionInfo, \
    getEstablishmentInformation
from Src.Services.ps.Utils.Utils import getAllPrivileges


def PMCheckService(options, infoParams, queryCenterInfo, returnValue):
    o = options
    functionName = PMCheckService.__name__
    settings.userName = queryCenterInfo['userName']
    settings.genEmail = queryCenterInfo['genEmail']
    settings.ticketNo = queryCenterInfo['ticketNo']

    EstNo, lNo = sortAndGetInsertionInfo(infoParams)
    print('EstNo -==> ', EstNo)
    print('lNo -==> ', lNo)

    EstNo = getEstNumber(EstNo)

    if EstNo is None:
        returnValue[functionName] = exitMethodWithText('يرجى تزويدنا برقم المنشأة الصحيح لو سمحتم')
        return returnValue[functionName]

    if isEmpty(lNo):
        returnValue[functionName] = exitMethodWithText('يرجى تزويدنا برقم هوية المستخدم')
        return returnValue[functionName]

    resultText = ' رقم المنشأة : ' + str(EstNo[0] + '-' + EstNo[1]) + ' \n^-^\n'
    returnValue[functionName] = resultText
    estInfo = getEstablishmentInformation(EstNo)
    if estInfo is None or type(estInfo) is str:
        returnValue[functionName] = estInfo
        return returnValue[functionName]

    code, estInfo, resultText = ArrangeAndGetEstInfo(EstNo, estInfo, resultText, False)
    if o:
        if len(lNo) != 10 or lNo[0] not in ['1', '2']:
            resultText = 'يرجى تزويدنا في رقم الهوية الصحيح\n\n'

        else:
            resultText = getAllPrivileges(estInfo, lNo) #2309496-1 / 1009326784   29072-1-1015073800

    returnValue[functionName] = resultText.replace('^-^', '')
    if not settings.autoFlag:
        pyperclip.copy(returnValue[functionName])
    return returnValue



