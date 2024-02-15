import datetime
import traceback
from datetime import datetime, time

import PySimpleGUI as sg

from Core.Config import settings
from Core.GenralApis import getPIA
from Core.SchemaBuilder.Components.PopupWindow import PopupWindow
from Core.SchemaBuilder.schemaUtils import isEmpty
from Core.Utils.EnumsValues import APIsEnum, AllQueriesEnum, ErrorCodesAndAnswerEnum
from Core.Utils.UtilsFunctions import getNumToString
from Src.Services.EmployeeList.Utils.EmpListUtils import updateLaborer
from Src.Services.EmployeeList.Utils.Enums import UpdateAnswers
from Src.Services.sw.Service.Utils.Enums import IndebtAnswers


def getLaborInfo(lNo):
    laborerNICInfo = getPIA({'valsToReplace': {'IdOrBorderNo': lNo},
                             'bodyJsons': APIsEnum.laborer_info_nic})['GetForeignerAllDataRs']
    if laborerNICInfo['Header']['ResponseStatus']['Code'] == 'NIC00543':
        mol_Laborer = getPIA(
            {'bodyJsons': APIsEnum.query_center_api_custom,
             'query': AllQueriesEnum.LaborerInfoInMolByBorder.value, 'valsToReplace': {'LabNo': lNo}
             })
        print('تم اصدار اقامة لرقم الحدود المدخل')
        if mol_Laborer is None:
            updateLaborer(lNo)
            result = '\nتم طلب تحديث بيانات الموظف في ' + str(
                datetime.today().strftime('%Y-%m-%d')) + ' , الساعة ' + str(time.strftime("%I:%M %p"))
            result += '\n الموظف غير ظاهر في ال Mol_laborer  \n \n يرجى الإنتظار 24 ساعة ثم التحقق في حال تم حل المشكلة \n'
            return result
        mol_Laborer = mol_Laborer[0]
        if not isEmpty(mol_Laborer['IdNo']):
            print('laborer has already Iqameh Number')
            result = UpdateAnswers.LaborerHaveAnIqameh.value + ' ' + str(mol_Laborer['IdNo'])
            lNo = str(mol_Laborer['IdNo'])
            return lNo
        else:
            updateLaborer(lNo)
            return UpdateAnswers.OnGoingUpdatingToIqame.value

def createManualFilesWP(listOfIqameh, pathToExtract=settings.ROOT_DIR):
    settings.listOfVisasOut = listOfIqameh

    while True:
        try:
            if settings.listOfVisasOut is None:
                break
            if type(settings.listOfVisasOut) == str:
                if PopupWindow(text="الخطوة الأولى : التأكد من التأشيرات الغير موجودة ( تأكد الآن من الإتصال في الفي "
                                    "بي أن - إل 2 قبل الإستمرار )", ):
                    return True
                #settings.listOfVisasOut = getVisasIfNotExists(settings.listOfVisasOut.split(','), pathToExtract)

            if type(settings.listOfVisasOut) == list:
                if PopupWindow(
                        text='الخطوة الثانية : جلب بيانات التأشيرات كاملة ( تأكد الآن من الإتصال في الفي بي أن الآخر قبل الإستمرار ) \n'
                             'عدد التأشيرات = ' + str(len(settings.listOfVisasOut))
                ):
                    return True
                print("\n\n\n\nsamer ----> ", settings.listOfVisasOut)
                print("\n\n\n\n")
                #settings.listOfVisasOut = hitAndGetVisaInfoFromSoap(settings.listOfVisasOut)

            if type(settings.listOfVisasOut) == dict:
                if PopupWindow(
                        text=
                        "الخطوة الثالثة : ترتيب البيانات لإنشاء الملفات تحت المغلف بإسم مانيوال ( تأكد الآن من الإتصال في "
                        "الفي بي أن ال تو - قبل الإستمرار )"):
                    return True
                #lastStepArrangeData(settings.listOfVisasOut, visaType, pathToExtract)
                settings.listOfVisasOut = None
                sg.popup(
                    "تم الإنتهاء بنجاح ,يرجى التوجه للملف التالي حيث تم إنشاء المانيوال في " + pathToExtract
                    , keep_on_top=True, title='Done', font=16)

        except ConnectionError:
            sg.popup_error("يرجى التأكد من الإتصال بالإنترنت و التأكد من إتصال ال VPN22"
                           , font=16)
        except Exception as e:
            if 'HTTPConnectionPool(host=' in str(e):
                sg.popup_error("يرجى التأكد من الإتصال بالإنترنت و التأكد من إتصال ال VPN"
                               , font=16)
            elif 'No such file or directory:' in str(e):
                sg.popup_error("يرجى التأكد من الملف الذي يحتوي على التأشيرات"
                               , font=16)
            elif "('08001', '[08001] [Microsoft][ODBC SQL Server Driver][DBNETLIB]SQL Server does not exist or access denied" in str(
                    e):
                sg.popup_error("يرجى التأكد من الإتصال بالإنترنت و التأكد من إتصال ال VPN - l2"
                               , font=16)
            else:
                sg.popup_error(str(e) + "حدث خطأ ما ... يرجى المحاولة مرة أخرى لاحقا")
                traceback.print_exc()


def getFinancialExemptionAnswer(estInfo):
    estNo = [estInfo['LaborOfficeId'], estInfo['SequanceNumber']]
    resultTextIndust = '\n في حال كان إستفساركم عن الإعفاء الصناعي : \n'

    IndustrialExemptionEst = getPIA(
        {'Est': estNo, 'bodyJsons': APIsEnum.query_center_api_custom,
         'query': AllQueriesEnum.IndustrialExemptionEst.value})
    if IndustrialExemptionEst is not None:
        IndustrialExemptionEst = IndustrialExemptionEst[0]
        if str(IndustrialExemptionEst['IsActive']) == '1':
            deactivateDate = datetime.datetime.strptime(str(IndustrialExemptionEst['DeactivatedOn'])[:10],
                                                        "%Y-%m-%d") if IndustrialExemptionEst[
                                                                           'DeactivatedOn'] != 'NULL' else ''
            if deactivateDate == '' or datetime.datetime.strptime(str(IndustrialExemptionEst['DeactivatedOn'])[:10],
                                                                  "%Y-%m-%d") > datetime.datetime.today():
                resultTextIndust += '\n' + ErrorCodesAndAnswerEnum.IndustExempShouldWork.value
            else:
                resultTextIndust += '\n' + ErrorCodesAndAnswerEnum.IndustExempExpired.value.replace(
                    '{{deactivateDate}}', str(deactivateDate)[:10])
            return resultTextIndust
        else:
            resultTextIndust += '\n' + ErrorCodesAndAnswerEnum.IndustExempNotActive.value + '\n'
    else:
        resultTextIndust += '\n' + ErrorCodesAndAnswerEnum.IndustExempNotExist.value.replace('{{EstNo}}',
                                                                                             str(estNo[0]) + '-' + str(
                                                                                                 estNo[1]))

    resultText = '\n'
    agriLaborers = 0

    SaudisDetails = getPIA(
        {'Est': estNo,
         'bodyJsons': APIsEnum.query_center_api_custom,
         'query': AllQueriesEnum.SyncedSaudisUnderUnifiedQuery.value,
         'valsToReplace': {'UnifiedNumberId': estInfo['UnifiedNumberId']}
         })
    SaudisDetails = [] if SaudisDetails is None else SaudisDetails

    owner = 1
    saudis = len(SaudisDetails)
    totalUnderUnified = 10 + owner + saudis + agriLaborers

    if totalUnderUnified > 9 or owner == 0:
        if owner == 0:
            resultText += '\n' + ErrorCodesAndAnswerEnum.ExemptionNotAvailableOwnerNotAch.value
        if totalUnderUnified > 9:
            resultText += '\n' + ErrorCodesAndAnswerEnum.ExemptionNotAvailableNumLabNotAch.value
            resultText += '\n' + 'أرقام إقامات/حدود العمالة على رقمكم الموحد هي : ' + '\n'
            for idx, lInfo in enumerate(3):
                idOrBorder = str(lInfo['IdNo']) if lInfo['IdNo'] != '-' else str(lInfo['BorderNo'])
                resultText += str(idx + 1) + '- رقم الإقامة/الحدود : ' + idOrBorder + '\n'
            if saudis > 0:
                if SaudisDetails is not None and len(SaudisDetails) > 0:
                    resultText += '\n\nمعلومات الموظفين السعوديين : '

        if agriLaborers > 0:
            resultText += '\n\n' + ErrorCodesAndAnswerEnum.MoreThan6Agri.value.replace('{{AllNoOfAgri}}', str(3))\
            .replace('{{CountedFromAgri}}', str(agriLaborers))
            resultText += '\n\nمعلومات الموظفين الزراعيين : '

        resultText += '\n\n' + resultTextIndust
        return resultText

    EstsIdsUnderUnified = getPIA(
        {'bodyJsons': APIsEnum.query_center_api_custom,
         'query': AllQueriesEnum.EstsIdsUnderUnified.value,
         'valsToReplace': {'UnifiedNumberId': estInfo['UnifiedNumberId']}})
    EstsIdsUnderUnified = str([estId['PK_EstablishmentId'] for estId in EstsIdsUnderUnified]).replace('[', '').replace(
        ']', '')

    ExemptionInfoByEstsId = getPIA(
        {'bodyJsons': APIsEnum.query_center_api_custom,
         'query': AllQueriesEnum.ExemptionInfoByEstsId.value,
         'valsToReplace': {'UnifiedNumberId': estInfo['UnifiedNumberId']}})[0]

    TransAndPeriodInfo = getPIA(
        {'bodyJsons': APIsEnum.query_center_api_custom,
         'query': AllQueriesEnum.TransAndPeriodInfo.value,
         'valsToReplace': {'EstablishmentsId': EstsIdsUnderUnified,
                           'FinancialYearStart': ExemptionInfoByEstsId['FinancialYearStart_Grg']}})

    print('EstsIdsUnderUnified', EstsIdsUnderUnified)

    print('ExemptionInfoByEstsId', ExemptionInfoByEstsId)

    print('TransAndPeriodInfo', TransAndPeriodInfo)
    print('TransAndPeriodInfo', TransAndPeriodInfo)

    print('SaudisDetails', SaudisDetails)

    exemptionsShouldBe = 2
    resultText += 'المالك مسجل كمتفرغ في منشآت الرقم الموحد و يوجد لديه ' + str(
        3) + ' موظفين اجانب \n'
    resultText += 'تاريخ بداية السنة المالية الحالية: ' + str(
        ExemptionInfoByEstsId['FinancialYearStart_Grg']) + '\n'
    if saudis >= 1:
        print('estInfo[Entity_Foreigners_Total_Factorized]',estInfo['Entity_Foreigners_Total_Factorized'])
        if SaudisDetails is not None and len(SaudisDetails) > 0:
            resultText += '\nمعلومات الموظفين السعوديين : '
            if saudis >= 1 and float(estInfo['Entity_Saudis_Total_Factorized']) >= 1.00:
                exemptionsShouldBe = 4
            else:
                saudis = 0

    excessEmpls = (len('LaborersUnderUnifiedRegular') - exemptionsShouldBe)
    excessEmpls = 0 if excessEmpls <= 0 else excessEmpls

    exemptionsNo = 0
    paidPerPlus = []
    paidPerSaudi = []
    allExUsedInfo = []
    expiredPaidPerPlus = 0
    TransText = ''
    if TransAndPeriodInfo is not None and len(TransAndPeriodInfo) > 0:
        TransText += '\n\n'
        TransText += 'تم دفع عدد ' + str(len(TransAndPeriodInfo)) + ' أرقام سداد بالبيانات التالية : \n'
        TransText += '\n'
        for tInfo in TransAndPeriodInfo:
            TransText += '- رقم السداد : ' + str(tInfo['BillNumber']) \
                         + ' الفترة المسجلة علية هي ' + getNumToString(tInfo['Period'], AddType='Period') \
                         + ' والمبلغ المدفوع هو ' + tInfo['TransactionFees'] \
                         + ' بتاريخ : ' + str(tInfo['TransactionDate'])[:10] + '\n'

            TransText += '\n\n'
    else:
        TransText += 'لم يتم استخدام أرقام سداد أو تجديد رخص خلال السنة المالية الحالية\n'

    excessEmpls = excessEmpls - (len(paidPerPlus) - expiredPaidPerPlus) - saudis
    excessEmpls = 0 if excessEmpls <= 0 else excessEmpls
    remainingExemp = exemptionsShouldBe - exemptionsNo
    remainingExemp = 0 if remainingExemp <= 0 else remainingExemp

    resultText += '\nعدد الإعفاءات المستحقة في السنة المالية الحالية : ' + str(
        exemptionsShouldBe) + '\n'
    resultText += 'عدد الإعفاءات المستخدمة في السنة المالية الحالية : ' + str(
        exemptionsNo) + '\n'
    resultText += 'عدد الإعفاءات المتبقية في السنة المالية الحالية : ' + str(remainingExemp) + '\n'

    if exemptionsNo > 0:
        resultText += '\nتاريخ استخدام الاعفاءات المستحقة : ' + '\n'
        for idx, exUsedInfo in enumerate(allExUsedInfo):
            resultText += str(idx + 1) + '- تم تجديد رخصة الموظف برقم الحدود/الإقامة "' + str(
                exUsedInfo[0]) + '" بتاريخ ' + str(exUsedInfo[1])[:10] + '\n'
        if exemptionsNo >= exemptionsShouldBe:
            resultText += '\n' + 'تم استخدام جميع الاعفاءات لسنة المالية الحالية، من الممكن استخدام الاعفاءات مرة اخرى في السنة المالية الجديدة.' + '\n\n'

    countPerPlus = 0
    if not settings.autoFlag:
        if len(paidPerPlus) > 0:
            resultText += '\n\nتم الدفع عن  العمالة الزائدة بقيمة مقابل مالي بالبيانات التالية : ' + '\n'
            for idx, perPlusInfo in enumerate(paidPerPlus):
                countPerPlus += perPlusInfo[3]
                if perPlusInfo[3] < 1:
                    paidPlusLessYear = True
                resultText += str(idx + 1) + '- تم تجديد رخصة الموظف برقم الحدود/الإقامة "' + str(
                    perPlusInfo[0]) + '" بتاريخ ' + str(perPlusInfo[1])[:10] + 'المبلغ المدفوع هو ' + str(perPlusInfo[2]) + '\n'


        resultText += '\n\n' + resultTextIndust
        return resultText


def CheckWPInHRSD(IdNo):
    if len(IdNo) > 10 or len(IdNo) < 10:
        return 'الرجاء التأكد من رقم المدخل حيث انه غير صحيح \n\n'
    if IdNo[0] == '2' or IdNo[0] in ['3', '4']:
        mol_Laborer = getPIA(
            {'bodyJsons': APIsEnum.query_center_api_custom,
             'query': AllQueriesEnum.LaborerInfoWPCheckBo.value if str(IdNo)[0] in ['3','4']
             else AllQueriesEnum.LaborerInfoWPCheck.value
                , 'valsToReplace': {'LabNo': IdNo}
             })
        print(mol_Laborer)
        if mol_Laborer is not None:
            mol_Laborer = mol_Laborer[0]
        if mol_Laborer['ExpirationDate'] == 'NULL':
            return 'لا بوجد لرقم الاقامة المدخل رخصة عمل مصدرة، يمكن اصدار رخصة جديدة'
        print('mol_Laborer     ',mol_Laborer)
        currentDate = datetime.datetime.strptime(str(datetime.datetime.today())[:10],"%Y-%m-%d")
        WPEndDate = datetime.datetime.strptime(str(mol_Laborer['ExpirationDate'])[:10],"%Y-%m-%d")
        IqamaNumber = datetime.datetime.strptime(str(mol_Laborer['IqamaExp'])[:10], "%Y-%m-%d")
        delta = (WPEndDate - IqamaNumber).days
        isSync = str(mol_Laborer['isSynchronized'])
        if WPEndDate == 'NULL':
            return IndebtAnswers.NoWp.value.replace("{{IdNo}}", str(IdNo))
        elif isSync == 'NULL':
            return IndebtAnswers.WPISSYNC.value.replace("{{IdNo}}", str(IdNo))
        elif (WPEndDate - currentDate).days >= 180 or (IqamaNumber - currentDate).days >= 180:
            return IndebtAnswers.WPIqamaValid.value.replace("{{IdNo}}", str(IdNo)).replace("{{WorkPermitEndDate}}",
                                                                                           str(WPEndDate)[:10]) \
                .replace("{{IqamaNumber}}", str(IqamaNumber)[:10])
        elif delta > 14:
            return IndebtAnswers.wpbiggerthaniqama.value.replace("{{IdNo}}", str(IdNo))
        elif (WPEndDate - currentDate).days >= 0:
            return IndebtAnswers.WPCheckdetails.value.replace("{{IdNo}}", str(IdNo)).replace("{{WorkPermitEndDate}}",
                                                                                             str(WPEndDate)[:10])
        else:
            return IndebtAnswers.WPCheckdetailsF.value.replace("{{IdNo}}", str(IdNo)).replace("{{WorkPermitEndDate}}",
                                                                                              str(WPEndDate)[:10])
    else:
        return 'يرجى اعلام قائد فريق رخص العمل'
