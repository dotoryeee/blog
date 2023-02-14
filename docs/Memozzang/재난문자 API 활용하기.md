# 재난안전문자 API 활용하기

https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp?menuSeq=679

https://www.data.go.kr/iim/api/selectAPIAcountView.do

```python title="emergency_alert_to_slack.py" linenums="1"
import requests
import datetime

auth_key = ""
return_type = "json"
request_row = "1000"
target_message_time = 720 #cron 주기로 사용 할 분(minutes) 값을 입력한다. 1을 입력할 경우 최근 1분간 메시지만 전송한다.
target_location_ids = ["2", "21", "53", "74", "98", "104", "113", "119", "136", "162", "168", "179", "202", "217", "222", "238", "6474", "6474"]
# location_id는 다음 문서를 참조: https://www.data.go.kr/data/15066113/fileData.do 

slack_webhook_url = "https://hooks.slack.com/services/~~~~"

def load_messages() -> list: 
    """
    https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp?menuSeq=679 의 데이터 호출하는 함수
    https://www.data.go.kr/data/3058822/openapi.do API 사용
    auth_key: 이정원 계정의 인증키
    """
    r = requests.get(f'http://apis.data.go.kr/1741000/DisasterMsg3/getDisasterMsg1List?ServiceKey={auth_key}&type={return_type}&numOfRows={request_row}')
    return r.json()["DisasterMsg"][1]["row"]

def time_str_to_obj(time_str: str) -> object:
    """
    string type으로 제공되는 날짜데이터를 datetime object로 변환한다
    """
    time_obj = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S") #공공데이터 time format을 datetime object format으로 변환
    return time_obj

def time_kst_to_utc(time_obj: object) -> object:
    """
    KST datetime object를 입력받아 UTC datetime object를 리턴
    """
    time_obj += datetime.timedelta(hours = -9) # KST -> UTC 연산
    return time_obj

def check_message_time(message_time: object) -> bool:
    """
    target_message_time 변수값을 참조하여 지난 몇 분 사이에 생성된 메세지가 맞는지 검증한다 (timeWindow filtering)
    """
    if datetime.datetime.now() - datetime.timedelta(minutes = target_message_time) < message_time:
        return True
    return False

def check_location_id(location_id: str) -> bool:
    """
    location_id가 target_location_ids 리스트 내에 존재하는 경우에만 메세지 발송
    """
    if location_id in target_location_ids:
        return True
    return False

def send_slack_message(message: dict) -> None:
    """
    slack webhook을 이용해 slack channel로 메세시 발신하는 함수
    backslash parsing때문에 코드가 좀 어지럽습니다
    참고: chr92 = backslash
    """
    kst_time = time_str_to_obj(message['create_date'])
    utc_time = time_kst_to_utc(kst_time)

    if check_message_time(kst_time) & check_location_id(message["location_id"]):
        kst_msg = f"KST: {kst_time}"
        utc_msg = f"UTC: {utc_time}"
        location_msg = f"발송지역: {message['location_name']}"
        emergency_msg = message["msg"].replace("\n", "")
        payload={
            "text": f"{kst_msg} | {utc_msg} {chr(92)}n{location_msg} {chr(92)}n {emergency_msg}".replace("\\n", "\n")
        }
        requests.post(slack_webhook_url, json=payload)

def main():
    messages = load_messages()
    for message in messages:
        send_slack_message(message)
    
main()
```