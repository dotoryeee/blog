---
draft: false
date: 2025-03-10
authors:
  - dotoryeee
categories:
  - Network
  - Security
---
# HTTP와 TLS 간단 정리

<!-- more -->

---

##  HTTP 기본 통신 과정
``` mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: TCP 3-way Handshake (SYN, SYN-ACK, ACK)
    Client->>Server: HTTP Request (GET /index.html)
    Server-->>Client: HTTP Response (200 OK, HTML Content)
    Client->>Server: Additional Requests (CSS, JS, Images)
    Server-->>Client: Additional Responses
    Client->>Server: Keep-Alive or Connection Close
```
- TCP 3-way Handshake: 클라이언트와 서버 간 TCP 연결 수립
- HTTP Request/Response: 요청한 웹 페이지 데이터를 주고받음
- Keep-Alive: HTTP/1.1에서는 TCP 연결을 유지하여 성능 개선

##  HTTPS 적용 시 변경되는 과정
``` mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: TCP 3-way Handshake
    Client->>Server: TLS Handshake (ClientHello)
    Server-->>Client: ServerHello + Certificate
    Client->>Server: Key Exchange + Finished
    Server-->>Client: Finished (Encrypted)
    Client->>Server: Encrypted HTTP Request
    Server-->>Client: Encrypted HTTP Response
```

- TLS Handshake 추가: 서버 인증서 확인 및 세션 키 교환
- 데이터 암호화 적용: 이후의 HTTP 요청과 응답이 암호화됨

## HTTP 버전별 차이점
|HTTP 버전|TCP 세션 개수|특징|TLS 적용 시 차이점|
|-------|-----------|---|---------------|
|HTTP/1.1|여러 개 (보통 6개)|Keep-Alive 지원, 동시 요청 불가|TCP 세션별 TLS 핸드셰이크 필요 (부하 증가)|
|HTTP/2|1개만 사용|멀티플렉싱 지원, 헤더 압축(HPACK)|1개의 TLS 핸드셰이크만 필요 (성능 향상)|
|HTTP/3|1개만 사용 (UDP 기반)|QUIC 사용, 0-RTT 지원|TCP 핸드셰이크 없음, TLS 내장 (최적화됨)|

- HTTP/3는 UDP 기반이므로 Keep-Alive 개념이 없음, TLS 1.3 필수 적용됨 → 핸드셰이크 속도가 빠름

## TLS 버전별 차이점
|TLS 버전|핸드셰이크 RTT|암호화 방식|특징|
|-------|-----------|--------|---|
|TLS 1.0 / 1.1|2-RTT|CBC 모드 지원|보안 취약, 지원 중단|
|TLS 1.2|2-RTT|AES-GCM, SHA-256 지원|RSA 키 교환 가능, PFS 선택적 적용|
|TLS 1.3|1-RTT, 0-RTT|AES-GCM, ChaCha20|PFS 강제 적용, 0-RTT 지원|

- TLS 1.3에서는 0-RTT를 통해 세션 복구 속도를 대폭 개선
- TLS 1.2는 RSA 기반 키 교환을 지원하지만, TLS 1.3에서는 ECDHE만 사용

## TLS 1.3에서 0-RTT(Zero-RTT) 동작 원리
``` mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: ClientHello + Early Data (0-RTT)
    Server-->>Client: ServerHello + Finished
    Server-->>Client: Processing Early Data
    Client->>Server: Secure HTTP Request
    Server-->>Client: Secure HTTP Response
```

- 0-RTT(Zero-RTT): 과거 TLS 세션 정보를 활용하여 핸드셰이크 없이 즉시 데이터 전송
- 보안 이슈: 리플레이 공격 가능성이 있음 → 서버에서 제한적으로 허용

## 프리마스터 키(Pre-Master Secret)와 세션 키의 차이
|개념|설명|
|---|---------|
|프리마스터 키|클라이언트가 생성하여 서버로 전송하는 임시 키|
|어떻게 사용됨?|서버가 복호화하여 Master Secret 생성, 이후 세션 키 유도|
|세션 키(Session Key)|최종적으로 데이터를 암호화하는 키|
|TLS 1.2와 TLS 1.3 차이점|TLS 1.2는 RSA 기반 전달 가능, TLS 1.3은 ECDHE로 협상|

- 프리마스터 키는 한 번 사용되며, 이후 모든 암호화는 세션 키로 수행

## TLS 1.2에서 ECDHE 사용 시 단점
|단점|설명|
|---|--------|
|CPU 부하 증가|RSA보다 연산량 많음 (타원곡선 연산 필요)|
|세션 재사용 불가|Ephemeral Key(임시 키) 사용으로 세션 복구 불가능|
|메모리 사용 증가|클라이언트별 임시 키 저장 필요|

- TLS 1.3에서는 키 교환 과정을 최적화하여 이러한 단점을 해결함
  




