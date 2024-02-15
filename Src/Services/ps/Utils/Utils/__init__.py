import time

from Core.Config.Config import getConnectionQiwa
from Core.GenralApis import getPIA
from Core.SchemaBuilder.schemaUtils import isEmpty
from Core.Utils.EnumsValues import APIsEnum
from Src.Services.ps.Core.Enums import PMQueries, PMAnswers


def getAllPrivileges(estInfo, idNo): #2309496-1 / 1009326784   1064438979-1-2113711

    result = ''

    cursorQiwa = getConnectionQiwa().cursor()

    PS = cursorQiwa.execute(PMQueries.Privileges.value).fetchall()
    allPriv = cursorQiwa.execute(PMQueries.RedundantPrivilegs.value.replace('{{idNo}}', idNo).replace('{{estLab}}' , str(estInfo['LaborOfficeId'])).replace('{{estSeq}}' , str(estInfo['SequanceNumber']))).fetchall()
   # RedundantPrivilegs = cursorQiwa.execute(PMQueries.RedundantPrivilegs.value.replace('{{idNo}}', idNo).replace('{{estLab}}' , str(estInfo['LaborOfficeId'])).replace('{{estSeq}}' , str(estInfo['SequanceNumber'])).replace('{{idNo}}', idNo)).fetchall()
    userInAccountManager = getPIA(
        {'Est': [estInfo['LaborOfficeId'], estInfo['SequanceNumber']], 'bodyJsons': APIsEnum.query_center_api_custom,
         'query': PMQueries.userInAccountManager.value, 'valsToReplave' : {'{{idNo}}', idNo}
         })
    userInUserSubscription = cursorQiwa.execute(PMQueries.userInUserSubscription.value.replace('{{estLab}}' , str(estInfo['LaborOfficeId'])).replace('{{estSeq}}' , str(estInfo['SequanceNumber'])).replace('{{idNo}}', idNo)).fetchall()
    isUserOnTheJob = getPIA(
        {'Est': [estInfo['LaborOfficeId'], estInfo['SequanceNumber']], 'bodyJsons': APIsEnum.query_center_api_custom,
         'query': PMQueries.isUserOnTheJob.value, 'valsToReplace' : {'idNo': idNo, 'estSeq': estInfo['SequanceNumber'] ,'estLab':estInfo['LaborOfficeId'] }
         })

    print(' userInUserSubscription ====> ', userInUserSubscription)
    if isEmpty(userInUserSubscription) :
        return PMAnswers.userNotInUserSubscription.value.replace('{{Est}}', str([estInfo['LaborOfficeId'], estInfo['SequanceNumber']])).replace('{{IdNo}}', str(idNo))


    #print (' RedundantPrivilegs ====> ' , RedundantPrivilegs) #1958743-10-1068021011
    print(' userInAccountManager ====> ', userInAccountManager)

    print(' isUserOnTheJob ====> ' , isUserOnTheJob)
    print('allPriv ===> ',allPriv)
    print('allPrivLenght ===> ',len(allPriv))

    # check if there is any redundant privileges
    Red1 =[]
    for priv in list(filter(lambda a:a[1] > 1,allPriv)):
        Red1.append(priv[0])
    print('Red1 = ', Red1)
    if len(Red1) > 0 :
        return 'لديك صلاحيات مكرره يجب حذفها وهي : \n \n' + str(Red1)


    currentPrivileges = [i[0] for i in allPriv]
    shouldBe = [i[0] for i in PS]
    missedPrivgs = []
    print('shouldBe ==> ', shouldBe)
    print('currentPrivileges ==> ', currentPrivileges)

    filtred = list(filter(lambda x: x[1] > 1, allPriv))


    if userInAccountManager is None or len(userInAccountManager) == 0 :
        return PMAnswers.IsNotAccountManager.value
    elif userInAccountManager[0]['UserType'] == '1' :
        return addPrivileges( shouldBe , currentPrivileges ,estInfo , result , idNo , cursorQiwa)

    elif userInAccountManager[0]['UserType'] == '2' :
        if isUserOnTheJob is None :
            return PMAnswers.IsNotAccountManager.value
        elif isUserOnTheJob is not None :
            if currentPrivileges == shouldBe:
                result += PMAnswers.NoNeedToAddPriv.value
                return result

            else:
                return addPrivileges(shouldBe , currentPrivileges  ,estInfo , result, idNo ,cursorQiwa)


def addPrivileges ( shouldBe , privgsOnly ,estInfo , result , idNo , cursorQiwa):
    if privgsOnly == shouldBe :
        result += PMAnswers.NoNeedToAddPriv.value
        return result

    missedPrivgs= list(filter(lambda x: x not in privgsOnly, shouldBe))

    if not isEmpty(missedPrivgs) and len(missedPrivgs) >0:
        result += 'هناك صلاحيات لم يتم إضافتها وهي  \n ' + str(missedPrivgs) +'\n'
        print('inside missedPrivgs == ' , missedPrivgs)
        getPIA(
        {'bodyJsons': APIsEnum.add_missing_privileges,
         'valsToReplace': {'par2': estInfo['SequanceNumber'], 'par1': estInfo['LaborOfficeId'], 'IdNo': idNo}
         })
        allPrivAfter = cursorQiwa.execute(
            PMQueries.RedundantPrivilegs.value.replace('{{idNo}}', idNo).replace('{{estLab}}', str(
                estInfo['LaborOfficeId'])).replace('{{estSeq}}', str(estInfo['SequanceNumber']))).fetchall()
        currentPrivilegesAfter = [i[0] for i in list(allPrivAfter)]
        print('currentPrivilegesAfter = ',currentPrivilegesAfter)
        time.sleep(5)
        if currentPrivilegesAfter == shouldBe :
            result += '\n تم إضافة الصلاحيات الناقصة بنجاح \n'
            return result
        else:
            missedPrivgs = list(filter(lambda x: x not in privgsOnly, shouldBe))
            result += '\n الرجاء التحقق مره اخرى  \n '
            return result
