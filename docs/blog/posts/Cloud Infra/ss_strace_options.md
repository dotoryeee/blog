---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - Server
  - Network
description: "ss -nltp로 포트 점유 프로세스를 찾고 strace로 실패 시스템 콜을 역추적하는 트러블슈팅 옵션 조합 정리"
---

# ss, strace 트러블슈팅 옵션 정리

<!-- more -->

## 언제 쓰는가

- ss: 리스닝 포트와 소켓 상태, 그 소켓을 잡고 있는 프로세스를 확인하는 도구 (netstat 대체, iproute2 포함)
- strace: 프로세스가 호출하는 시스템 콜을 추적하는 도구
- 조합 워크플로: ss로 포트 점유 프로세스의 PID 확인 → strace로 해당 PID에 attach해 실패 원인 추적

---

## ss -nltp

```s
ss -nltp
State   Recv-Q  Send-Q   Local Address:Port   Peer Address:Port  Process
LISTEN  0       511            0.0.0.0:80          0.0.0.0:*      users:(("nginx",pid=1234,fd=6))
LISTEN  0       128            0.0.0.0:22          0.0.0.0:*      users:(("sshd",pid=890,fd=3))
```

|옵션|설명|
|---|---|
|-n|포트를 서비스명으로 변환하지 않고 숫자 그대로 출력 (조회 속도↑)|
|-l|LISTEN 상태 소켓만 출력|
|-t|TCP 소켓만 출력 (UDP는 -u)|
|-p|소켓을 소유한 프로세스명·PID 표시 (타 유저 프로세스는 root 권한 필요)|

- "어떤 프로세스가 이 포트를 물고 있는가"를 확인하는 가장 빠른 조합
- Recv-Q/Send-Q: LISTEN 소켓에서는 accept 대기 큐 사용량/최대치 → backlog 튜닝(somaxconn) 판단 근거

---

## strace -k -p <PID> -x -i -T -Z

```s
strace -k -p 1234 -x -i -T -Z
```

|옵션|설명|
|---|---|
|-k|각 시스템 콜의 유저 스택 트레이스 출력 → 어느 코드 경로에서 호출됐는지 확인|
|-p <PID>|실행 중인 프로세스에 attach (PID 인자 필수)|
|-x|비ASCII 문자열을 16진수로 출력 → 바이너리 데이터 식별|
|-i|시스템 콜 시점의 instruction pointer 출력|
|-T|각 시스템 콜에 소요된 시간 표시 → 느린 콜 식별|
|-Z|실패한 시스템 콜만 출력 (성공만 보려면 -z)|

- -Z로 실패 콜만 추리고 -k 스택 트레이스로 호출 지점까지 역추적하는 에러 원인 분석용 조합
- -T는 지연 분석용 → 어떤 콜에서 시간을 쓰는지 확인
- 운영 환경 주의: strace attach는 대상 프로세스를 크게 느리게 만들 수 있음 → 단시간만 붙였다 뗄 것

---

## 사용 사례

|상황|명령|
|---|---|
|포트 충돌 (bind 실패) 원인 프로세스 찾기|ss -nltp 로 점유 PID 확인|
|프로세스가 에러를 뱉는데 로그가 없음|strace -Z -k -p <PID> 로 실패 콜과 호출 스택 확인|
|특정 요청만 느림|strace -T -p <PID> 로 소요 시간 큰 콜 식별|
|accept 큐 넘침 의심|ss -nltp 의 Recv-Q가 Send-Q(backlog)에 근접하는지 확인|

## 결론

- ss는 "누가 물고 있는가", strace는 "안에서 무슨 일이 벌어지는가"를 보는 도구
- 포트 확인 → PID 추출 → strace attach 순서로 이어 쓰면 로그 없는 장애도 원인 추적 가능
