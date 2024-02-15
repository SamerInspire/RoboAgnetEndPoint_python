# coding=utf8

import requests

from Core.Config import settings
from Core.Utils.EnumsValues import APIsEnum, getUrlBody


def getEstablishmentInfo(Est):
    responseInfo_json = getPIA({'Est': Est, 'bodyJsons': APIsEnum.est_info_api})
    if responseInfo_json['GetEstablishmentInformationRs'].get('Body') is None:
        return None
    ED = responseInfo_json['GetEstablishmentInformationRs']['Body']['ED']

    return ED


def getPIARegular(props):
    bodyJson = props.get('bodyJsons').value

    get_url_body_headers = getUrlBody(props.get('bodyJsons').name, props.get('Est'), props.get('query'),
                                      props.get('valsToReplace'))

    if props.get('headers') is not None:
        headers = {**get_url_body_headers[2], **props['headers']}
    else:
        headers = get_url_body_headers[2]
    print('get_url_body_headers ', get_url_body_headers)
    if get_url_body_headers[1] is None or (bodyJson.get('mType') == 'get'):
        responseInfo = requests.request("GET", get_url_body_headers[0], headers=get_url_body_headers[2])
    elif get_url_body_headers[1] is None or (bodyJson.get('mType') == 'put'):
        print('bodyJson sadsadsadsadsadsadsawqeqweeqw', get_url_body_headers)
        responseInfo = requests.request("PUT", get_url_body_headers[0], headers=get_url_body_headers[2],
                                        data=get_url_body_headers[1].encode('utf-8'))
    else:
        responseInfo = requests.request("POST", get_url_body_headers[0], headers=headers,
                                        data=get_url_body_headers[1].replace('\\', ''))

    if props.get('bodyJsons').name == APIsEnum.cr_information_api.name:
        responseInfo = responseInfo.json()
        while responseInfo['CrDetailsRs'].get('Body') is None:
            responseInfo = requests.request("POST", get_url_body_headers[0], headers=headers,
                                            data=get_url_body_headers[1].replace('\\', ''))
            responseInfo = responseInfo.json()
    return responseInfo


def getPIA(props):
    headers = {
        'X-IBM-Client-Id': '7ba45647aa95402d0c898f776feeac1a',
        'X-IBM-Client-Secret': '35581a93a21003d648a5019ce3dc231d',
        'Content-Type': 'application/json'
    }
    get_url_body = getUrlBody(props.get('bodyJsons').name, props.get('Est'), props.get('query'),
                              props.get('valsToReplace'))
    if get_url_body[1] is None or props.get('type') == 'get':
        responseInfo = requests.request("GET", get_url_body[0], headers=headers)
    else:
        responseInfo = requests.request("POST", get_url_body[0], headers=headers,
                                        data=get_url_body[1].replace('\\', ''))
    print('bodyJsons ==', props.get('bodyJsons').name)
    print('get_url_body[0] ==', get_url_body[1])
    print('get_url_body[1] ==', get_url_body[0])
    print('headers ==', headers)
    print('Timeout ===> ', responseInfo.elapsed.total_seconds())
    if props.get('bodyJsons').name == 'nitaq_Info_qiwa_new' and responseInfo.status_code != 200:
        return None
    assert responseInfo.status_code == 200, f"The service is down: {responseInfo.status_code} \nurl = " + get_url_body[
        0] + "\nheaders = " + str(headers) + "\nbody" + get_url_body[1]
    print('response ===> ', responseInfo.content.decode('utf-8'))
    responseInfo = responseInfo.json()
    if props.get('bodyJsons').name == APIsEnum.validate_api.name:
        body = responseInfo['ValidateEstablishingExpansionRequestRs'].get('Body')
        if body is None :
            ResponseStatus = responseInfo['ValidateEstablishingExpansionRequestRs']['Header']['ResponseStatus']
            if ResponseStatus['Code'] == 'E0000065':
                return ResponseStatus['ArabicMsg']

        if body.get('ValidationsErrorsList') is not None and type(
                body['ValidationsErrorsList']['ValidationError']) == dict:
            responseCode = body['ValidationsErrorsList']['ValidationError']['ErrorCode']
            print('querycenter ==> ', settings.userName)
            if responseCode in ['E9999998']:
                count = 1

                while responseCode in ['E9999998'] and count <= 50:
                    print(get_url_body)
                    responseInfo = requests.request("POST", get_url_body[0], headers=headers,
                                                    data=get_url_body[1].replace('\\', ''))
                    assert responseInfo.status_code == 200, f"The service is down: {responseInfo.status_code}"
                    responseInfo = responseInfo.json()
                    print(responseInfo)
                    if body.get('ValidationsErrorsList') is not None and type(
                            body['ValidationsErrorsList']['ValidationError']) == dict:
                        responseCode = \
                        responseInfo['ValidateEstablishingExpansionRequestRs']['Body']['ValidationsErrorsList'][
                            'ValidationError']['ErrorCode']
                    else:
                        break

                    count += 1
            assert responseCode not in ['E9999998'], f" API is not returning data, try again please: {responseCode}"

    if props.get('bodyJsons').name == APIsEnum.query_center_api_custom.name:
        print("Semo ---> responseInfo ==> ", responseInfo)
        if responseInfo.get('Header') is not None:
            responseInfo['CustomQueryRs'] = responseInfo
        if responseInfo.get('CustomQueryRs') is None:
            return None
        responseCode = responseInfo['CustomQueryRs']['Header']['responsecode']
        response = responseInfo['CustomQueryRs']['Header']['response']
        print("Semo ---> responseCode ==> ", responseCode)

        assert responseCode != '9979', f"the username changed, login again"
        assert responseCode != '9980', f"Query Center Didn't understand the query... "
        if str(responseCode) == '208':
            return None
        print('responseCode==> ', responseCode)
        print('responseInfo ==>', responseInfo)
        if response == 'An internal error occurred while processing the SQL response':
            # assert response != 'An internal error occurred while processing the SQL response', f"The Query Center is facing Problem with result (garbage data) "
            return "\n يوجد مشكلة في بيانات الموظف (إسم الموظف أو معلومات أخرى لا يمكن إسترجاعها لدينا ) \n \n \n\n\n يرجى تزويدنا بصورة من إسم الموظف في أبشر و رقم إقامته/الحدود \n"
        print('responseInfo flaf ==>', str(responseCode) in ['9999', '9992'])

        if str(responseCode) in ['9999', '9992']:
            count = 1

            while responseCode in ['9999', '9992'] and count <= 10:
                print('query center retry ... ', get_url_body)
                responseInfo = requests.request("POST", get_url_body[0], headers=headers,
                                                data=get_url_body[1].replace('\\', ''))
                assert responseInfo.status_code == 200, f"The service is down: {responseInfo.status_code}"
                responseInfo = responseInfo.json()
                print(responseInfo)
                if responseInfo.get('Header') is not None:
                    responseInfo['CustomQueryRs'] = responseInfo
                responseCode = responseInfo['CustomQueryRs']['Header']['responsecode']

                count += 1

        assert responseCode not in ['9999', '9992'], f"The Query center is not returning data: {responseCode}"

        if responseCode in ['9988', '9979']:
            return None

        # assert responseInfo['CustomQueryRs'].get(
        #     'Body') is not None, f"QueryCenter is didn't return data: \n body : {get_url_body[1]} \n responseInfo :{responseInfo}"
        print('responseCode ===> ', responseCode)
        if str(responseCode) in ['117']:
            responseInfo = responseInfo['CustomQueryRs']['Header']
        else:
            responseInfo = responseInfo['CustomQueryRs']['Body']['QueryRs'][0]['Records']

    return responseInfo
