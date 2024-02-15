import os
from itertools import islice


def gettingTableName(insertDate):
    if insertDate.year >= 2000:
        year = insertDate.year - 2000
    else:
        year = insertDate.year - 1000
    tablesName = []
    quarter = str(int((insertDate.month - 1) / 3 + 1))
    tablesName.append("ESB_LOGGER_" + str(year) + "_Q" + quarter)

    if insertDate.month == 10:
        tablesName.append("ESB_LOGGER_" + str(year) + "_Q3")
    if insertDate.month == 4:
        tablesName.append("ESB_LOGGER_" + str(year) + "_Q1")
    if insertDate.month == 6:
        tablesName.append("ESB_LOGGER_" + str(year) + "_Q3")
    if insertDate.month == 12:
        tablesName.append("ESB_LOGGER_" + str(year + 1) + "_Q1")
    if insertDate.month == 12 or insertDate.month == 6 or insertDate.month == 4 or insertDate.month == 10:
        print(insertDate)
        print(tablesName)

    return tablesName


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def getThePath(excelPath, addFolders=None):
    pathToWrite = ''
    arr = excelPath.split('/')

    for i in range(len(arr)):
        pathToWrite = pathToWrite + arr[i] + '/'
        if not os.path.exists(pathToWrite):
            os.mkdir(pathToWrite)
    pathToWrite = pathToWrite[:-1] if pathToWrite[-1] == '/' else pathToWrite

    if addFolders is not None:
        if addFolders.__contains__('/'):
            addFoldersArr = addFolders.split('/')
            for i in range(len(addFolders.split('/'))):
                pathToWrite = pathToWrite + '/' + addFoldersArr[i]
                if not os.path.exists(pathToWrite):
                    os.mkdir(pathToWrite)
        else:
            pathToWrite = pathToWrite + '/' + addFolders
            if not os.path.exists(pathToWrite):
                os.mkdir(pathToWrite)

    pathToWrite = pathToWrite + '/'
    return pathToWrite


def writeToFile(contentArr, fileName):
    with open(r'' + fileName, "w", encoding="utf-8") as f:
        for content in contentArr:
            print(content)
            f.write(str(content).replace('------', '\n'))
            f.write("\n")


def replaceTextBetween(originalText, delimeterA, delimterB, replacementText):
    leadingText = originalText.split(delimeterA)[0]
    trailingText = originalText.split(delimterB)[1]

    return leadingText + replacementText + trailingText


def getFullName(fullNmObj):
    lastName = fullNmObj['FourthName'] if fullNmObj.get('FourthName') is not None else fullNmObj['LastName']
    return str(fullNmObj['FirstName']) + str(fullNmObj['SecondName']) + str(fullNmObj['ThirdName']) + str(
        lastName)


def getNameAsArr(fullNmObj):
    lastName = fullNmObj['FourthName'] if fullNmObj.get('FourthName') is not None else fullNmObj['LastName']
    return [str(fullNmObj['FirstName']), str(fullNmObj['SecondName']), str(fullNmObj['ThirdName']), str(
        lastName)]
