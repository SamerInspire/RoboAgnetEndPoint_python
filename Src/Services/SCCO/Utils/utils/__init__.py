import datetime
from time import strftime

from Core.Config.Config import getConnectionQiwa
from Core.GenralApis import getPIA
from Core.Utils.EnumsValues import AllQueriesEnum, APIsEnum
from Src.Services.SCCO.Utils.Enums import COAnswers, OccupationStatus


def CheckChangeOccupationDetailsDB(LaborerIdNo):
    cursorQiwa = getConnectionQiwa().cursor()
    COccupationQuery = cursorQiwa.execute(
        AllQueriesEnum.COCheckDetail.value.replace('{{LaborerIdNo}}', str(LaborerIdNo))).fetchone()
    print('MM--COccupationQuery', COccupationQuery)
    Result = ''
    if COccupationQuery is None:
        Result += COAnswers.NoChangeOccupation.value.replace('{{LaborerIdNo}}', LaborerIdNo)
        return Result
    else:
        SourceJob = cursorQiwa.execute(
            AllQueriesEnum.CheckOccupation.value.replace('{{JobID}}', str(COccupationQuery[1]))).fetchone()
        DestinationJob = cursorQiwa.execute(
            AllQueriesEnum.CheckOccupation.value.replace('{{JobID}}', str(COccupationQuery[2]))).fetchone()
        print('SourceJob====>>', SourceJob)
        InsertDate = datetime.datetime.strptime(str(COccupationQuery[3])[:10], "%Y-%m-%d")
        Result += COAnswers.ChangeOccupationQIWA.value.replace('{{LaborerIdNo}}', LaborerIdNo).replace(
            '{{StatusId}}', OccupationStatus.__getitem__("Status" + str(COccupationQuery[0])).value).replace(
            '{{SourceJobId}}', 'صفرية' if COccupationQuery[1] == 0 else str(SourceJob[0])).replace(
            '{{DestinationJobId}}',
            str(DestinationJob[0])).replace('{{InsertDate}}',
                                            str(InsertDate)[:10])
        laborerMLSDInfo = getPIA({'valsToReplace': {'IdOrBorderNo': LaborerIdNo},
                                  'bodyJsons': APIsEnum.laborer_info_mol})['GetLaborerInformationMLSDRs']
        if laborerMLSDInfo['Header']['ResponseStatus']['Code'] == '00000000':
            JobCodeHRSD = laborerMLSDInfo['Body']['LaborerInformation']['Job']['JobCode']

            LaborerNicInfo = getPIA({'valsToReplace': {'IdOrBorderNo': LaborerIdNo},
                                     'bodyJsons': APIsEnum.laborer_info_nic})['GetForeignerAllDataRs']
            print('mm--GetForeignerAllDataRs', LaborerNicInfo)
            JobCodeNic = LaborerNicInfo['Body']['HRSDOccupation']['Code']
            print('MM-JobCodeNic', JobCodeNic)
            print('mm---JobCodeHRSD', JobCodeHRSD)
            # Check Occupation in NIC and HRSD -------------------------------------------------------------------------
            if JobCodeNic != JobCodeHRSD:
                return COAnswers.HRSDIssueOC.value.replace('{{LaborerIdNo}}',
                                                           LaborerIdNo) + '\n- Internal Note*********** -:' + '\n'
            else:
                return Result
        else:
            return Result


def ValidEstSaudiCertificate(estInfo):
    EstLabo = estInfo['Labor_Office_Id']
    EstSeq = estInfo['Sequence_Number']
    print('Mohammad===>>>', EstLabo, EstSeq)
    result = ''
    ValidEstSaudiCertificateAPI = getPIA({'valsToReplace': {'par1': EstLabo, 'par2': EstSeq},
                                          'bodyJsons': APIsEnum.validate_est_certificate})['ValidEstSaudiCertificateRs']
    print('M@Shurrab==>>', ValidEstSaudiCertificateAPI)
    if ValidEstSaudiCertificateAPI['Header']['ResponseStatus']['Code'] == 'E0000022':
        for idx, ListOfTerminateByLaBo in enumerate(ValidEstSaudiCertificateAPI['Body']['ErrorList']['ErrorItem']):
            result += ':' + COAnswers.SaudiCertificate2.value + '\n \n'
            result += str(idx + 1) + '-' + ValidEstSaudiCertificateAPI['Body']['ErrorList']['ErrorItem'][
                'ArDescription']
            return result

    elif ValidEstSaudiCertificateAPI['Header']['ResponseStatus']['Code'] == '00000000':
        result += COAnswers.SaudiCertificate.value + '\n \n'
        return result
    elif ValidEstSaudiCertificateAPI['Header']['ResponseStatus']['Code'] != 'E0000022':
        result += ':' + COAnswers.SaudiCertificate2.value + '\n \n' + ValidEstSaudiCertificateAPI['Header']['ResponseStatus']['ArabicMsg']
        return result


def CheckEstSaudiCertificate(estInfo):
    EstLabo = estInfo['Labor_Office_Id']
    EstSeq = estInfo['Sequence_Number']
    EstName = estInfo['EstablishmentName']
    print('M@MO===>>>', EstLabo, EstSeq, EstName)
    result = ''
    GetSaudiCertificate = getPIA({'valsToReplace': {'par1': EstLabo, 'par2': EstSeq},
                                  'bodyJsons': APIsEnum.get_saudi_certificate})['GetSaudiCertificateRs']
    print('mo==>>>', GetSaudiCertificate)
    if GetSaudiCertificate['Header']['ResponseStatus']['Code'] == '00000000':
        saudi_cert_status_id = GetSaudiCertificate["Body"]["SCDetailsList"]["SCDetailsItem"]["SaudiCertStatus"][
            "SaudiCertStatusId"]
        saudi_cert_date = GetSaudiCertificate["Body"]["SCDetailsList"]["SCDetailsItem"]["SaudiCertIssueDate"]
        currentDate = datetime.datetime.today()
        CertificateDate = datetime.datetime.strptime(str(saudi_cert_date)[:10], "%Y-%m-%d")
        delta = (currentDate - CertificateDate).days
        print('SHURRAB@==>>>', CertificateDate, currentDate, delta)
        # Check if it's Active
        if saudi_cert_status_id == "1":
            if delta > 1:
                result += COAnswers.CertificateName.value + '\n'
                return result
            else:
                result += COAnswers.CertificateDate.value.replace('{{CreationDate}}', str(CertificateDate[:10])) + '\n'
                return result
        else:
            result += COAnswers.NoCertificate.value + '\n'
            return result
    elif GetSaudiCertificate['Header']['ResponseStatus']['Code'] == 'E0000214':
        result += COAnswers.CertifcatetNo.value
        return result

    else:
        result += 'Internal-Note*******************' + '\n' + 'الرجاء تحويل التذكرة الى خدمة إدارة المهن'
        return result
