import pyperclip

from Core.Config import settings
from Core.SchemaBuilder.schemaUtils import isEmpty
from Core.Utils.UtilsFunctions import getEstNumber, ArrangeAndGetEstInfo, exitMethodWithText, sortAndGetInsertionInfo, \
    getEstablishmentInformation
from Src.Services.se.Utils.Utils import CheckChangeSponsorDetailsDB, ValidateEstNatPercentage


def ETService(options, infoParams, queryCenterInfo, returnValue):
    o5, o4 = options
    functionName = ETService.__name__
    settings.userName = queryCenterInfo['userName']
    settings.genEmail = queryCenterInfo['genEmail']
    settings.ticketNo = queryCenterInfo['ticketNo']
    resultText = ''
    EstNo, LaborerNo = sortAndGetInsertionInfo(infoParams)
    print('EstNo -==> ', EstNo)
    print('LaborerNo -==> ', LaborerNo)
    EstNo = getEstNumber(EstNo)

    if o5 or o4:
        arr = CheckLabNumber(LaborerNo)
        print('arr', arr)
        print('resultText ', resultText)
        if arr.startswith('**'):
            resultText += arr.replace('**', '')
        else:
            resultText = arr
            if o5:
                resultText += '\n'+CheckChangeSponsorDetailsDB(LaborerNo) + '\n\n'
                #M@!
                print('Mohammad>>>>>>',resultText)
            if o4:
                if EstNo is None:
                    returnValue[functionName] = exitMethodWithText('يرجى تزويدنا برقم المنشأة الصحيح لو سمحتم')
                    return returnValue[functionName]
                if isEmpty(LaborerNo):
                    returnValue[functionName] = exitMethodWithText('يرجى تزويدنا برقم الهوية/الإقامة')
                    return returnValue[functionName]
                resultText += ' رقم المنشأة : ' + str(EstNo[0] + '-' + EstNo[1]) + ' \n\n'
                returnValue[functionName] = resultText
                estInfo = getEstablishmentInformation(EstNo)
                if estInfo is None or type(estInfo) is str:
                    returnValue[functionName] = estInfo
                    return returnValue[functionName]
                code, estInfo, resultText = ArrangeAndGetEstInfo(EstNo, estInfo, resultText, False)
                resultText += ValidateEstNatPercentage(estInfo, LaborerNo)
    returnValue[functionName] = resultText
    if not settings.autoFlag:
        pyperclip.copy(returnValue[functionName])
        return returnValue


def CheckLabNumber(laborerId):
    if len(laborerId) != 10:
        return '**' + exitMethodWithText('يرجى تزويدنا برقم الإقامة الصحيح')
    if laborerId[0] == '2':
        resultText = 'رقم الإقامة : ' + laborerId + '\n'
    else:
        return '**' + exitMethodWithText('يرجى تزويدنا برقم الإقامة الصحيح')

    return resultText
