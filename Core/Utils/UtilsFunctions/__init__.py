# coding=utf8
import calendar
import datetime as datetimes
import math
import re
from datetime import timedelta, datetime, date

import pyperclip
from hijri_converter import Hijri

from Core.Config import settings
from Core.Config.Config import getConnectionQiwa
from Core.Utils.EnumsValues import ErrorCodesAndAnswerEnum, APIsEnum, AllQueriesEnum, HeaderCodes
from Core.GenralApis import getPIA, getPIARegular


def getEstNumber(Est):
    if str(Est).__contains__('-'):  # xx-xxxxx
        Est = Est.split('-')
        Est[0] = str(int(Est[0]))
        Est[1] = str(int(Est[1]))
        if int(Est[0]) > int(Est[1]):
            return [Est[1], Est[0]]
        else:
            return [Est[0], Est[1]]
    elif len(Est) < 10 or len(Est) > 10:
        return None
    if str(Est).startswith('7'):  # sevenHundred
        response = getPIA({'Est': ['0', Est], 'bodyJsons': APIsEnum.query_center_api_custom,
                           'query': AllQueriesEnum.EstInfoFromSevenhundredQuery.value})
    else:  # Cr Number
        response = getPIA({'Est': ['0', Est], 'bodyJsons': APIsEnum.query_center_api_custom,
                           'query': AllQueriesEnum.EstInfoFromCommRecQuery.value})
    if response is None or response[0] is None:
        if str(Est).startswith('7'):  # sevenHundred
            response = getPIA({'Est': ['0', Est], 'bodyJsons': APIsEnum.query_center_api_custom,
                               'query': AllQueriesEnum.EstInfoFromMOL_UnifiedNumberQuery.value})
            if response is None or response[0] is None:
                return None
        else:
            return None
    data = response[0]
    return [data['FK_LaborOfficeId'], data['SequenceNumber']]


# {Est:'Establishment Number' , APIsEnum , query :  AllQueriesEnum---Optional only for query_center_api,
# headers : {}


def getCalcBalanceAnswer(estInfo, exceptionalEst):
    calcAnswer = ''
    if estInfo.get('EstablishmentConditionsType') == 1:
        calcAnswer = createEstablishingAnswer(estInfo)
    if estInfo.get('EstablishmentConditionsType') == 2:
        responseJson = \
        getPIA({'Est': [estInfo['EconomicActivityId'], '0'], 'bodyJsons': APIsEnum.query_center_api_custom,
                'query': AllQueriesEnum.ConstAAndBQuery.value})[0]

        estInfo = {**estInfo, **responseJson}
        EntityTotalCount = float(estInfo['EntityTotalCount'])
        EntitySaudisTotalFactorized = float(estInfo['EntitySaudisTotalFactorized'])
        ForeignersFactorized = float(estInfo['EntityForeignersTotalFactorized'])
        EntityForeignersCount = float(estInfo['EntityForeignersCount'])
        constant_a = float(estInfo['Constant_A'])
        constant_b = float(estInfo['Constant_B'])
        Pending_ET = 0
        if estInfo.get('PendingValue'):
            Pending_ET = float(estInfo['PendingValue'])
        issuedVisas = float(estInfo['issuedVisas'])
        Ajeer = float(
            estInfo['EntityAjeerPendingLaborers'] if estInfo.get('EntityAjeerPendingLaborers') is not None else 0)
        totalUsedBalance = issuedVisas + Pending_ET + EntityForeignersCount + Ajeer

        if not (constant_b <= constant_a <= 0):

            currentBalance = getCurrentBalance(Ajeer, EntityTotalCount, ForeignersFactorized,
                                               EntitySaudisTotalFactorized, Pending_ET, constant_a,
                                               constant_b,
                                               issuedVisas)
            if not isEmpty(exceptionalEst) and len(exceptionalEst) > 0:
                result = ErrorCodesAndAnswerEnum.ExceptionalBalance.value.replace('{{QuotaBalance}}',
                                                                                  str(exceptionalEst[0])) \
                    .replace('{{EstNo}}', str(estInfo['LaborOfficeId']) + '-' + str(estInfo['SequanceNumber'])) \
                    .replace('{{totalUsedBalance}}', str(int(totalUsedBalance))) \
                    .replace('{{currentByExcp}}', str(exceptionalEst[0] - int(totalUsedBalance)))
                if estInfo.get('Calculation_Type_Id') is not None and estInfo[
                    'Calculation_Type_Id'] == '1' and estInfo.get('EstablishmentConditionsType') == 2:
                    result += 'تنويه : في حال الغاء الإستثناء سيكون رصيد المنشأة تابع للإحتساب المتوسط'
                elif estInfo["SizeId"] == "1" and estInfo.get('EstablishmentConditionsType') != 1:
                    result += 'في حال إلغاء الإستثناء من وزارة الموارد البشرية سيتم منحكم الرصيد بحسب المنشآت الصغيرة فئة أ كالتالي : \n\n\n\n'.replace(
                        '{{balanceWillBe}}', str(currentBalance))
                    result += getSmallClassAAnswer(estInfo)
                else:
                    result += 'في حال إلغاء الإستثناء من وزارة الموارد البشرية سيتم منحكم الرصيد بحسب نسبة التوطين و سيصبح رصيدكم {{balanceWillBe}}'.replace(
                        '{{balanceWillBe}}', str(currentBalance))
                return result

            fStepCount = 0
            newBalanceStep1 = 0
            # if estInfo.get('Calculation_Type_Id') is not None and estInfo['Calculation_Type_Id'] == '1':
            #     calcAnswer = getAnswerForExpansionSizeBandBigger(Ajeer, Pending_ET,
            #                                                      currentBalance, fStepCount, issuedVisas,0,0,
            #                                                      0)
            while newBalanceStep1 <= 0:
                fStepCount += 1
                newBalanceStep1 = getCurrentBalance(Ajeer, EntityTotalCount, ForeignersFactorized,
                                                    EntitySaudisTotalFactorized + fStepCount, Pending_ET,
                                                    constant_a,
                                                    constant_b,
                                                    issuedVisas)
            sStepCount = fStepCount
            newBalanceStep2 = newBalanceStep1
            while newBalanceStep2 <= newBalanceStep1:
                sStepCount += 1
                newBalanceStep2 = getCurrentBalance(Ajeer, EntityTotalCount, ForeignersFactorized,
                                                    EntitySaudisTotalFactorized + sStepCount, Pending_ET,
                                                    constant_a,
                                                    constant_b,
                                                    issuedVisas)
            calcAnswer = getAnswerForExpansionSizeBandBigger(Ajeer, Pending_ET,
                                                             currentBalance, fStepCount, issuedVisas,
                                                             newBalanceStep1,
                                                             newBalanceStep2, sStepCount, estInfo)
        else:
            currentBalance = int(estInfo['Quota'])
            calcAnswer = getAnswerForExpansionSizeBandBigger(Ajeer, Pending_ET,
                                                             currentBalance, 0, issuedVisas,
                                                             0,
                                                             0, 0, estInfo, Static=True)

    return calcAnswer


def getNumToString(num, AddType=None):
    num = str(num).replace(' ', '')
    if AddType == 'Period':
        if num == "1":
            return 'سنة كاملة'
        elif num == "3":
            return '3 أشهر'
        elif num == "6":
            return '6 أشهر'
        elif num == "9":
            return '9 أشهر'
        else:
            return num
    elif AddType == 'days':
        if num == "1":
            return '24 ساعة'
        elif num == "2":
            return '48 ساعة'
        else:
            return num + ' أيام'
    elif AddType == 'name':
        if num == "1":
            return 'الإسم الأول'
        elif num == "2":
            return 'الإسم الثاني'
        elif num == "3":
            return 'الإسم الثالث'
        elif num == "4":
            return 'الإسم الرابع'
        else:
            return num
    else:
        if num == "1":
            return 'الأولى'
        elif num == "2":
            return 'الثانية'
        elif num == "3":
            return 'الثالثة'
        elif num == "4":
            return 'الرابعة'
        else:
            return num


def getAllowanceInfo(estInfo):
    cursorQiwa = getConnectionQiwa().cursor()
    insertDate = datetime.strptime(str(estInfo['InsertDate'])[:10], "%Y-%m-%d")
    allowanceEndDate = ''
    requestDate = ''
    terminationRequesterIdNo = ''
    terminationDate = ''
    tierId = ''
    tierBalance = ''
    result = cursorQiwa.execute(
        AllQueriesEnum.TierAllowanceInfo.value.replace('{{par1}}', estInfo['LaborOfficeId']).replace('{{par2}}',
                                                                                                     estInfo[
                                                                                                         'SequanceNumber'])).fetchone()
    if not isEmpty(result):
        allowanceEndDate, requestDate, terminationRequesterIdNo, terminationDate, tierId, tierBalance = result
    if isEmpty(tierId):
        tierId = 1
    tierIdName = getNumToString(tierId)

    if isEmpty(allowanceEndDate):
        allowanceEndDate = datetime.strptime(str(add_months(insertDate, 6)), "%Y-%m-%d")
    else:
        allowanceEndDate = datetime.strptime(str(allowanceEndDate)[:10], "%Y-%m-%d")
    if not isEmpty(terminationDate):
        terminationDate = datetime.strptime(str(terminationDate)[:10], "%Y-%m-%d")
    return allowanceEndDate, requestDate, terminationRequesterIdNo, terminationDate, tierIdName, insertDate, tierId, tierBalance


def createEstablishingAnswer(estInfo):
    AvailableVisas = estInfo['AvailableVisas']
    CurrentLaborers = '0'
    PendingSponsorTransferRequests = '0'
    NotUsedVisas = '0'
    EntityAjeerPendingLaborers = '0'
    if estInfo.get('CurrentLaborers'):
        CurrentLaborers = estInfo['CurrentLaborers']
    if estInfo.get('PendingSponsorTransferRequests'):
        PendingSponsorTransferRequests = estInfo['PendingSponsorTransferRequests']
    if estInfo.get('NotUsedVisas'):
        NotUsedVisas = estInfo['NotUsedVisas']
    if estInfo.get('EntityAjeerPendingLaborers'):
        EntityAjeerPendingLaborers = estInfo['EntityAjeerPendingLaborers']
    total = str(int(AvailableVisas) + int(CurrentLaborers) + int(PendingSponsorTransferRequests) + int(
        NotUsedVisas) + int(EntityAjeerPendingLaborers))
    result = ErrorCodesAndAnswerEnum.ESTING_BALANCE.value

    resultArr = result.split('-')
    valuesToReplace = [CurrentLaborers, NotUsedVisas, PendingSponsorTransferRequests, EntityAjeerPendingLaborers]

    allowanceEndDate, requestDate, terminationRequesterIdNo, terminationDate, tierIdName, insertDate, tierId, tierBalance = getAllowanceInfo(
        estInfo)
    if isEmpty(tierBalance):
        tierBalance = total
    if total == str(AvailableVisas):
        result = resultArr[0] + resultArr[6]
    else:
        result = resultArr[0] + resultArr[1]
        for index, vals in enumerate(valuesToReplace):
            if vals != "0":
                result += '-' + resultArr[index + 2]
        result += resultArr[6]
    result = result.replace('{{allowanceEndDate}}', str(allowanceEndDate)[:10]) \
        .replace('{{tierIdName}}', tierIdName) \
        .replace('{{TierBalance}}', str(tierBalance)) \
        .replace('{{CurrentLaborers}}', CurrentLaborers) \
        .replace('{{NotUsedVisas}}', NotUsedVisas) \
        .replace('{{PendingSponsorTransferRequests}}', PendingSponsorTransferRequests) \
        .replace('{{EntityAjeerPendingLaborers}}', EntityAjeerPendingLaborers) \
        .replace('{{AvailableVisas}}', AvailableVisas)
    return result


def getSmallClassAAnswer(estInfo):
    result = ''
    EntitySaudisTotalFactorized = float(estInfo["EntitySaudisTotalFactorized"])

    if 0 < EntitySaudisTotalFactorized < 1 and estInfo.get('nitaq'):
        result += ErrorCodesAndAnswerEnum.ODM00012SmallWithHalfSaudi.value.replace(
            '{{EntitySaudisTotalFactorized}}', str(EntitySaudisTotalFactorized))
        return result
    elif estInfo.get('calcAnswer'):
        Quota = estInfo.get('Quota') if estInfo.get('Quota') is not None else "0"
        Saudis = float(estInfo["Saudis"])

        EntityTotalCount = math.ceil(float(estInfo['EntityTotalCount']))

        PendingSponsorTransferRequests = estInfo.get('PendingValue')
        unUsedVisas = estInfo.get("issuedVisas")
        if unUsedVisas is None:
            unUsedVisas = '0'
        if PendingSponsorTransferRequests is None:
            PendingSponsorTransferRequests = '0'

        currentBalance = 6 - (EntityTotalCount + int(unUsedVisas) + int(
            PendingSponsorTransferRequests))

        if currentBalance > int(Quota) and Quota == "0":
            if Quota == "0" and currentBalance > 0 and Saudis == 0:
                result = ErrorCodesAndAnswerEnum.ODM00012Small.value
            elif Quota == "0" and currentBalance >= 0 and Saudis >= 1 and EntitySaudisTotalFactorized >= 1:
                result += ErrorCodesAndAnswerEnum.ODM00012SmallWithSyncIssue.value
            else:
                result = ErrorCodesAndAnswerEnum.ODM00012Small.value

            return result
        result = "للمنشآت ذات الحجم الصغير فئة ( أ ) يكون الرصيد 6 ( مخصوم منه عدد الموظفين الإجمالي ( عدد السعوديين " \
                 "+ عدد الأجانب ) و عدد التأشيرات المصدرة الغير مستخدمة أو طلبات النقل تحت الاجراء إن وجدت ) \nمع " \
                 "اشتراط وجود موظف سعودي واحد على الأقل أو تسجيل المالك على المنشأة.\n\n " \
                 + "عند وصول مجموع الموظفين على رأس العمل الى 6 يصبح نطاق و رصيد المنشأة حسب نسبة التوطين حيث أن المنشأة في هذه الحالة لا تصبح مصنفة كمنشأة ( صغير فئة أ ) .\n"
        if Quota != "6":
            result += " \n ولديك : " + "\n"

            if EntityTotalCount > 0:
                result += "- عدد " + str(
                    EntityTotalCount) + " موظفين (عدد السعوديين و الأجانب) على مستوى الكيان" + "\n"
            if unUsedVisas != "0":
                result += "- عدد " + unUsedVisas + " تأشيرات مصدرة وغير مستخدمة" + "\n"
            if PendingSponsorTransferRequests != "0":
                result += "- عدد " + PendingSponsorTransferRequests + " طلب نقل خدمات قيد الإجراء" + "\n"

        return result + "ورصيد الإستقطاب : " + str(math.ceil(currentBalance)) + "\n\n"
    elif estInfo['EntitySaudisTotalFactorized'] == "0.00" and not estInfo.get('nitaq'):
        result = ErrorCodesAndAnswerEnum.ODM00012Small.value
        return result
    result += 'معلومات المنشأة كالتالي:\n'
    if estInfo['EstablishmentConditionsType'] == 2:
        result += 'نوع المنشأة : توسع \n'
    elif estInfo['EstablishmentConditionsType'] == 1:
        result += 'نوع المنشأة: تأسيس \n'
    result += 'نطاق المنشأة :"' + estInfo['NitaqatColor'] + '" \n'
    result += 'حجم المنشأة : صغير فئة (أ) ' + ' \n'
    if not isEmpty(estInfo.get('EntityTotalCount')):
        result += 'إجمالي عدد الموظفين (السعوديين والأجانب) : ' + str(
            int(float(estInfo['EntityTotalCount']))) + ' \n'
    if estInfo['EstablishmentConditionsType'] == 1:
        result += "مع التنويه بأن نطاق المنشآت بحجم صغير فئة (أ) كالتالي : أخضر صغير و أحمر صغير" + "\n" + "و بعد وصول منشأتك إلى عدد موظفين 6 فأكثر سيصبح احتساب النطاقات بحسب نسبة التوطين ( أحمر ، أخضر منخفض ،  أخضر متوسط ،  أخضر مرتفع ،  بلاتيني ) "
    else:
        result += "مع التنويه بأن نطاق المنشآت بحجم صغير فئة (أ) كالتالي : أخضر صغير و أحمر صغير" + "\n" + "و بعد وصول منشأتك إلى عدد موظفين 6 فأكثر سيصبح الرصيد بحسب نسبة التوطين مع احتساب النطاقات بحسب نسبة التوطين ( أحمر ، أخضر منخفض ،  أخضر متوسط ،  أخضر مرتفع ،  بلاتيني ) "

    if 'حمر' in estInfo['NitaqatColor']:
        result += '\n\n ليصبح نطاقكم أخضر صغير فئة أ في كيان مجمع صغير فئة أ ، يجب أن يكون لدى المنشأة موظف سعودي على ' \
                  'الأقل أو أن يكون المالك مسجل على نفس المنشأة \n'

    return result


def getCurrentBalance(Ajeer, EntityTotalCount, ForeignersFactorized, EntitySaudisTotalFactorized, Pending_ET,
                      constant_a, constant_b, issuedVisas):
    fNumb = 0
    sNumb = 1
    while True:

        stopper1 = getStopperNum(issuedVisas, Pending_ET, Ajeer, EntityTotalCount, ForeignersFactorized,
                                 EntitySaudisTotalFactorized, constant_a, constant_b, fNumb)

        stopper2 = getStopperNum(issuedVisas, Pending_ET, Ajeer, EntityTotalCount, ForeignersFactorized,
                                 EntitySaudisTotalFactorized, constant_a, constant_b, sNumb)

        if stopper1 >= 0 and stopper2 < 0:
            break
        if stopper1 < 0 and stopper2 < 0:
            fNumb -= 1
            sNumb -= 1
        else:
            fNumb += 1
            sNumb += 1
    return fNumb


def getStopperNum(issuedVisas, Pending_ET, Ajeer, EntityTotalCount, ForeignersFactorized, EntitySaudisTotalFactorized,
                  constant_a, constant_b, numb):
    pendingBalance = issuedVisas + Pending_ET + Ajeer
    E = ForeignersFactorized + pendingBalance
    D = EntityTotalCount + pendingBalance
    P = E + numb
    K = P + EntitySaudisTotalFactorized
    M = D + numb
    try:
        TargetForeignersModNStep1 = 100 - ((math.log(M) * constant_a) + constant_b)
        ForeignersVSTotalStep2 = (P / K) * 100
        Stopper = TargetForeignersModNStep1 - ForeignersVSTotalStep2

    except:
        Stopper = 1

    return Stopper


def getAnswerForExpansionSizeBandBigger(Ajeer, Pending_ET, currentBalance,
                                        fStepCount, issuedVisas, newBalanceStep1, newBalanceStep2, sStepCount, estInfo,
                                        Static=False):
    afterRemovingAjeer = currentBalance + Ajeer
    afterCancelingVisas = currentBalance + issuedVisas
    afterCancelingET = currentBalance + Pending_ET
    pendingBalance = issuedVisas + Pending_ET + Ajeer
    foreignersCount = math.floor(float(estInfo['EntityForeignersCount']))

    afterCancel2 = currentBalance + 2
    expansionClassBiggerThanAAnswer = ErrorCodesAndAnswerEnum.EXPANSION_BALANCE_ANSWER.value
    if Static:
        currentBalance = currentBalance + int(math.ceil(float(estInfo['CurrentLaborers'])))

        balanceInformation = "ويوجد لديكم : \n**- {{issuedVisas}} تاشيرات مصدرة و غير مستخدمة\n**- {{Pending_ET}} طلب نقل تحت الاجراء\n**- {{Ajeer}} موظفين أجير\n**- {{EntityForeignersCount}} موظفين مقيمين على مستوى الكيان"
    else:
        balanceInformation = "ويوجد لديكم : \n**- {{issuedVisas}} تاشيرات مصدرة و غير مستخدمة في حال تم إلغاؤهم سيصبح رصيدكم {{afterCancelingVisas}}\n**- {{Pending_ET}} طلب نقل تحت الاجراء في حال لم يتم إستكمال إجراءاتهم سيصبح رصيدكم {{afterCancelingET}}\n**- {{Ajeer}} موظفين أجير, بعد إنتهاء فترة العمل الخاصة بهم سيصبح رصيدكم {{afterRemovingAjeer}}\n**المجموع : {{pendingBalance}}\n"

    if pendingBalance == 0:
        expansionClassBiggerThanAAnswer = expansionClassBiggerThanAAnswer.replace("{{BalanceInfomation}}", "")

    splittedText = balanceInformation.split("**")
    if issuedVisas <= 0:
        splittedText[1] = ""
        expansionClassBiggerThanAAnswer = expansionClassBiggerThanAAnswer.replace(
            "و {{issuedVisas}} تاشيرات مصدرة و غير مستخدمة", "")
    if Pending_ET <= 0:
        splittedText[2] = ""
    if Ajeer <= 0:
        splittedText[3] = ""
    if foreignersCount <= 0:
        splittedText[4] = ""
    balanceInformation = ''.join(map(str, splittedText))

    balanceInformation = balanceInformation.replace("{{issuedVisas}}", str(math.floor(issuedVisas))) \
        .replace("{{Ajeer}}", str(math.floor(Ajeer))) \
        .replace("{{Pending_ET}}", str(math.floor(Pending_ET))) \
        .replace("{{afterRemovingAjeer}}", str(math.floor(afterRemovingAjeer))) \
        .replace("{{afterCancelingVisas}}", str(math.floor(afterCancelingVisas))) \
        .replace("{{afterCancelingET}}", str(math.floor(afterCancelingET))) \
        .replace("{{pendingBalance}}", str(math.floor(pendingBalance))) \
        .replace("{{afterCancel2}}", str(math.floor(afterCancel2))) \
        .replace("{{currentBalance}}", str(math.floor(currentBalance)))
    if Static:
        return (ErrorCodesAndAnswerEnum.CONST_ZERO_STATIC_BALANCE.value.replace('{{balanceInformation}}',
                                                                                balanceInformation)
                .replace('{{ActivityName}}', estInfo['EconomicActivityName'])
                .replace('{{ActivityID}}', estInfo['EconomicActivityId'])
                .replace('{{TotalBalance}}', str(math.floor(currentBalance + pendingBalance)))
                .replace('{{CurrentBalance}}', str(math.floor(float(estInfo['Quota']))))
                .replace("{{Ajeer}}", str(math.floor(Ajeer)))
                .replace("{{Pending_ET}}", str(math.floor(Pending_ET)))
                .replace("{{pendingBalance}}", str(math.floor(pendingBalance)))
                .replace("{{afterCancel2}}", str(math.floor(afterCancel2)))
                .replace("{{EntityForeignersCount}}", str(foreignersCount))
                )

    expansionClassBiggerThanAAnswer = expansionClassBiggerThanAAnswer.replace("{{currentBalance}}",
                                                                              str(math.floor(currentBalance))) \
        .replace("{{issuedVisas}}", str(math.floor(issuedVisas))) \
        .replace("{{fStepCount}}", str(math.floor(fStepCount))) \
        .replace("{{sStepCount}}", str(math.floor(sStepCount))) \
        .replace("{{newBalanceStep1}}", str(math.floor(newBalanceStep1))) \
        .replace("{{newBalanceStep2}}", str(math.floor(newBalanceStep2))) \
        .replace("{{BalanceInfomation}}", str(balanceInformation))

    return expansionClassBiggerThanAAnswer


def getValidationAnswer(Est, validationDetails, estInfo):
    validationList = []
    if type(validationDetails) == list:
        listVal = validationDetails
    else:
        listVal = [validationDetails]
    for validation in listVal:

        errorCode = "E0000015" if str(validation['ErrorCode']).replace(' ', '') == "ODM00030" else str(
            validation['ErrorCode']).replace(' ', '')
        if errorCode in [str(member.name) for member in ErrorCodesAndAnswerEnum]:
            if errorCode == "ODM00020":
                resultText = ErrorCodesAndAnswerEnum.__getitem__(errorCode).value

                resultText = resultText.replace('{{ListOfExpired}}', getExpiredWPAndIqameh(Est))
                validationList.append(resultText)
            elif errorCode == "E0000015" or errorCode == "E0000606":
                resultText = CRValidateIssue(errorCode, estInfo)

                if 'internal note' in resultText:
                    validationList = resultText
                    break
                else:
                    validationList.append(resultText)

            else:
                resultText = ErrorCodesAndAnswerEnum.__getitem__(errorCode).value
                validationList.append(resultText)
        else:
            validationList.append(validation['ArDescription'])
    return validationList


def CRValidateIssue(errorCode, estInfo):
    print("Samer ===> CRNumber ---- ", estInfo['CRNumber'])
    if str(estInfo['CRNumber']).replace(' ', '') == '{}':
        return ErrorCodesAndAnswerEnum.E0000606.value
    responseInfo_json = getPIARegular(
        {'bodyJsons': APIsEnum.cr_information_api, 'valsToReplace': {'CRNumber': estInfo['CRNumber']}})

    print('responseInfo_json ==semo===> ', responseInfo_json)
    expCrInCrDetails = str(responseInfo_json['CrDetailsRs']['Body']['CRExpiryHijriDate'])
    print('expCrInCrDetails ==> ', expCrInCrDetails)
    expCrInCrDetails = expCrInCrDetails.split("-")
    print('expCrInCrDetails ==> ', expCrInCrDetails)
    expCrInCrDetails = Hijri(int(expCrInCrDetails[2]), int(expCrInCrDetails[1]),
                             int(expCrInCrDetails[0])).to_gregorian()
    expCrInCrDetails = datetimes.datetime.strptime(str(expCrInCrDetails)[:10], "%Y-%m-%d")
    estInfoCrExpDate = str(estInfo['CREndDate'])
    if str(estInfo['CREndDate']) != '{}':
        estInfoCrExpDate = datetimes.datetime.strptime(str(estInfo['CREndDate'])[:10], "%Y-%m-%d")
    if str(estInfo['CREndDate']) == '{}' or (expCrInCrDetails - estInfoCrExpDate).days != 0:
        estNo = str(estInfo['LaborOfficeId']) + '-' + str(estInfo['SequanceNumber'])
        resultOfAPI = getPIA({'bodyJsons': APIsEnum.updating_cr_issue,
                              'valsToReplace': {'CRNumber': estInfo['CRNumber']}})

        resultText = 'internal note : \nestablishmentNumber = ' + estNo + '\nCr Number : ' + str(
            estInfo['CRNumber']) + '\nCR End Date in Qiwa : ' \
                     + str(estInfo['CREndDate'])[:10] + \
                     '\nCR End Date in CR Details : ' + str(expCrInCrDetails)[0:10] + \
                     '\nHijri CR End Date in CR Details : ' + str(
            responseInfo_json['CrDetailsRs']['Body']['CRExpiryHijriDate'])[0:10]
        data = settings.ticketNo, estNo, estInfo['CRNumber'], str(estInfo['CREndDate'])[:10], expCrInCrDetails, str(
            responseInfo_json['CrDetailsRs']['Body']['CRExpiryHijriDate'])[0:10]
        throwToExcel('E0000015', data)
        resultText += '\n \n تم إدخالها من خلال الكويري سنتر, يرجى المحاولة مرة أخرى خلال ال 24 ساعة القادمة '

        resultText += '\n\n\n related to email with subject [TKM-Production-Issue]CRnumberNotUpdatedinQiwa'
        return resultText
    else:
        return ErrorCodesAndAnswerEnum.__getitem__(errorCode).value.replace('{{CRExpDt}}',
                                                                            str(estInfo['CREndDate'])[:10])


def validateTheEstablishment(Est, estInfo):
    responseInfo_json = getPIA({'Est': Est, 'bodyJsons': APIsEnum.validate_api})
    if type(responseInfo_json) == str:
        return responseInfo_json
    if responseInfo_json['ValidateEstablishingExpansionRequestRs'].get('Body') is None or \
            responseInfo_json['ValidateEstablishingExpansionRequestRs']['Body'].get('ValidationsErrorsList') is None:
        return None
    validationDetails = responseInfo_json['ValidateEstablishingExpansionRequestRs']['Body']['ValidationsErrorsList']
    return getValidationAnswer(Est, validationDetails['ValidationError'], estInfo)


def getExpiredWPAndIqameh(Est):
    response = getPIA(
        {'Est': Est, 'bodyJsons': APIsEnum.query_center_api_custom, 'query': AllQueriesEnum.ExpiredWpQuery.value})
    resultText = ''
    listOfInfo = {}

    for labInfo in response:

        if labInfo['IdNo'] is not None and labInfo['IdNo'] != '-':
            labNo = labInfo['IdNo']
        else:
            labNo = labInfo['BorderNo']
        if listOfInfo.get(
                labInfo['FK_LaborOfficeId'] + '-' + labInfo['SequenceNumber'] + "||" + labInfo['Name']) is not None:
            listOfInfo[labInfo['FK_LaborOfficeId'] + '-' + labInfo['SequenceNumber'] + "||" + labInfo['Name']].append(
                labNo)
        else:
            listOfInfo[labInfo['FK_LaborOfficeId'] + '-' + labInfo['SequenceNumber'] + "||" + labInfo['Name']] = [labNo]

    for key in listOfInfo.keys():
        estNum_estName = key.split('||')
        resultText = resultText + '\n' + 'رقم المنشأة : ' + estNum_estName[0] + ' \n إسم المنشأة : ' + estNum_estName[
            1] + '\n'
        resultText = resultText + ' - رقم إقامة/حدود العمالة المنتهية رخصتهم/اقامتهم : \n'
        for labNo in listOfInfo[key]:
            resultText = resultText + '  ' + labNo + '  \n'
    return resultText


def add_months(sourceDate, months):
    month = sourceDate.month - 1 + months
    year = sourceDate.year + month // 12
    month = month % 12 + 1
    day = min(sourceDate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday == 5 or weekday == 4:  # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date


def findNumbersByLength(n, s):
    result = re.findall(r"\D\d{" + str(n) + "}\D", s)
    print('result ===> ', result)
    result = [r[1:-1] for r in result]
    result = set(result)
    return result


def findEsts(s):
    result = re.findall(r"[^\d\-]\d{3,9}\-\d{1,4}[^\d\-]|[^\d\-]\d{1,4}\-\d{3,9}[^\d\-]", ' ' + s + ' ')
    print('result == ', result)
    result = [r[1:-1] for r in result]
    print('result2 == ', result)
    # result = set(result)
    return result


def sortDescList(lis):
    lis = list(filter(lambda ov: not isEmpty(ov), lis))[0:3]
    lis = [int(ov) for ov in lis]
    lis.sort()
    lis = [str(ov) for ov in lis]
    return lis


def ArrangeAndGetEstInfo(EstNo, estInfo, resultText, validate):
    validationList = None
    if validate:
        validationList = validateTheEstablishment(EstNo, estInfo)
        if type(validationList) == str:
            resultText = validationList
        elif validationList is not None:
            resultText = resultText + '\n\n' + 'يرجى الإحاطة بأن المنشأة عليها الملاحظات التالية, ويجب معالجتهم لتتمكنوا من استخدام الخدمات الخاصة بمنصة قوى : ' + ' \n\n'
            if len(validationList) > 1:
                for index, val in enumerate(validationList):
                    resultText = resultText + 'الملاحظة (' + str(index + 1) + ') : ' + str(val)
                    resultText = resultText + '\n'
            else:
                resultText = resultText + '\n - ' + validationList[0] + '\n'
    response_json = getPIA({'Est': EstNo, 'bodyJsons': APIsEnum.calc_est_balance_kc_Api})
    body = response_json['CalculateEstBalanceKCRs'].get('Body')
    code = response_json['CalculateEstBalanceKCRs']['Header']['ResponseStatus']['Code'].replace(' ', '')
    if body is not None:
        if body.get('Establishing') is not None:
            estInfo = {**estInfo, **body['Establishing'],
                       'EstablishmentConditionsType': 1}
        elif body.get('Expansion') is not None:
            estInfo = {**estInfo, **body['Expansion'],
                       'EstablishmentConditionsType': 2}
    else:
        estInfo = {**estInfo, 'EstablishmentConditionsType': 0}
    if not validate and code not in ['E0000101', '00000000', 'E0000066', 'E0000067']:
        if code in HeaderCodes.__members__:
            resultText = resultText + HeaderCodes.__getitem__(code).value + '\n'
        else:
            resultText = resultText + response_json['CalculateEstBalanceKCRs']['Header']['ResponseStatus'][
                'ArabicMsg'] + '\n'

    if validate and validationList is None:
        if code in ['00000000', 'E0000066', 'E0000067']:
            if validate:
                resultText = resultText + 'يرجى المحاولة مرة أخرى وتزويدنا بصورة واضحة في حال إستمرار الإشكالية أو في حال ظهور أية مشاكل أخرى \n\n'
    return code, estInfo, resultText


def exitMethodWithText(text):
    if not settings.autoFlag:
        pyperclip.copy(text)
    return text


def sortAndGetInsertionInfo(EstNo):
    print('est in samer ===> ', EstNo)
    if type(EstNo) == str:
        infoParams = EstNo.split('-')
    else:
        infoParams = EstNo
    lNo = ''

    if len(infoParams) == 1:
        return infoParams[0], infoParams[0]

    infoParams = sortDescList(infoParams)
    print('infoParams in samer ===> ', infoParams)

    if len(infoParams) >= 3:
        EstNo = infoParams[0] + '-' + infoParams[1]
        lNo = infoParams[2]
    elif len(infoParams) == 2:
        if len(infoParams[0]) >= 5 and len(infoParams[1]) == 10:
            EstNo = infoParams[1]
            lNo = infoParams[0]
        else:
            EstNo = infoParams[0] + '-' + infoParams[1]

    print('EstNo in samer ===> ', EstNo)

    return EstNo, lNo


def getEstablishmentInformation(Est, justInfo=False):
    responseInfo_json = getPIA({'Est': Est, 'bodyJsons': APIsEnum.est_info_api})['GetEstablishmentInformationRs']
    if responseInfo_json.get('Body') is None:
        if responseInfo_json['Header']['ResponseStatus']['Code'] == 'E0000142':
            return exitMethodWithText('يرجى تزويدنا برقم المنشأة الصحيح لو سمحتم')
        else:
            return exitMethodWithText('يرجى المحاولة مرة أخرى')

    EstablishmentDetails = responseInfo_json['Body']['EstablishmentDetails']

    if EstablishmentDetails['EstablishmentStatusId'] != "1" and not justInfo:
        return exitMethodWithText('المنشأة رقم ' + str(Est[0]) + '-' + str(Est[1]) + ',  حالتها ' + str(
            EstablishmentDetails['EstablishmentStatus']))
    # print("EstablishmentDetails" + str(EstablishmentDetails))

    responseText = getPIA(
        {"Est": Est, "bodyJsons": APIsEnum.query_center_api_custom, "query": AllQueriesEnum.EvalHistoryQuery.value,
         'valsToReplace': {'pageSize': '1'}})
    print('Semo ---- ', responseText)
    responseText = responseText[0] if responseText is not None else {}

    EstablishmentDetails = {**EstablishmentDetails, **responseText, 'EstNo': str(Est[0]) + '-' + str(Est[1])}

    return EstablishmentDetails
