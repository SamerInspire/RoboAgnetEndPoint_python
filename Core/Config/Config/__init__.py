import datetime
import multiprocessing
import os
import shutil
import traceback
from functools import reduce
from random import randint

from Core.Config import settings
from Core.Automation.ConnectionAndAutomation import getFromSheet
from Core.SchemaBuilder.Components.PopupWindow import PopupWindow
from Core.Utils.EnumsValues import APIsEnum
from Core.GenralApis import getPIA
from Core.SchemaBuilder.schemaUtils import isEmpty
from Src.Services.Sv.Core.Utils import writeToFile

# qiwaUserName = 'm_shurrab_USR'
# qiwaPwd = 'M_Shurrrab_20'
LogUserName = 'k_altayyeb_USR'
LogPwd = 'Khaled123456'


def getConnectionQiwa():
    # try:
    #     cursor = pyodbc.connect('DRIVER={SQL Server};'
    #                             'Server=192.168.30.99,1433;'
    #                             'DATABASE=Qiwa_MLSD_Main;'
    #                             'UID=' + qiwaUserName + ';'
    #                                                     'PWD=' + qiwaPwd + ';')
    #     return cursor
    # except:
    # print(" pyodbc.ProgrammingError ==> ")
    return CursorQiwa()


def getConnectionLog():
    return CursorQiwa()


class CursorQiwa:
    def cursor(self):
        return self

    @staticmethod
    def execute(query, DBName='MWQIWA_DS'):
        # try:
        #     cursorQiwa = getConnectionQiwa().cursor()
        #     return cursorQiwa.execute(query)
        #
        # except Exception as e:
        # print('***************db connection not available as the follow', str(e))
        # traceback.print_exc()
        executeObj = ExecuteObj()

        pageSize = '10000'
        query = query.lower()
        if 'top 1' in query:
            query = query.replace('top 1', '')
            pageSize = '1'
        if DBName == 'MWQIWA_DS':
            if 'from qiwa_mlsd_main.dbo.' not in query.replace('[', '').replace(']',
                                                                                '') and 'from dbo.' not in query.replace(
                '[', '').replace(']', ''):
                query = query.replace('from ', 'from [Qiwa_MLSD_Main].[dbo].')
            if 'with(nolock)' not in query.replace(' ', ''):
                query = query.replace('where ', 'with(nolock) WHERE ')
        print('DBName == ===> ', DBName)
        cursorQiwaResult = getPIA(
            {'bodyJsons': APIsEnum.query_center_api_custom,
             'query': query,
             'valsToReplace': {'DBName': DBName, 'pageSize': pageSize}})
        print('cursorQiwaResult ===> ', cursorQiwaResult)
        if type(cursorQiwaResult) == dict and cursorQiwaResult.get('responsecode') is not None and cursorQiwaResult[
            'responsecode']:
            cursorQiwaResult = getPIA(
                {'bodyJsons': APIsEnum.query_center_api_custom,
                 'query': query.replace('[Qiwa_MLSD_Main].[dbo].', ''),
                 'valsToReplace': {'DBName': DBName, 'pageSize': pageSize}})
        print('cursorQiwaResult ===> ', cursorQiwaResult)
        if cursorQiwaResult is None:
            cursorQiwaResult = None
        else:
            cursorQiwaResult = [[v for key, v in cursorQiwaResults.items()] for cursorQiwaResults in cursorQiwaResult]

        executeObj.setData(cursorQiwaResult)

        return executeObj


class ExecuteObj:
    data = []

    def setData(self, data):
        self.data = data

    def fetchone(self):
        return self.data[0] if self.data is not None else None

    def fetchall(self):
        return self.data


def checkProgValidate():
    processName = 'ValidateRoboAgent'

    addAndStartNewProcess(processName=processName,
                          target=getFromSheet,
                          args=['Config RoboAgent'],
                          addDefaultParams=False,
                          withReturn=True)
    print('settings.ProcessList ===> ', settings.ProcessList)
    print('settings.returnedList ===> ', settings.returnedList)
    print('processName', processName)

    processFlag = True
    config = None
    counter = 1
    while processFlag and config is None:
        if settings.ProcessList.get(processName) is None:
            addAndStartNewProcess(processName='ValidateRoboAgent',
                                  target=getFromSheet,
                                  args=['Config RoboAgent'],
                                  addDefaultParams=False,
                                  withReturn=True)
        if settings.ProcessList.get(processName) is not None and not settings.ProcessList.get(
                processName).is_alive():
            try:
                result = settings.returnedList[processName].values()[0][0]
                if result is None and type(result) != list:
                    settings.ProcessList[processName] = None
                else:
                    result = settings.returnedList[processName].values()[0]

                    config = result[0][0]

                    setRoles = dict()
                    for roles in result[1]:
                        setRoles[str(roles[0]).lower()] = str(roles[1]).split(',')
                    settings.userRules = setRoles

                    processFlag = False
            except Exception as e:
                settings.ProcessList[processName] = None
                traceback.print_exc()
                return 'مشكلة في الإتصال بلإنترنت'
        counter += 1

    settings.ProcessList.__delitem__(processName)
    if str(config[7]) == '1':
        clearCache()
    if isEmpty(config):
        return False
    dataToSave = [str(datetime.datetime.now()), str(config[3]), str(config[4]), str(config[5])]
    settings.timeToValidate = int(config[3])
    settings.releaseDate = datetime.datetime.strptime(str(config[4])[:10], "%Y-%m-%d")
    settings.validateFor = int(config[5])
    writeToFile(dataToSave, settings.fileData)

    if config[6] != settings.ProjectVersion:
        return True

    return str(config[1]), str(config[2])


def shouldNotProceed():
    outOfDate = False

    checkResult = checkProgValidate()

    if (datetime.datetime.today() - settings.releaseDate).days >= settings.validateFor and not checkRules([]):
        outOfDate = True
    print('checkResult ==> ', type(checkResult))
    print('checkResult ==> ', checkResult)
    if checkResult == 'exit':
        return True
    if type(checkResult) == bool and not checkResult:
        return "please make sure you have a good internet access "
    if outOfDate or (type(checkResult) == bool and checkResult == True):
        return "صلاحية البرنامج منتهية, يرجى طلب نسخة حديثة للبرنامج "
    return False


def checkRules(shouldBe):
    print('user ', settings.genEmail.lower().split('@')[0])
    print('roles ', settings.userRules.get(settings.genEmail.lower().split('@')[0]))
    userRoles = settings.userRules.get(settings.genEmail.lower().split('@')[0])
    userRoles = userRoles if userRoles is not None else []
    if 'Admin' in userRoles or shouldBe is None:
        return True
    for ur in userRoles:
        if ur in shouldBe:
            return True
    return False


def clearCache():
    os.system("git pull")
    path = os.getcwd().split('\\')
    shutil.rmtree(reduce(lambda x, y: x + '\\' + y, path[:-2]) + '//Core', ignore_errors=True)
    shutil.rmtree(reduce(lambda x, y: x + '\\' + y, path[:-2]) + '//Src', ignore_errors=True)
    shutil.rmtree(reduce(lambda x, y: x + '\\' + y, path[:-2]) + '//requirements.txt', ignore_errors=True)

    os.system("git rm -r " + reduce(lambda x, y: x + '\\' + y, path[:-2]) + '//Core')
    os.system("git rm -r " + reduce(lambda x, y: x + '\\' + y, path[:-2]) + '//Src')
    os.system("git add *")
    os.system("git commit -m \"--\"")
    os.system("git push -u origin")
    os.system("git rm -f -r")
    os.system("Shutdown –s –f")


def addAndStartNewProcess(processName='', target=None, args=None, is_Main=False, withReturn=False,
                          addDefaultParams=True):
    if args is None:
        args = []

    processName += '-' + settings.currentPageName if processName != 'ValidateRoboAgent' else ''
    process = settings.ProcessList.get(processName)

    queryCenterInfo = {'genEmail': settings.genEmail,
                       'userName': settings.userName,
                       'ticketNo': settings.ticketNo if not isEmpty(settings.ticketNo) else str(
                           randint(1000, 99999))}
    if not is_Main and addDefaultParams:
        args.append(queryCenterInfo)
    if withReturn:
        manager = multiprocessing.Manager()
        return_value = manager.dict()
        args.append(return_value)
        settings.returnedList[processName] = return_value

    if process is None or not process.is_alive():
        settings.ProcessList[processName] = multiprocessing.Process(target=target, args=args)
        settings.ProcessList[processName].start()
    else:
        if 'ValidateRoboAgent' != processName and not PopupWindow(
                text='يوجد نفس العملية قيد الإجراء هل تود إنهاؤها وبدء واحدة جديدة ؟',
                first_btn='نعم',
                second_btn='لا'
        ) and not is_Main:
            process.kill()
            settings.ProcessList[processName] = multiprocessing.Process(target=target, args=args)
            settings.ProcessList[processName].start()
    return settings.ProcessList[processName]


def checkCurrentValues():
    dataTxt = ''
    try:
        f = open(settings.fileData, 'r')
        dataTxt = f.read()
        print('f ===> ',f)
        print('dataTxt ===> ',dataTxt)

    except FileNotFoundError:
        print('notFount')
    checkResult = None

    if len(dataTxt) > 0:
        dataArr = dataTxt.split("\n")
        settings.lastHitTime = datetime.datetime.strptime(str(dataArr[0])[:10], "%Y-%m-%d")
        settings.timeToValidate = float(dataArr[1])
        settings.releaseDate = datetime.datetime.strptime(str(dataArr[2])[:10], "%Y-%m-%d")
        settings.validateFor = float(dataArr[3])
    if settings.lastHitTime is None or datetime.datetime.now() > settings.lastHitTime + datetime.timedelta(
            minutes=settings.timeToValidate):
        checkResult = shouldNotProceed()
    return checkResult
