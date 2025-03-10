---
draft: false
date: 2025-03-10
authors:
  - dotoryeee
categories:
  - Network
---
# Websocket 정리

<!-- more -->

# WebSocket 세션 수립 및 종료 과정

---

## WebSocket 세션 수립 과정 (Handshake)

WebSocket은 HTTP 프로토콜을 사용하여 핸드셰이크를 수행한 후, 지속적인 양방향 통신을 지원합니다.

| 단계 | 설명 |
|------|-------------------------------|
| 1 | 클라이언트가 `HTTP GET` 요청을 보냄 (`Upgrade: websocket` 헤더 포함) |
| 2 | 서버가 `101 Switching Protocols` 응답을 반환 (WebSocket 프로토콜 전환 승인) |
| 3 | TCP 연결이 유지되며 이후 WebSocket 프레임을 주고받음 |
| 4 | 클라이언트와 서버가 양방향 메시지 전송 가능 |


``` mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: HTTP GET /chat <br> Upgrade: websocket
    Server-->>Client: HTTP 101 Switching Protocols
    Client->>Server: WebSocket 메시지 전송
    Server-->>Client: WebSocket 메시지 응답
```

## WebSocket Graceful 종료 과정 (정상적인 연결 해제)

|단계|설명|
|---|---------|
|1|클라이언트 또는 서버가 Close Frame(종료 요청)을 보냄|
|2|상대방이 Close Frame(응답)을 보냄|
|3|TCP 연결 종료 및 세션 해제|

``` mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: Close Frame (Code=1000, "Normal Closure")
    Server-->>Client: Close Frame 응답 (Code=1000, "OK")
    Client->>Server: TCP 연결 종료
    Server-->>Client: 세션 해제 완료
```

## WebSocket Timeout에 의한 종료 과정

클라이언트가 갑자기 종료되거나 네트워크 문제로 인해 연결이 끊어졌을 때, 서버는 일정 시간 동안 클라이언트 응답을 기다린 후 연결을 종료합니다.

|단계|설명|
|---|---------|
|1|서버가 일정 주기로 Ping 프레임(연결 상태 확인 요청)을 보냄|
|2|정상적인 클라이언트는 Pong 프레임(응답)을 반환|
|3|일정 시간 내 응답이 없으면 서버가 연결을 Timeout으로 간주하고 강제 종료|

``` mermaid
sequenceDiagram
    participant Client
    participant Server

    Server->>Client: Ping Frame 전송 (연결 확인)
    Client-->>Server: (응답 없음)
    Server->>Client: Ping Frame 재전송
    Client-->>Server: (응답 없음)
    Server-->>Client: 연결 Timeout (Connection Closed)
```
