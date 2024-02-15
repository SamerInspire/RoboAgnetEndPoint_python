# coding=utf8

import pyperclip as pyperclip

from Core.Config import settings
from Core.Utils.UtilsFunctions import getEstNumber, ArrangeAndGetEstInfo, exitMethodWithText, sortAndGetInsertionInfo, \
    getEstablishmentInformation
from Src.Services.Sv.Utils.utils import getEstIssuesWhileIssuing, visaCheckAllCasesAnswer, \
    getCancelVisasAnswer


def VisaCheckService(options, infoParams, queryCenterInfo, returnValue):
    o1, o2, o3, o4 = options
    functionName = VisaCheckService.__name__
    settings.userName = queryCenterInfo['userName']
    settings.genEmail = queryCenterInfo['genEmail']
    settings.ticketNo = queryCenterInfo['ticketNo']

    print('infoParams -==> ', infoParams)
    EstNo, VNo = sortAndGetInsertionInfo(infoParams)
    print('EstNo -==> ', EstNo)
    print('VNo -==> ', VNo)
    if o2:
        returnValue[functionName] = visaCheckAllCasesAnswer(VNo)
        if not settings.autoFlag:
            pyperclip.copy(returnValue[functionName])
        return returnValue[functionName]


    EstNo = getEstNumber(EstNo)

    if EstNo is None:
        returnValue[functionName] = exitMethodWithText('يرجى تزويدنا برقم المنشأة الصحيح لو سمحتم')
        return returnValue[functionName]

    resultText = ' رقم المنشأة : ' + str(EstNo[0] + '-' + EstNo[1]) + ' \n^-^\n'
    returnValue[functionName] = resultText
    estInfo = getEstablishmentInformation(EstNo)
    print('estInfo', estInfo)
    if estInfo is None or type(estInfo) is str:
        returnValue[functionName] = estInfo
        return returnValue[functionName]

    if not (o4 or o3 or o2 or o1):
        return returnValue[functionName]

    code, estInfo, resultText = ArrangeAndGetEstInfo(EstNo, estInfo, resultText, False)
    if code not in ['E0000101', '00000000', 'E0000066', 'E0000067'] and o4:
        returnValue[functionName] = resultText.replace('^-^', '')
        return returnValue[functionName]

    if o1:
        resultText += getCancelVisasAnswer(estInfo)
    if o3:
        print('in here')
        resultText += getEstIssuesWhileIssuing(estInfo)
        print('resultText ', resultText)
        print('out here')

    returnValue[functionName] = resultText.replace('^-^', '')
    if not settings.autoFlag:
        pyperclip.copy(returnValue[functionName])  # resultText.replace('^_^', '')

    return returnValue


