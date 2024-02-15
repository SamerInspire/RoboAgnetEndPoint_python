from Core.Config.Config import getConnectionQiwa
from Core.GenralApis import getPIA
from Core.SchemaBuilder.schemaUtils import isEmpty
from Core.Utils.EnumsValues import AllQueriesEnum, ErrorCodesAndAnswerEnum, APIsEnum
from Core.Utils.UtilsFunctions import getAllowanceInfo, getSmallClassAAnswer, getCalcBalanceAnswer, exitMethodWithText
from Src.Services.Sv.Core.Enums import QuriesToGetManual, VisaStatusEnum


def getEstIssuesWhileIssuing(estInfo):
    print('in here getEstIssuesWhileIssuing ')
    resultText = ''
    cursorQiwa = getConnectionQiwa().cursor()
    BusinessNotFound = cursorQiwa.execute(
        AllQueriesEnum.CheckForBusinessNotFoundExp.value.replace('{{LaborOfficeId}}', str(estInfo['LaborOfficeId'])) \
            .replace('{{EstablishmentSequence}}', str(estInfo['SequanceNumber']))).fetchall()
    print('in here BusinessNotFound ',
          AllQueriesEnum.CheckForBusinessNotFoundExp.value.replace('{{LaborOfficeId}}', str(estInfo['LaborOfficeId'])) \
          .replace('{{EstablishmentSequence}}', str(estInfo['SequanceNumber'])))
    print('in here BusinessNotFound ', BusinessNotFound)
    if BusinessNotFound is None or len(BusinessNotFound) == 0:
        BusinessNotFound = cursorQiwa.execute(
            AllQueriesEnum.CheckForBusinessNotFoundEst.value.replace('{{LaborOfficeId}}', str(estInfo['LaborOfficeId'])) \
                .replace('{{EstablishmentSequence}}', str(estInfo['SequanceNumber']))).fetchall()
        print('in here BusinessNotFound ', AllQueriesEnum.CheckForBusinessNotFoundEst.value.replace('{{LaborOfficeId}}',
                                                                                                    str(estInfo[
                                                                                                            'LaborOfficeId'])) \
              .replace('{{EstablishmentSequence}}', str(estInfo['SequanceNumber'])))
        print('in here BusinessNotFound ', BusinessNotFound)

    print('in here BusinessNotFound ', BusinessNotFound)

    if BusinessNotFound is not None and len(BusinessNotFound) > 0:
        resultText = 'بخصوص إستفساركم نفيدكم بأن هذه المشكلة خارج إختصاص قوى, حيث أن الطلب مرفوض من وزارة الداخلية'
        resultText += '\n \n \n *************************** \n \n \n \n \n \n'
        resultText += 'internal note :  \n \n \n مشاكل المنشآت المربوطة برقم وطني موحد \n \n ac3247e business not found  '

        return resultText

    visaInformation = cursorQiwa.execute(
        QuriesToGetManual.CheckIfEstHasVisaIssues.value.replace('{{LaborOfficeId}}', str(estInfo['LaborOfficeId'])) \
            .replace('{{EstablishmentSequence}}', str(estInfo['SequanceNumber']))).fetchall()

    if visaInformation is None or len(visaInformation) == 0:
        return ErrorCodesAndAnswerEnum.noLogsOrErrorsForIssuingVisas.value

    resultText = 'يوجد طلبات معلقة للعميل يجب التحقق في حال وجود مانيوال للعميل بالبيانات التالية : \n'
    for idx, vi in enumerate(visaInformation):
        visaType = 'تأسيس' if str(vi[7]) == '1' else 'توسع' if str(vi[7]) == '3' else 'مؤقته' if str(
            vi[7]) == '2' else 'أخرى يرجى التحقق'
        resultText += str(idx + 1) + '- OrderYear - orderNumber - laborOffice : ' + str(vi[0]) + '-' + str(
            vi[1]) + '-' + str(vi[2]) + '\n' \
                      + 'تاريخ الإصدار : ' + str(vi[3].day) + '-' + str(vi[3].month) + '-' + str(vi[3].year) + '\n' \
                      + 'رقم المنشأة : ' + str(vi[4]) + '-' + str(vi[2]) + '\n' \
                      + 'رقم ال700 : ' + str(estInfo['NICAccountNumber']) + '\n' \
                      + 'نوع طلب التأشيرات : ' + visaType + '\n \n'

    print('in here resultText ', resultText)

    return resultText


def visaCheckAllCasesAnswer(VOrBNumber):
    resultText = ''
    cursorQiwa = getConnectionQiwa().cursor()
    if type(VOrBNumber) == str:
        VOrBNumber = VOrBNumber.replace('-', '').replace(' ', '')[:10]
        if len(VOrBNumber) != 10:
            return exitMethodWithText('يرجى تزويدنا ب الرقم الصادر أو رقم الحدود للتأشيرة للتحقق')
        else:
            if VOrBNumber[:3] != '130':
                resultText = 'رقم الحدود : ' + VOrBNumber
                visaInformation = cursorQiwa.execute(
                    AllQueriesEnum.GetVisasInfoByBorderNumber.value.replace('{{par1}}', str(VOrBNumber)) \
                        .replace('{{status}}', str('1,2,3,4'))).fetchall()
            else:
                resultText = 'الرقم الصادر : ' + VOrBNumber
                visaInformation = cursorQiwa.execute(
                    AllQueriesEnum.GetVisasInfoByVGON.value.replace('{{VisaOutGoingNumber}}',
                                                                    str(VOrBNumber))).fetchall()
                if visaInformation is None:
                    VOGONExistance = cursorQiwa.execute(
                        AllQueriesEnum.GetVGONExistance.value.replace('{{VisaOutGoingNumber}}',
                                                                        str(VOrBNumber))).fetchone()
                    if VOGONExistance is not None:
                        VRID_Type = VOGONExistance[0].split('-')
                        if str(VRID_Type[1]) in ['1', '2', '3']:
                            resultText += '\n\ninternal note :  يرجى التحقق من ربط الرقم الصادر مع أرقام الحدود حيث لم يتم إيجاد أي رقم حدود تابع للرقم الصادر (مشكلة رقم صادر بدون أرقام حدود) \n\n' \
                                          + '\nVisaRequestId = ' + VRID_Type[0] \
                                          + '\nstatus = ' + ('تأسيس' if '1' == VRID_Type[1] else 'توسع' if VRID_Type[
                                                                                                              1] == '3' else 'تأشيرات عمل مؤقت')
                        return resultText
                else:
                    resultText += ' ويوجد عليه ' + str(len(visaInformation)) + ' تأشيرة كالتالي : \n\n'
    elif type(VOrBNumber) == list:
        visaInformation = VOrBNumber
    if visaInformation is None or len(visaInformation) == 0:
        resultText = exitMethodWithText(ErrorCodesAndAnswerEnum.VISA_NOT_FOUND.value)
    return resultText


def getCancelVisasAnswer(estInfo):
    cursorQiwa = getConnectionQiwa().cursor()
    resultText = ''
    bordersPendAndCanceled = cursorQiwa.execute(
        AllQueriesEnum.GetVisasInfoByEstNumber.value.replace('{{par1}}', str(estInfo['LaborOfficeId'])) \
            .replace('{{par2}}', str(estInfo['SequanceNumber'])) \
            .replace('{{status}}', str('4'))).fetchall()
    if bordersPendAndCanceled is None or len(bordersPendAndCanceled) == 0:
        return resultText + ErrorCodesAndAnswerEnum.NO_PEND_VISAS.value
    visasInfo = list(filter(lambda c: c[1] == 4, bordersPendAndCanceled))
    resultText += visaCheckAllCasesAnswer(visasInfo)

    return resultText
