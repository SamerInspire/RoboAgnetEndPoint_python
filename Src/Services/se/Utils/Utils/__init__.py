from Core.Config.Config import getConnectionQiwa
from Core.GenralApis import getPIA
from Core.Utils.EnumsValues import AllQueriesEnum, APIsEnum
from Src.Services.se.Utils.Enums import ETStatus, ETAnswers


def CheckChangeSponsorDetailsDB(LaborerIdNo):
    cursorQiwa = getConnectionQiwa().cursor()
    CheckETReq = cursorQiwa.execute(
        AllQueriesEnum.ChangeSponsorDetails.value.replace('{{LaborerIdNo}}', str(LaborerIdNo))).fetchone()
    print(CheckETReq)
    result = ''
    if CheckETReq is None:
        result += ETAnswers.NoChangeSponsor.value.replace('{{LaborerIdNo}}', LaborerIdNo)
    elif str(CheckETReq[0]) == '7':
        result += ETAnswers.ChangeSponsorRelease.value.replace('{{LaborerIdNo}}', LaborerIdNo).replace(
            '{{SourceEstablishmentNumber}}', str(CheckETReq[1])) \
            .replace('{{DestinationEstablishmentNumber}}', str(CheckETReq[2])) \
            .replace('{{ETStatus}}', ETStatus.__getitem__("Status" + str(CheckETReq[0])).value).replace('{{Realase}}',
                                                                                                        str(CheckETReq[
                                                                                                                3])[
                                                                                                        :10])
    else:
        result += ETAnswers.HasChangeSponsor.value.replace('{{LaborerIdNo}}', LaborerIdNo).replace(
            '{{SourceEstablishmentNumber}}', str(CheckETReq[1])) \
            .replace('{{DestinationEstablishmentNumber}}', str(CheckETReq[2])) \
            .replace('{{ETStatus}}', ETStatus.__getitem__("Status" + str(CheckETReq[0])).value)

    return result


def ValidateEstNatPercentage(estInfo, LaborerIdNo):
    result = ''
    EsInfoEntityId = estInfo['EntityId']
    if EsInfoEntityId is None:
        result += ETAnswers.EntityNotValid.value + '\n Internal Note *********'
        return result
    else:
        laborerMLSDInfo = getPIA({'valsToReplace': {'IdOrBorderNo': LaborerIdNo},
                                  'bodyJsons': APIsEnum.laborer_info_mol})['GetLaborerInformationMLSDRs']
        NationalityCode = laborerMLSDInfo['Body']['LaborerInformation']['Nationality']['NationalityCode']
        validateEstPercentage = getPIA({'valsToReplace': {'EntityId': EsInfoEntityId, 'CodeNat': NationalityCode},
                                        'bodyJsons': APIsEnum.validate_api_natpercentag})[
            'ValidateEstNatPercentageRs']
        ###
        if validateEstPercentage['Header']['ResponseStatus']['Code'] != '00000000':

            result += (validateEstPercentage['Header']['ResponseStatus'][
                'ArabicMsg'])
            # LaborerNationality = apiHit(
            #     {'bodyJsons': APIsEnum.query_center_api_custom,
            #      'query': AllQueriesEnum.EntityLaborersGroupByNationality.value,
            #      'valsToReplace': {'EsInfoEntityId': estInfo['EntityId'],
            #                        'NationalityId': NationalityCode,
            #                        }
            #      })
            # numberNation = int(LaborerNationality[0]['Numbers'])
            # totalCountEst = int(float(estInfo['EntityTotalCount']))
            # PercentageOfNationality = round((numberNation / totalCountEst) * 100, 2)
            # print('Percentage', PercentageOfNationality)
            # + '\n\n' + 'حيث ان نسبة الموظفين على نفس الجنسية '+ str(PercentageOfNationality))
            # get IdNumbers --------------------------------------------------------------------------------------------
        else:
            result += ETAnswers.Cantransfer.value.replace('{{LaborerIdNo}}', LaborerIdNo)
        return result
