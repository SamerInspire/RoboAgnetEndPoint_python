import pyperclip

from Core.Config import settings
from Core.SchemaBuilder.schemaUtils import isEmpty
from Core.Utils.UtilsFunctions import getEstNumber, ArrangeAndGetEstInfo, exitMethodWithText, sortAndGetInsertionInfo
from Src.Services.sm.Utils.utils import notAppearEstsCheck
from Src.Services.sm.Utils.utils import CheckPaymentRefUMService, notAppearEstsCheck


def UMCheckService(options, infoParams, queryCenterInfo, returnValue):
    notAppearEsts, CheckPaymentRef = options
    functionName = UMCheckService.__name__
    settings.userName = queryCenterInfo['userName']
    settings.genEmail = queryCenterInfo['genEmail']
    settings.ticketNo = queryCenterInfo['ticketNo']
    resultText = ''
    EstNo, lNo = sortAndGetInsertionInfo(infoParams)
    print('EstNo -==> ', EstNo)
    print('lNo -==> ', lNo)

    EstNo = getEstNumber(EstNo)

    if notAppearEsts:
        if EstNo is None or isEmpty(lNo) or len(lNo) != 10:
            returnValue[functionName] = "\n \n برجى تزويدنا برقم الهوية/الإقامة و رقم المنشأة الصحيح (-): \n \n \n \n \n "
            return returnValue[functionName]

        resultText = ' رقم المنشأة : ' + str(EstNo[0] + '-' + EstNo[1]) + ' \n^-^\n'
        returnValue[functionName] = resultText
        estInfo = getEstablishmentInformation(EstNo)
        if estInfo is None or type(estInfo) is str:
            returnValue[functionName] = estInfo + '\n\n\n\n\n'
            return returnValue[functionName]

        code, estInfo, resultText = ArrangeAndGetEstInfo(EstNo, estInfo, resultText, False)

        resultText = notAppearEstsCheck(estInfo, lNo)

    # Check Payment and "returned refunded and rejected"
    if CheckPaymentRef:
        if len(lNo) != 10 or lNo[0] not in ['1', '2']:
            resultText = 'يرجى تزويدنا في رقم الهوية الصحيح  \n\n \n\n'
        else:
            resultText = CheckPaymentRefUMService(lNo) + '\n\n'
            print('Mohammad Shurrab=.=', resultText)

    returnValue[functionName] = resultText.replace('^-^', '')
    if not settings.autoFlag:
        pyperclip.copy(returnValue[functionName])
    return returnValue
