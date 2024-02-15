import pyperclip

from Core.Config import settings
from Src.Services.SCCO.Utils.utils import CheckChangeOccupationDetailsDB
from Core.Utils.UtilsFunctions import ArrangeAndGetEstInfo, exitMethodWithText, sortAndGetInsertionInfo


def CheckIdNumber(laborerId):
    if len(laborerId) != 10:
        return '**' + exitMethodWithText('يرجى تزويدنا برقم الإقامة الصحيح')
    if laborerId[0] == '2':
        resultText = 'رقم الإقامة : ' + laborerId + '\n'
    else:
        return '**' + exitMethodWithText('يرجى تزويدنا برقم الإقامة الصحيح')
    return resultText


def COService(options, infoParams, queryCenterInfo, returnValue):
    CheckCORequest = options
    functionName = COService.__name__
    settings.userName = queryCenterInfo['userName']
    settings.genEmail = queryCenterInfo['genEmail']
    settings.ticketNo = queryCenterInfo['ticketNo']
    EstNo, LaborerNo = sortAndGetInsertionInfo(infoParams)
    # print('EstNo -==> ', EstNo)
    # EstNo = getEstNumber(EstNo)
    print('LaborerNo -==> ', LaborerNo)
    resultText = ''
    if CheckCORequest:
        arr = CheckIdNumber(LaborerNo)
        print('arr', arr)
        print('resultText ', resultText)
        if arr.startswith('**'):
            resultText += arr.replace('**', '')
        else:
            resultText = CheckChangeOccupationDetailsDB(LaborerNo) + '\n\n'

    returnValue[functionName] = resultText
    if not settings.autoFlag:
        pyperclip.copy(returnValue[functionName])
        return returnValue
