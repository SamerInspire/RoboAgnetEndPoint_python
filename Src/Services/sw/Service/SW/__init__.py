# coding=utf8
import datetime
import datetime as datetimes

import pyperclip as pyperclip

from Core.Config import settings
from Core.Config.Config import getConnectionQiwa
from Core.GenralApis import getPIA
from Core.SchemaBuilder.schemaUtils import isEmpty
from Core.Utils.EnumsValues import AllQueriesEnum, APIsEnum
from Core.Utils.UtilsFunctions import getEstNumber, ArrangeAndGetEstInfo, exitMethodWithText, sortAndGetInsertionInfo, \
    getEstablishmentInformation
from Src.Services.sw.Service.Utils.Enums import SadadAnswers, IndebtAnswers, SadadLastStatus
from Src.Services.sw.Service.Utils.Utils import getFinancialExemptionAnswer, CheckWPInHRSD


def getSadadInfo(idType, LaborerId, manual=False):
    if idType == 'TransId':
        query = AllQueriesEnum.SadadDetails.value.replace('{{BillNumber}}',
                                                          'PK_Service_TransactionId in (\'' + LaborerId + '\'')
    elif idType == 'BillNo':
        query = AllQueriesEnum.SadadDetails.value.replace('{{BillNumber}}', 'BillNumber in (\'' + LaborerId + '\'')
    else:
        query = AllQueriesEnum.SadadDetails.value.replace('{{BillNumber}}', AllQueriesEnum.TransIdFormWp.value)
    SadadInfo = getPIA(
        {'bodyJsons': APIsEnum.query_center_api_custom,
         'query': query, 'valsToReplace': {'LaborerId': LaborerId, 'IdNoBorderNo': idType}})
    if SadadInfo is None or len(SadadInfo) == 0:
        return SadadAnswers.NoIndo.value
    SadadInfo = SadadInfo[0]
    print("SadadInfo ====> ", SadadInfo)
    result = SadadAnswers.SadadInfo.value.replace('{{sadadNumber}}', str(SadadInfo['BillNumber'])).replace('{{Status}}',
                               SadadLastStatus.__getitem__('Status' + str(SadadInfo['FK_Service_LastServiceStatusId'])).value) + '\n'
    print("SadadInfo ====> ", SadadInfo)
    TransText = ''
    if SadadInfo is not None and idType != '':
        PKServiceTransactionId = SadadInfo['PK_Service_TransactionId']
        WPNormalLaborers = getPIA(
            {'bodyJsons': APIsEnum.query_center_api_custom,
             'query': AllQueriesEnum.WPNormalLaborer.value,
             'valsToReplace': {'transactionid': PKServiceTransactionId}})

        WPPenalityLaborers = getPIA(
            {'bodyJsons': APIsEnum.query_center_api_custom,
             'query': AllQueriesEnum.WPPenalityLaborer.value,
             'valsToReplace': {'transactionid': PKServiceTransactionId}})

        if WPPenalityLaborers is not None and len(WPPenalityLaborers):
            TransText += '  - تجديد رخصة عمالة غير منتظمة ' + '\n'
            for idx, WPPenalityLaborer in enumerate(WPPenalityLaborers):
                wpEndDate = datetime.datetime.strptime(str(WPPenalityLaborer['WPEndDate'])[:10], "%Y-%m-%d")
                TransText += '    ' + str(idx + 1) + '- رقم الإقامة/الحدود : ' + str(
                    WPPenalityLaborer['IdOrBorderNo']) \
                             + ' تم التجديد من تاريخ ' + str(WPPenalityLaborer['WPStartDate'])[:10] \
                             + ' إلى تاريخ ' + str(WPPenalityLaborer['WPEndDate'])[:10] + '\n'
                if wpEndDate < datetime.datetime.today():
                    TransText += '        تنويه : هذه الرخصة إنتهت' + '\n'

        if WPNormalLaborers is not None and len(WPNormalLaborers):
            TransText += '  - تجديد رخصة عمالة منتظمة ' + '\n'
            for idx, WPNormalLaborer in enumerate(WPNormalLaborers):
                wpEndDate = datetime.datetime.strptime(str(WPNormalLaborer['WPEndDate'])[:10], "%Y-%m-%d")

                TransText += '    ' + str(idx + 1) + '- رقم الإقامة/الحدود : ' + str(
                    WPNormalLaborer['IdOrBorderNo']) \
                             + ' تم التجديد من تاريخ ' + str(WPNormalLaborer['WPStartDate'])[:10] \
                             + ' إلى تاريخ ' + str(WPNormalLaborer['WPEndDate'])[:10] + '\n'
                if wpEndDate < datetime.datetime.today():
                    TransText += '        تنويه : هذه الرخصة إنتهت' + '\n'

                if str(WPNormalLaborer['IsFinalExit']) != '0' and not isEmpty(WPNormalLaborer['IsFinalExit']):
                    TransText += '        يوجد على الموظف خروج نهائي بإجمالي رسوم الخروج النهائي ' + \
                                 WPNormalLaborer['TotalLaborerWPFeesForFinalExit'] \
                                 + ' تاريخ انتهاء رخصة الخروج النهائي ' + WPNormalLaborer[
                                     'WPEndDateForFinalExit'] + '\n'

        TransText += '\n\n'
    return result + '\n\n' + TransText
    # if iqameh in mol != iqameh in NIC
    # result += '\n \n ****** \n \n الإقامة في وزارة الموارد البشرية تنتهي بتاريخ {{}} \n وفي وزارة الداخلية الإقامة تنتهي بتاريخ {{}}
    # if iqameh in mol > iqameh in NIC
    # \n مشكلة الإقامة في وزارة الموارد أكبر من الداخلية يرجى رفع تذكرة على QiwaSupport '
    # return 'يرجى رفع التذكرة على البورد '
    # else
    # تحديث
    # if SadadInfo is not None and SadadInfo['FK_Service_LastServiceStatusId'] == '3':
    #
    #     # check Iqameh(NIC) -- case valid for 60 days and more
    #
    #     # return  SadadAnswers.IqamehValidFor60Days.value.replace('',str(iqamehNo))
    #     # elif         # check WP(MOL) valid for 2 month min and Iqameh expired for more than 2 months or more :
    #
    #     if manual:
    #         manualCaseStatus3('')
    #     else:
    #         return result + '\n\n****\n\n  يرجى إدخال هذه الحالة إلى المنايوال للتحقق من مشاكل في الربط \n \n tag: رخص_ربط '
    #     # else: wp valid less than 2 month or expired and iqameh expired or valid for less than 60 days
    #     # SadadInfo['wpEndDt'] == wp[endDt] no issue should c  :
    #     # iqamehExpDt == wpExpDt
    #     # return ' لا يوجد مشاكل'
    #     # else:-
    #     # return ' مجدد اقامة'
    # else:
    #     # if wp valid for less than 2 month and iqameh valid for less than that
    #     return SadadAnswers.IqamehAndWPEqualization.value.replace('', str('iqamehNo'))
    #     # elsif # iqamehExpDt == wpExpDt
    #     #             #return ' لا يوجد مشاكل'
    #
    # return result


def manualCaseStatus3(iqamehNo):
    # case manual return None (no issue)
    return SadadAnswers.ManualNoIssues.value.replace('', str(iqamehNo))
    # case manual Good


def sadadCheck(EstNo):
    LaborerId = EstNo.replace('-', '')

    if LaborerId[:1] == '2' and len(LaborerId) == 10:
        resultText = 'رقم الإقامة : ' + LaborerId + '\n'
        idType = 'idNo'
    elif LaborerId[:1] in ['3', '4'] and len(LaborerId) == 10:
        resultText = 'رقم الحدود : ' + LaborerId + '\n'
        idType = 'BorderNo'
    elif len(LaborerId) == 14:
        resultText = 'رقم السداد : ' + LaborerId + '\n'
        idType = 'BillNo'
    else:
        resultText = 'رقم المعاملة : ' + LaborerId + '\n'
        idType = 'TransId'
    resultText += '\n\n' + getSadadInfo(idType, LaborerId)
    return resultText


def getIndebtednessDetails(laborerId, EstNo):
    cursorQiwa = getConnectionQiwa().cursor()

    indebtednessDetails = getPIA({'bodyJsons': APIsEnum.query_center_api_custom,
                                  'query': AllQueriesEnum.LaborIndebtednessDetails.value,
                                  'valsToReplace': {'LaborerId': laborerId}})
    print('indebtDetials ===> ', indebtednessDetails)
    if indebtednessDetails is not None:
        indebtednessDetails = indebtednessDetails[0]
    transferRequestDetails = cursorQiwa.execute(
        AllQueriesEnum.LastETDetails.value.replace('{{LaborerId}}', laborerId)).fetchone()
    print('etDetails ==> ', transferRequestDetails)
    if transferRequestDetails is None:
        transferRequestDetails = cursorQiwa.execute(
            AllQueriesEnum.TransOutQiwa.value.replace('{{LaborerId}}', laborerId), DBName='HRSD').fetchone()
    if transferRequestDetails is not None:

        if not transferRequestDetails[8]:  # check if not run away

            lastModifiedDate = datetimes.datetime.strptime(str(transferRequestDetails[6])[:10], "%Y-%m-%d")
            Last_Modified_Date_69 = datetimes.datetime.strptime('2022-06-09', "%Y-%m-%d")
            Last_Modified_Date_91 = datetimes.datetime.strptime('2022-09-01', "%Y-%m-%d")

            if indebtednessDetails is not None:
                ServiceStartDate = datetimes.datetime.strptime(str(indebtednessDetails['ServiceStartDate'])[:10],
                                                               "%Y-%m-%d")
                IqamaExpirationDate = datetimes.datetime.strptime(str(indebtednessDetails['IqamaExpirationDate'])[:10],
                                                                  "%Y-%m-%d")

                if indebtednessDetails['DueExtraFeesDays'] == '0' and \
                        indebtednessDetails['DueExtraFeesAmount'] == '0' and \
                        indebtednessDetails['HRDF_Amount'] == '0' and \
                        indebtednessDetails['MOF_Extra_Amount'] == '0' and \
                        indebtednessDetails['WP_Amount'] == '0':

                    if ServiceStartDate >= Last_Modified_Date_69:

                        delta = (ServiceStartDate - IqamaExpirationDate).days
                        if delta >= 89:
                            return IndebtAnswers.Answer_indebtedness_technical_issue_0.value.replace('ServiceStartDate',
                                                                                                     str(ServiceStartDate)).replace(
                                '{{indebtStartDcn}}',
                                str(Last_Modified_Date_69)).replace('{{QDt}}', str(
                                indebtednessDetails['ExtraFeesCalculationDate'][:10]))
                        else:
                            return IndebtAnswers.Answer_Iqama_Lass_than_88_days.value

                    else:
                        return IndebtAnswers.Answer_indebtedness_technical_issue_0.value.replace('ServiceStartDate',
                                                                                                 str(
                                                                                                     ServiceStartDate)).replace(
                            '{{indebtStartDcn}}', str(
                                Last_Modified_Date_69)).replace('{{QDt}}', str(
                            indebtednessDetails['ExtraFeesCalculationDate'][
                            :10])) + '\n\n تاريخ بداية الخدمة أقل من 9-6-2022'
                else:
                    return IndebtAnswers.Answer_indebtedness_technical_issue_1.value
            else:

                if lastModifiedDate < Last_Modified_Date_69:
                    return IndebtAnswers.Answer_transfer_requests_less_69.value.replace('{{etdate}}',
                                                                                        str(Last_Modified_Date_69))

                if Last_Modified_Date_91 > lastModifiedDate >= Last_Modified_Date_69:
                    estInfo = getEstablishmentInformation(
                        [str(transferRequestDetails[1]), str(transferRequestDetails[2])])
                    if str(estInfo['EstablishmentTypeId']) == '2':
                        return IndebtAnswers.Answer_transfer_requests_between_69_91_company.value
                    if str(estInfo['EstablishmentTypeId']) == '1':
                        return IndebtAnswers.Answer_transfer_requests_between_69_91_org.value
                    return 'internal note مشكلة تقنية: يرجى اعلام قائد الفريق'

                if lastModifiedDate >= Last_Modified_Date_91:
                    return IndebtAnswers.Answer_transfer_requests_bigger_91.value

        else:
            estInfo = getEstablishmentInformation([str(transferRequestDetails[1]), str(transferRequestDetails[2])],
                                                  justInfo=True)
            sourceEst = str(transferRequestDetails[1]) + '-' + str(transferRequestDetails[2])
            print('sourceEst ===> ', sourceEst)
            print('estInfo ===> ', estInfo)
            print('indebtDetials ===> ', indebtednessDetails)
            if indebtednessDetails is not None:
                if estInfo['EstablishmentId'] == indebtednessDetails['NewEstablishmentId']:
                    return IndebtAnswers.Absent_answer_for_old_est.value.replace('{{sourceEst}}',
                                                                                 str(sourceEst)).replace('{{idNo}}',
                                                                                                         str(laborerId))
                else:
                    return IndebtAnswers.Absent_answer_for_new_est.value.replace('{{sourceEst}}', str(EstNo))
            else:
                return 'يرجى اعلام قائد فريق الرخص وتحويل التذكرة لخدمة الرخص'
    else:
        return IndebtAnswers.Answer_no_transfer_request.value
    return 'nothing '


def WPCheckService(options, infoParams, queryCenterInfo, returnValue):
    o1, o2, o3, o4 = options
    functionName = WPCheckService.__name__
    settings.userName = queryCenterInfo['userName']
    settings.genEmail = queryCenterInfo['genEmail']
    settings.ticketNo = queryCenterInfo['ticketNo']
    print('infoParams -==> ', infoParams)
    resultText = ''
    EstNo, lNo = sortAndGetInsertionInfo(infoParams)
    print('EstNo -==> ', EstNo)
    print('lNo -==> ', lNo)

    if o3:
        returnValue[functionName] = sadadCheck(lNo)
        pyperclip.copy(returnValue[functionName])
        return returnValue[functionName]
    elif o4:
        resultText += CheckWPInHRSD(lNo) + '\n'
    elif o2:
        resultText += getIndebtednessDetails(lNo, EstNo)
    else:
        EstNo = getEstNumber(EstNo)

        if EstNo is None:
            returnValue[functionName] = exitMethodWithText('يرجى تزويدنا برقم المنشأة الصحيح لو سمحتم')
            return returnValue[functionName]

        resultText = ' رقم المنشأة : ' + str(EstNo[0] + '-' + EstNo[1]) + ' \n\n'

        estInfo = getEstablishmentInformation(EstNo)
        if estInfo is None or type(estInfo) is str:
            returnValue[functionName] = estInfo
            return returnValue[functionName]

        if not (o1 or o3 or o4 or o2):
            return returnValue[functionName]

        code, estInfo, resultText = ArrangeAndGetEstInfo(EstNo, estInfo, resultText, False)

        if o1:
            resultText += getFinancialExemptionAnswer(estInfo)
    returnValue[functionName] = resultText
    if not settings.autoFlag:
        pyperclip.copy(resultText)
    return returnValue


def CheckLabNumber(laborerId):
    if laborerId[0] == '2':
        resultText = 'رقم الإقامة : ' + laborerId + '\n'
    elif laborerId[0] in ['3', '4']:
        resultText = 'رقم الحدود : ' + laborerId + '\n'
    elif laborerId[0] == '1':
        resultText = 'رقم الهوية : ' + laborerId + '\n'
    else:
        return '**' + exitMethodWithText('يرجى تزويدنا برقم الإقامة الصحيح')
    return resultText
