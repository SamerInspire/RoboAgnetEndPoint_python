import datetime

from Core.Config.Config import getConnectionQiwa
from Core.GenralApis import getPIA
from Core.Utils.EnumsValues import AllQueriesEnum, APIsEnum
from Src.Services.SCM.Utils.Enums import CMAnswers, ContractStatus, StatusTermiante
from Src.Services.EmployeeList.Utils.EmpListUtils import newSortAndGetLaborerCase, get_new_token
from Core.Utils.UtilsFunctions import exitMethodWithText


def afw(IqamaNumber):
    laborerInfo = None
    cursorQiwa = getConnectionQiwa().cursor()
    currentDate = datetime.datetime.strptime(str(datetime.datetime.today())[:10], "%Y-%m-%d")
    print(AllQueriesEnum.AbsentFromWorkRequest.value.replace('{{IqamaNumber}}', str(IqamaNumber)))
    AbsentFromWorkReq = cursorQiwa.execute(
        AllQueriesEnum.AbsentFromWorkRequest.value.replace('{{IqamaNumber}}', str(IqamaNumber))).fetchone()
    laborerInfo = {}
    if IqamaNumber[0] == '2':
        laborerMLSDInfo = getPIA({'valsToReplace': {'IdOrBorderNo': IqamaNumber},
                                  'bodyJsons': APIsEnum.laborer_info_mol})['GetLaborerInformationMLSDRs']
        print("samer - -- - - ", laborerMLSDInfo['Header']['ResponseStatus']['Code'])
        if laborerMLSDInfo['Header']['ResponseStatus']['Code'] == 'E0000098':
            token = get_new_token()
            return newSortAndGetLaborerCase(IqamaNumber, token)

        laborerInfo = laborerMLSDInfo['Body']
        LaborerStatusCode = str(laborerInfo['LaborerInformation']['LaborerStatus']['LaborerStatusCode'])
        laborerInfo = {**laborerInfo,
                       'estNumber': str(laborerInfo['EstablishmentInfo']['LaborOfficeId']) + '-' + str(
                           laborerInfo['EstablishmentInfo']['SequanceNumber']),
                       'LaborerStatusName': laborerInfo['LaborerInformation']['LaborerStatus']['LaborerStatusName']
                       }

    else:
        token = get_new_token()
        laborerInfo = newSortAndGetLaborerCase(IqamaNumber, token, True)
        print("laborerInfo ==> ", laborerInfo)
        LaborerStatusCode = str(int(laborerInfo['Status']['PersonStatus']['Code']) + 1)
        laborerInfo = {**laborerInfo,
                       'estNumber': str(laborerInfo['LaborOfficeId']) + '-' + str(laborerInfo['SequenceNumber']),
                       'LaborerStatusName': laborerInfo['Status']['PersonStatus']['Name']
                       }

    if AbsentFromWorkReq is None and IqamaNumber[0] == '2':
        WPEndDate = laborerInfo['LaborerInformation']['WorkPermitEndDate']
        print('WPEndDate ====> ', WPEndDate)
        if str(WPEndDate).replace(' ', '') == '{}':
            WPEndDate = datetime.datetime.today() - datetime.timedelta(90)

        WPEndDate = datetime.datetime.strptime(str(WPEndDate)[:10], "%Y-%m-%d")
        delta = (WPEndDate - currentDate).days
        contractInfo = cursorQiwa.execute(
            AllQueriesEnum.ContractInfoByLabEst.value.replace('{{LaborerId}}', str(IqamaNumber)) \
                .replace('{{SequenceNumber}}', str(laborerInfo['EstablishmentInfo']['SequanceNumber'])) \
                .replace('{{LaborOfficeId}}',
                         str(laborerInfo['EstablishmentInfo']['LaborOfficeId']))).fetchone()

        if str(laborerInfo['LaborerInformation']['WorkPermitTypeId']) == '2' and delta >= 60 and contractInfo is None:
            result = CMAnswers.NoAbsentReq.value.replace('{{IqamaNumber}}', IqamaNumber)
            return result
        else:
            result = CMAnswers.NoAbsentReq.value.replace('{{IqamaNumber}}', IqamaNumber) + '\n\n'
            result += 'الموظف لم يحقق الشروط التالية : \n'
            # print(laborerInfo['LaborerInformation']['WorkPermitTypeId'])
            # if str(laborerInfo['LaborerInformation']['WorkPermitTypeId']) != '2':
            #     result += '- لا يوجد رخصة عمل عادية\n'
            if delta < 60:
                result += '- لا يوجد رخصة سارية لمدة 60 يوم \n'
            if contractInfo is not None:
                result += '- لديه عقد عمل ساري على المنشأة المسجل عليها في وزارة الموارد البشرية \n'

            return result

    elif AbsentFromWorkReq is None and IqamaNumber[0] != '2':
        print('laborerInfo ===> ', laborerInfo)
        entryDate = datetime.datetime.strptime(str(laborerInfo['Travel']['EntryDate']['GregorianDate'])[:10],
                                               "%Y-%m-%d")
        delta = (currentDate - entryDate).days
        if delta >= 90:
            return CMAnswers.StaysForMoreThan60.value.replace('{{borderNumber}}', str(IqamaNumber)).replace(
                '{{enterDate}}', str(entryDate)[:10]).replace(
                '{{daysCount}}', str(delta))

        else:
            return CMAnswers.StaysLessThan60.value.replace('{{borderNumber}}', str(IqamaNumber))
    else:
        absentDate = datetime.datetime.strptime(str(AbsentFromWorkReq[0])[:10], "%Y-%m-%d")
        delta = (currentDate - absentDate).days
        print('Mohammad Shurrab ===> ', absentDate)
        print('delta ===> ', delta)
        if delta < 60 and AbsentFromWorkReq[1] == 1:
            result = CMAnswers.HasAbsentStillTime.value.replace('{{IqamaNumber}}', str(IqamaNumber)).replace(
                '{{AbsentDt}}', str(AbsentFromWorkReq[0])[:10])
            return result
        else:

            if LaborerStatusCode == '1':
                if 3 == AbsentFromWorkReq[1]:
                    return '\n ********************************* \n يرجى تحويل التذكرة لفريق العقود \n \n حالة طلب الإنقطاع هي خروج نهائي \n '
                print('samer ====> ', AbsentFromWorkReq)
                if str(AbsentFromWorkReq[1]) in ('2', '5'):
                    if AbsentFromWorkReq[2] == str(laborerInfo['estNumber']):
                        token = get_new_token()
                        result = newSortAndGetLaborerCase(IqamaNumber, token)
                        result += '\n \n\n\n\n *************Status_5_2************** \n\n يوجد مشكلة '
                        return result
                    else:
                        return CMAnswers.TransFromEst.value.replace('{{IqamaNumber}}', IqamaNumber)
                print('semo ---> ',
                      AllQueriesEnum.RunAwayDetailsData.value.replace('{{IqamaNumber}}', str(IqamaNumber)))
                RunAwayDetailsData = cursorQiwa.execute(
                    AllQueriesEnum.RunAwayDetailsData.value.replace('{{IqamaNumber}}', str(IqamaNumber))).fetchone()
                print('RunAwayDetailsData -=--> ', RunAwayDetailsData)
                if RunAwayDetailsData is not None and '<Code>00000000</Code><ArabicMsg>تمت العملية بنجاح</ArabicMsg>' not in \
                        RunAwayDetailsData[6]:
                    if "<ArabicMsg>" in RunAwayDetailsData[6].replace('/', ''):
                        return CMAnswers.DidNotUpdatedToAbsent.value.replace('{{Reason}}',
                                                                             RunAwayDetailsData[6].replace('/',
                                                                                                           '').split(
                                                                                 "<ArabicMsg>")[1])
                    else:
                        return 'internal note :\n assign to Shurrab \n Pending email : Runway visa expiry visa **************tag:NICMessageNotRegistered \n\n\n\n\n\n' + CMAnswers.DidNotUpdatedToAbsent.value.replace(
                            '{{Reason}}', RunAwayDetailsData[6].replace('/', '').split("<ReturnMessage>")[1])
                token = get_new_token()
                return newSortAndGetLaborerCase(IqamaNumber,
                                                token) + '****************Status_1_didn\'t_updated*************** \n يوجد طلب إنقطاع للموظف وتم مرور 60 يوم على طلب الإنقطاع ولم يتم تحديث حالة الموظف يرجى التحقق'
            else:
                return CMAnswers.AbsentEnd.value.replace("{{IqamaNumber}}", IqamaNumber).replace("{{Status}}",
                                                                                                 laborerInfo[
                                                                                                     'LaborerStatusName'])


def ccd(LaborerId):
    cursorQiwa = getConnectionQiwa().cursor()
    # Check if LaborerId
    contractId = None
    if len(LaborerId) == 10:
        query = AllQueriesEnum.AllContractInfoByLab.value.replace('{{LaborerId}}', str(LaborerId))
    else:
        query = AllQueriesEnum.AllContractInfoByLab.value.replace('LaborerId =\'{{LaborerId}}\'',
                                                                  ' ' + 'ID=' + str(LaborerId))
        contractId = LaborerId
    CheckContractReq = cursorQiwa.execute(query).fetchone()

    print(CheckContractReq)
    if CheckContractReq is None:
        if contractId is not None:
            result = CMAnswers.NoContractID.value.replace('{{Contract}}', LaborerId)
        else:
            result = CMAnswers.NoContract.value.replace('{{LaborerId}}', LaborerId)
        return result
    else:
        iqamehNo = CheckContractReq[6]
        contractId = CheckContractReq[1]
        result = CMAnswers.HasContract.value.replace('{{LaborerId}}', str(iqamehNo)) \
            .replace('{{ContractId}}', str(contractId)) \
            .replace('{{estNo}}', str(CheckContractReq[5]) + '-' + str(CheckContractReq[4])) \
            .replace('{{ContStatus}}', ContractStatus.__getitem__("Status" + str(CheckContractReq[0])).value)
        query = AllQueriesEnum.CheckGosiRegistered.value.replace('{{ID}}', str(contractId))
        CheckGosi = cursorQiwa.execute(query).fetchone()
        print("CheckGosiRegi=======", CheckGosi)
        if CheckGosi is not None:
            result += '\n\n' + CMAnswers.AnswerGosi.value
            message = CheckGosi[1].lower().split('message":')
            message = message[1].split("\"")[3] if len(message) > 1 else message[0].split("\"")[3]
            print('Gossssssssssssssssi', message)
            result += '\n' + str(message)
        return result


def ct(LaborerIdNo):
    cursorQiwa = getConnectionQiwa().cursor()
    ContractID = None
    Result = ''
    if len(LaborerIdNo) > 10:
        Result = 'يرجى تزويدنا بالرقم الهوية الصحيح'
        return Result
    if len(LaborerIdNo) == 10:
        CheckTerminateContract = cursorQiwa.execute(
            AllQueriesEnum.TerminateContractsDetails.value.replace('{{LaborerIdNo}}',
                                                                   str(LaborerIdNo)))
        print(CheckTerminateContract)
    else:
        CheckTerminateContract = cursorQiwa.execute(
            AllQueriesEnum.TerminateContractsDetails.value.replace('LaborerIdNo= \'{{LaborerIdNo}}\'',
                                                                   ' ' + 'ContractId=' + str(LaborerIdNo)))
        ContractID = LaborerIdNo
    if CheckTerminateContract.fetchone() is None:
        if ContractID is not None:
            Result += CMAnswers.NoContractIDTerminate.value.replace('{{LaborerIdNo}}', ContractID)
        else:
            Result += CMAnswers.NoTerminateContract.value.replace('{{LaborerIdNo}}', LaborerIdNo)
        return Result
    else:
        allCheckTerminateContract = CheckTerminateContract.fetchall()
        print('allCheckTerminateContract', allCheckTerminateContract)
        if allCheckTerminateContract is None:
            return '\n' + CMAnswers.NoTerminateContract.value
        else:
            if str(allCheckTerminateContract[0][6][0]) == '1':
                Result += 'رقم الهوية: ' + allCheckTerminateContract[0][6] + '\n'
            else:
                Result += 'رقم الاقامة: ' + allCheckTerminateContract[0][6] + '\n'

            for idx, ListOfTerminateByLaBo in enumerate(allCheckTerminateContract):
                Result += '\n' + str(idx + 1) + '-' + (
                    CMAnswers.TerminateContract2 if str(ListOfTerminateByLaBo[2]) == '2' and str(
                        ListOfTerminateByLaBo[7]) == '1' else CMAnswers.TerminateContract).value.replace(
                    "{{ContractId}}", str(ListOfTerminateByLaBo[3])).replace('{{estNo}}',
                                                                             str(
                                                                                 ListOfTerminateByLaBo[
                                                                                     1]) + '-' + str(
                                                                                 ListOfTerminateByLaBo[
                                                                                     0])).replace(
                    '{{StatusId}}',
                    StatusTermiante.__getitem__("Status" + str(ListOfTerminateByLaBo[7])).value).replace(
                    '"{{CreationDate}}"',
                    str(ListOfTerminateByLaBo[8])[:10]) if ContractID is None else '\n' + '\n' + str(idx + 1) + '-' + (
                    CMAnswers.TerminateContract2 if str(
                        ListOfTerminateByLaBo[
                            2]) == '2' and str(
                        ListOfTerminateByLaBo[
                            7]) == '1' else CMAnswers.TerminateContract).value.replace(
                    "{{ContractId}}", str(ListOfTerminateByLaBo[3])).replace('{{estNo}}',
                                                                             str(
                                                                                 ListOfTerminateByLaBo[
                                                                                     1]) + '-' + str(
                                                                                 ListOfTerminateByLaBo[
                                                                                     0])).replace(
                    '{{StatusId}}',
                    StatusTermiante.__getitem__("Status" + str(ListOfTerminateByLaBo[7])).value).replace(
                    '"{{CreationDate}}"', str(ListOfTerminateByLaBo[8])[:10])
    return Result


def cdq(estInfo):
    CheckAuthenticationContract = getPIA({'Est': [str(estInfo['LaborOfficeId']), str(estInfo['SequanceNumber'])],
                                          'bodyJsons': APIsEnum.auth_indicator_contracts})
    print('CheckAuthenticationContract', CheckAuthenticationContract)
    code = CheckAuthenticationContract['ContractAuthenticationIndicatorRs']['Header']['ResponseStatus']['Code'].replace(
        ' ', '')
    body = CheckAuthenticationContract['ContractAuthenticationIndicatorRs'].get('Body')
    print('body ', body)
    if body is not None:
        if float(str(body['TotalAuthenticationPercentage']).replace('%', '')) < 100.00:
            return CMAnswers.ReturnAuthenticationContract.value.replace('{{TotalAuthenticationPercentage}}',
                                                                        str(body['TotalAuthenticationPercentage'])) \
                .replace('{{ForeignersCount}}', str(body['ForeignersCount'])).replace('{{SaudisCount}}',
                                                                                      str(body['SaudisCount']))
        else:
            return CMAnswers.ReturnAuthenticationContract2.value.replace('{{TotalAuthenticationPercentage}}',
                                                                         str(body['TotalAuthenticationPercentage'])) \
                .replace('{{ForeignersCount}}', str(body['ForeignersCount'])).replace('{{SaudisCount}}',
                                                                                      str(body['SaudisCount']))

    else:
        return '**' + exitMethodWithText('الرجاء تحويل التذكرة لخدمة العقود لتحقق من المشكلة')
