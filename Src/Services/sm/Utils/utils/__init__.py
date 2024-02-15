import datetime

from Core.Config.Config import getConnectionQiwa
from Core.Utils.EnumsValues import APIsEnum
from Src.Services.UserManagement.Core.Enums import UMQueries, UMAnswers, StatusPayment
from Core.GenralApis import getPIA
from Core.SchemaBuilder.schemaUtils import isEmpty
from Src.Services.UserManagement.Core.Enums import UMQueries, UMAnswers


def CheckPaymentRefUMService(IdNo):
    cursorQiwa = getConnectionQiwa().cursor()
    PaymentRefUM = cursorQiwa.execute(
        UMQueries.PaymentSelect.value.replace('{{IdNumber}}', str(IdNo)))
    allPaymentReferenceQuery = PaymentRefUM.fetchall()  # to check not linked with USER.SUB
    print('Mohammad====>All', allPaymentReferenceQuery)
    PaymentStatus = cursorQiwa.execute(
        UMQueries.AllPayment.value.replace('{{IdNumber}}', str(IdNo)))
    ALLPaymentStatus = PaymentStatus.fetchall()  # to check payment Status
    print('MOHAMMMADP=====>', ALLPaymentStatus)
    if allPaymentReferenceQuery is not None:
        ResultPayment = 'Internal Note ************* : \n' + '\n' + UMAnswers.EmployeePayment.value.replace(
            '{{IdNumber}}',
            IdNo) + "\n"
        for PaymentReferenceList in allPaymentReferenceQuery:
            ResultPayment += UMAnswers.ListPayment.value.replace('{{PaymentReference}}',
                                                                 str(PaymentReferenceList[0])).replace('{{InsertDate}}',
                                                                                                       str(
                                                                                                           PaymentReferenceList[
                                                                                                               1])).replace(
                '{{StatusId}}', StatusPayment.__getitem__("Status" + str(PaymentReferenceList[2])).value) + "\n" + "\n"
        return ResultPayment
    else:
        if ALLPaymentStatus is not None:
            resultText = ''
            rejectedPayments = list(filter(lambda ps: str(ps[2]) in ['4', '6'], ALLPaymentStatus))
            refundedPayments = list(filter(lambda ps: str(ps[2]) == '5', ALLPaymentStatus))
            pendingPayments = list(filter(lambda ps: str(ps[2]) == '2', ALLPaymentStatus))
            if len(rejectedPayments) > 0:
                resultText = '\n عمليات الدفع التالية مرفوضة :' + UMAnswers.PaymentAnswer4.value + '\n'
                for idx, r in enumerate(rejectedPayments):
                    resultText += str(idx + 1) + '- ' + UMAnswers.ListPayment.value.replace('{{PaymentReference}}',
                                                                                            str(r[0])).replace(
                        '{{InsertDate}}', str(r[1])).replace('{{StatusId}}', StatusPayment.Status4.value) + "\n"
                return resultText
            elif len(refundedPayments) > 0:
                resultText += '\n\n- Internal Note **********: \n مرتبطة بعملية الدفع التي حالتها تم ارجاع المبلغ :\n' + UMAnswers.PaymentAnswer5.value + '\n'
                for idx, r in enumerate(refundedPayments):
                    resultText += str(idx + 1) + '- ' + UMAnswers.ListPayment.value.replace('{{PaymentReference}}',
                                                                                            str(r[0])).replace(
                        '{{InsertDate}}', str(r[1])).replace('{{StatusId}}', StatusPayment.Status5.value) + "\n"
                return resultText
            elif len(pendingPayments) > 0:
                resultText += '\n\n-Internal Note ********** : \n مرتبطة بعملية الدفع التي حالتها معلقة \n' + UMAnswers.PaymentAnswer2.value + '\n'
                for idx, r in enumerate(pendingPayments):
                    resultText += str(idx + 1) + '- ' + UMAnswers.ListPayment.value.replace('{{PaymentReference}}',
                                                                                            str(r[0])).replace(
                        '{{InsertDate}}', str(r[1])).replace('{{StatusId}}', StatusPayment.Status2.value) + "\n"
                return resultText
            # else :
            #     continue

        else:
            ResultPayment = UMAnswers.EmployeePayment2.value.replace('{{IdNumber}}', IdNo) + "\n"
            return ResultPayment


def notAppearEstsCheck(estInfo, idNo):
    result = ''

    # check if the EconomyID is Supported at Qiwa or Not
    IsNotSupported = getPIA(
        {'bodyJsons': APIsEnum.query_center_api_custom,
         'query': UMQueries.NotSupportedActivity.value,
         'valsToReplace': {'Main_Economic_Activity_Id': estInfo['Main_Economic_Activity_Id'],
                           'Sub_Economic_Activity_Id': estInfo['SubEconomicActivityId']}
         })

    print('IsNotSupported ===> ', estInfo['Main_Economic_Activity_Id'])

    if estInfo['SubEconomicActivityId']  in ['781011','782002','782001','15','11600','11909','970001']:
        return UMAnswers.NotSupportedEst.value.replace('{{MainEconomicActivity}}', estInfo['MainEconomicActivity'])

    # Check account Managers in HRSD for this Est
    AccountManagers = getPIA(
        {'Est': [estInfo['LaborOfficeId'], estInfo['SequanceNumber']], 'bodyJsons': APIsEnum.query_center_api_custom,
         'query': UMQueries.EstablishmentsAccountManager.value
         })
    print('AccountManagers ===> ', AccountManagers)

    if AccountManagers is None or len(AccountManagers) == 0:
        return UMAnswers.ZeroAccounts.value
    elif len(AccountManagers) > 1:
        result += UMAnswers.MoreThanOneAccount.value.replace('{{estNumber}}', str(estInfo['LaborOfficeId']) + '-' + str(
            estInfo['SequanceNumber'])) \
                      .replace('{{NoAccounts}}', str(len(AccountManagers))) + '\nأرقام هويات المدراء \n'
        for idx, account in enumerate(AccountManagers):
            result += str(idx + 1) + '- رقم الهوية ' + account['IDNO'] + '\n'
        result += '*********** please send it to Qiwa Support to fix it'
        return result
    # if idNo is not None:
    if AccountManagers[0]['IDNO'] != idNo:
        return UMAnswers.NotTheAccountManager.value.replace('{{estNumber}}',
                                                            str(estInfo['LaborOfficeId']) + '-' + str(
                                                                estInfo['SequanceNumber'])) \
            .replace('{{last3Digits}}', AccountManagers[0]['IDNO'][-3:])
    elif AccountManagers[0]['IDNO'] == idNo:
        userAccount = getPIA(
            {'bodyJsons': APIsEnum.query_center_api_custom,
             'query': UMQueries.MolUserInfo.value,
             'valsToReplace': {'idNo': idNo}
             })
        print ('len(userAccount)',userAccount)
        if isEmpty(userAccount) :
            return UMAnswers.AccountNotRegistered.value

        userAccount = userAccount[0]

        if  isEmpty(userAccount['LastLoggedIn']) :
            return UMAnswers.AccountNotActive.value
        else :
            LastLoggedIn = datetime.datetime.strptime(str(userAccount['LastLoggedIn'])[:10], "%Y-%m-%d")
            currentDate = datetime.datetime.strptime(str(datetime.datetime.today())[:10], "%Y-%m-%d")

            delta = (LastLoggedIn - currentDate).days

    if delta >= 360:
        return UMAnswers.AccountNotActive.value

    currentDate = datetime.datetime.strptime(str(datetime.datetime.today())[:10], "%Y-%m-%d")
    InsertDate = datetime.datetime.strptime(str(estInfo['InsertDate'])[:10], "%Y-%m-%d")
    delta = (currentDate - InsertDate).days

    if delta < 6:
        result += 'الرجاء إنتظار تحديث النطاقات الاسبوعي وسيتم ظهور المنشاة بعدها \n\n\n\n'
        return result

    # print('InsertDate ====> ', InsertDate.strftime("%b %d, %Y"))
    print('InsertDate ====> ', InsertDate)
    print('delta ====> ', delta)

    WorkSpace = getPIA(
        {'bodyJsons': APIsEnum.get_est_qiwa_workspace_api,
         'valsToReplace': {'IdNo': idNo}
         })
    print('WorkSpace ====> ', WorkSpace)
    x = {}
    x = WorkSpace['GetQiwaWorkspaceEstablishmentsRs']['Header']['ResponseStatus']['Status']
    print('status ====> ', x)
    # if x != 'SUCCESS':
    #     return UMAnswers.WorkspaceDown.value
    # else:
    x = WorkSpace['GetQiwaWorkspaceEstablishmentsRs']['Header']['ResponseStatus']['Status']
    y = WorkSpace['GetQiwaWorkspaceEstablishmentsRs']['Body']
    print('Furat', y.keys())

    allEstinWS = []
    if y.get('EligibleEstablishmentsList'):
        if type(y['EligibleEstablishmentsList']['EligibleEstablishmentsItem']) == list:
            allEstinWS = allEstinWS + y['EligibleEstablishmentsList']['EligibleEstablishmentsItem']
        else:
            allEstinWS.append(y['EligibleEstablishmentsList']['EligibleEstablishmentsItem'])

    if y.get('NonEligibleEstablishmentsList'):
        if type(y['NonEligibleEstablishmentsList']['NonEligibleEstablishmentsItem']) == list:
            allEstinWS = allEstinWS + y['NonEligibleEstablishmentsList']['NonEligibleEstablishmentsItem']
        else:
            allEstinWS.append(y['NonEligibleEstablishmentsList']['NonEligibleEstablishmentsItem'])

    print('y ===>           ', y)
    print('allEstinWS 2===> ', allEstinWS)
    print('type of allEstinWS', type(allEstinWS))
    allEstinWSKeys = allEstinWS

    getEstFromWS = list(filter(
        lambda est: est['LaborOfficeId'] == estInfo['LaborOfficeId'] and est['EstablishmentSequence'] == estInfo[
            'SequanceNumber'], allEstinWS))
    print('getEstFromWS ==> ', getEstFromWS)
    if isEmpty(getEstFromWS):
        result += 'المنشأة محققة جميع الشروط ولكن ليست ظاهره , الرجاء المحاولة مرة اخرى بعد ساعة \n\n\n\n'
        return result
    else:
        result += 'المنشأة ظاهره بدون أية مشاكل \n \n \n \n '
        return result
