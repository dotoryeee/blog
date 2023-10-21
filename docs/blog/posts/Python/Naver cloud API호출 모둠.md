---
draft: false
date: 1993-09-17
authors:
  - dotoryeee
categories:
  - Python
---
# Naver cloud API 호출 예시
<!-- more -->
1. 인스턴스 리스트 확인
    ```python title="API_instanceList.py " linenums="1"
    import requests
    import hashlib
    import hmac
    import base64
    import requests
    import time
    import xmltodict

    ######################################################
    ACCESS_KEY = "********************"
    SECRET_KEY = "********************"
    ######################################################

    method = "GET"
    url = "https://ncloud.apigw.ntruss.com"
    uri = "/vserver/v2/getServerInstanceList"

    time_stamp = str(int(time.time() * 1000))


    def make_signature():
        secret_key = bytes(SECRET_KEY, "UTF-8")
        message = method + " " + uri + "\n" + time_stamp + "\n" + ACCESS_KEY
        message = bytes(message, "UTF-8")
        signKey = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
        )
        return signKey


    def main():
        signKey = make_signature()
        headers = {
            "x-ncp-iam-access-key": ACCESS_KEY,
            "x-ncp-apigw-timestamp": time_stamp,
            "x-ncp-apigw-signature-v2": signKey,
        }
        r = requests.get(url + uri, headers=headers)
        returnCode = r.status_code
        if returnCode == 200:
            data = r.text
            data = xmltodict.parse(data)
            data = data["getServerInstanceListResponse"]["serverInstanceList"][
                "serverInstance"
            ]
            print("----------------------서버 목록--------------------------")
            print("  서버이름\t\t 인스턴스ID\t   상태\t\t퍼블릭IP")
            for i in data:
                print(
                    f'{i["serverName"].ljust(20)}\t  {i["serverInstanceNo"]}\t  {i["serverInstanceStatusName"]}\t  {i["publicIp"]}'
                )
            print("--------------------------------------------------------")
        else:
            print(f"Error Code: {returnCode} / {r.text}")


    main()
    ```

2. 인스턴스 켜기
    ```python title="API_startInstance.py" linenums="1"
    import requests
    import hashlib
    import hmac
    import base64
    import requests
    import time
    import json

    ######################################################
    ACCESS_KEY = "********************"
    SECRET_KEY = "********************"
    TARGET_INSTANCE_IDs = ["6768447"]
    ######################################################


    method = "GET"
    url = "https://ncloud.apigw.ntruss.com"
    uri = "/vserver/v2/startServerInstances?responseFormatType=json"


    for num, ID in enumerate(TARGET_INSTANCE_IDs):
        uri = f"{uri}&serverInstanceNoList.{num+1}={ID}"


    time_stamp = str(int(time.time() * 1000))


    def make_signature():
        secret_key = bytes(SECRET_KEY, "UTF-8")
        message = method + " " + uri + "\n" + time_stamp + "\n" + ACCESS_KEY
        message = bytes(message, "UTF-8")
        signKey = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
        )
        return signKey


    def main():
        # print(f"REQUEST {url + uri}")
        signKey = make_signature()
        headers = {
            "x-ncp-iam-access-key": ACCESS_KEY,
            "x-ncp-apigw-timestamp": time_stamp,
            "x-ncp-apigw-signature-v2": signKey,
        }
        r = requests.get(url + uri, headers=headers)
        returnCode = r.status_code
        if returnCode == 200:
            data = json.loads(r.text)
            data = data["startServerInstancesResponse"]["returnMessage"]
            print(f"START REQUEST : {data}")
        else:
            print(f"Error Code: {returnCode} / {r.text}")


    main()
    ```
3. Target Group에 등록하기
    ```python title="API_appendInstanceToTG.py" linenums="1"
    import requests
    import hashlib
    import hmac
    import base64
    import requests
    import time
    import json

    ######################################################
    ACCESS_KEY = "********************"
    SECRET_KEY = "********************"
    TARGET_GROUP_NO = "64385"
    TARGET_INSTANCE_IDs = ["6799106"]
    ######################################################


    method = "GET"
    url = "https://ncloud.apigw.ntruss.com"
    uri = "/vloadbalancer/v2/addTarget?responseFormatType=json"
    uri = f"{uri}&targetGroupNo={TARGET_GROUP_NO}"
    for num, ID in enumerate(TARGET_INSTANCE_IDs):
        uri = f"{uri}&targetNoList.{num+1}={ID}"

    time_stamp = str(int(time.time() * 1000))


    def make_signature():
        secret_key = bytes(SECRET_KEY, "UTF-8")
        message = method + " " + uri + "\n" + time_stamp + "\n" + ACCESS_KEY
        message = bytes(message, "UTF-8")
        signKey = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
        )
        return signKey


    def main():
        # print(f"REQUEST {url + uri}")
        signKey = make_signature()
        headers = {
            "x-ncp-iam-access-key": ACCESS_KEY,
            "x-ncp-apigw-timestamp": time_stamp,
            "x-ncp-apigw-signature-v2": signKey,
        }
        print(url + uri)
        r = requests.get(url + uri, headers=headers)
        returnCode = r.status_code
        if returnCode == 200:
            data = json.loads(r.text)
            print(data["addTargetResponse"]["returnMessage"])
        else:
            print(f"HTTP Error Code: {returnCode} / {r.text}")


    main()
    ```
4. Target Group 현재 대상 조회
    ```python linenums="1"
    import requests
    import hashlib
    import hmac
    import base64
    import requests
    import time
    import json

    ######################################################
    ACCESS_KEY = "********************"
    SECRET_KEY = "********************"
    TARGET_GROUP_NO = "64385"
    ######################################################


    method = "GET"
    url = "https://ncloud.apigw.ntruss.com"
    uri = "/vloadbalancer/v2/getTargetGroupDetail?responseFormatType=json"
    uri = f"{uri}&targetGroupNo={TARGET_GROUP_NO}"

    time_stamp = str(int(time.time() * 1000))


    def make_signature():
        secret_key = bytes(SECRET_KEY, "UTF-8")
        message = method + " " + uri + "\n" + time_stamp + "\n" + ACCESS_KEY
        message = bytes(message, "UTF-8")
        signKey = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
        )
        return signKey


    def main():
        # print(f"REQUEST {url + uri}")
        signKey = make_signature()
        headers = {
            "x-ncp-iam-access-key": ACCESS_KEY,
            "x-ncp-apigw-timestamp": time_stamp,
            "x-ncp-apigw-signature-v2": signKey,
        }
        print(url + uri)
        r = requests.get(url + uri, headers=headers)
        returnCode = r.status_code
        if returnCode == 200:
            data = json.loads(r.text)
            print(
                data["getTargetGroupDetailResponse"]["targetGroupList"][0]["targetNoList"]
            )
        else:
            print(f"HTTP Error Code: {returnCode} / {r.text}")


    main()
    ```

