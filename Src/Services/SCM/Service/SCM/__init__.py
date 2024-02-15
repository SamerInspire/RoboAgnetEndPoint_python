# coding=utf8

import pyperclip as pyperclip

from Core.Utils.EnumsValues import CommonAnswers
from Core.Config import settings
from Core.Utils.UtilsFunctions import getEstNumber, ArrangeAndGetEstInfo, exitMethodWithText, sortAndGetInsertionInfo, \
    getEstablishmentInformation
from Src.Services.SCM.Utils.CMUtils import afw, ccd, \
    cdq, ct


def CMCheckService(options, infoParams, queryCenterInfo, returnValue):
    o3, O1, o4, o2 = options
    functionName = CMCheckService.__name__
    settings.userName = queryCenterInfo['userName']
    settings.genEmail = queryCenterInfo['genEmail']
    settings.ticketNo = queryCenterInfo['ticketNo']
    resultText = ''
    EstNo, LaborerNo = sortAndGetInsertionInfo(infoParams)
    print('EstNo -==> ', EstNo)
    print('LaborerNo -==> ', LaborerNo)

    if o3 or O1 or o4:

        arr = lnin(LaborerNo, O1 or o4)
        print('arr', arr)
        print('resultText ', resultText)

        if arr.startswith('**'):
            resultText += arr.replace('**', '')
        else:
            resultText = arr
            if o3:
                if len(LaborerNo) == 10 and LaborerNo[0] not in ['1']:
                    resultText += afw(LaborerNo) + '\n\n'
                else:
                    resultText += 'يرجى التأكد من إدخال رقم إقامة/حدود صحيح  \n\n'

            if O1:
                if (len(LaborerNo) == 10 and LaborerNo[0] in ['1', '2']) or len(LaborerNo) < 10:
                    resultText += ccd(LaborerNo) + '\n\n'
                else:
                    resultText += 'لا يمكن إنشاء عقد للرقم المدخل \n\n'
                print('resultText', resultText)
            if o4:
                if (len(LaborerNo) == 10 and LaborerNo[0] in ['1', '2']) or len(LaborerNo) < 10:
                    resultText += ct(LaborerNo) + '\n'
                else:
                    resultText += 'لا يمكن إنشاء طلب إنهاء علاقة تعاقدية لرقم حدود\n\n'
                    print('resultText', resultText)
    if EstNo is not None and o2:
        EstNo = getEstNumber(EstNo)
        print('EstNosss ==>', EstNo)

        estInfo = getEstablishmentInformation(EstNo)
        if estInfo is None or type(estInfo) is str:
            if resultText == '':
                returnValue[functionName] = estInfo
                return returnValue[functionName]
        else:
            code, estInfo, resultText = ArrangeAndGetEstInfo(EstNo, estInfo, resultText, False)
            resultText += '\n\n رقم المنشأة : ' + str(EstNo[0] + '-' + EstNo[1]) + ' \n^-^'

            # if changeActivity:سس
            # resultText += getChangeActivityAnswer(estInfo)
            if o2:
                resultText += cdq(estInfo) + '\n'
    else:
        if o2 and resultText == '':
            resultText = exitMethodWithText(CommonAnswers.MissingInfo.value)

    returnValue[functionName] = resultText.replace('^-^', '')
    if not settings.autoFlag:
        pyperclip.copy(returnValue[functionName])
    return returnValue


def lnin(laborerId, ContractFlag=False):
    if len(laborerId) > 10 or len(laborerId) < 10:
        if ContractFlag and len(laborerId) < 10:
            resultText = 'رقم العقد : ' + laborerId + '\n'
            return resultText
        else:
            return '**' + exitMethodWithText('يرجى تزويدنا بالرقم الهوية الصحيح')
    if laborerId[0] == '2':
        resultText = 'رقم الإقامة : ' + laborerId + '\n'
    elif laborerId[0] in ['3', '4']:
        resultText = 'رقم الحدود : ' + laborerId + '\n'
    elif laborerId[0] == '1':
        resultText = 'رقم الهوية : ' + laborerId + '\n'
    else:
        return '**' + exitMethodWithText('يرجى تزويدنا برقم الإقامة الصحيح')

    return resultText
