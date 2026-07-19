---
draft: false
date: 2025-03-18
authors:
  - dotoryeee
categories:
  - server
---
# EDNS 란

<!-- more -->

## 중요한 이유
- 2019년 DNS Flag Day부터 주요 퍼블릭 DNS 리졸버(Google, Cloudflare 등)가 EDNS 쿼리에 응답하지 않는 비표준 DNS 서버에 대한 재시도 워크어라운드를 중단 → 해당 서버는 조회 실패로 사실상 서비스 불가
- EDNS 미구현이어도 규격대로 응답(FORMERR 반환 또는 OPT 없이 응답)하는 서버는 Flag Day 이후에도 정상 동작

## 비교표

| 구분 | EDNS 사용 시 | EDNS 미사용 시 |
|------|-------------|--------------|
| 패킷 크기 (UDP) | 512바이트 초과 가능 (통상 1232~4096바이트 광고) | 512바이트 제한, 초과 시 TC 비트로 TCP 폴백 필요 |
| 플래그 필드 | 16비트 확장 플래그 필드 추가 (현재 DO 비트만 정의) | 헤더 기본 플래그만 사용 |
| 응답 코드 | 확장된 응답 코드 공간 | 제한된 응답 코드 |
| DNSSEC 지원 | 지원 (필수적) | 미지원 |
| 지리적 위치 정보 | EDNS Client Subnet(ECS) 옵션으로 전송 가능 | 불가능 |
| 패킷 처리 | 대용량 패킷 처리 가능 | 대용량 패킷 처리 불가 |
| 보안 | 향상된 보안 기능 지원 | 제한된 보안 기능 |
| 방화벽 호환성 | 일부 방화벽에서 문제 발생 가능 | 대부분의 방화벽과 호환 |
| DNS 증폭 공격 | 가능성 증가 | 상대적으로 낮은 위험 |
| 프로토콜 확장성 | 향후 기능 추가 용이 | 확장 어려움 |

## 동작 방식
``` mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: DNS 쿼리 + OPT 레코드 (UDP 페이로드 크기 광고, DO=1)
    Server-->>Client: 응답 + OPT 레코드 (512바이트 초과 응답, DNSSEC 서명 포함)
    Note over Client,Server: EDNS 미지원 서버는 OPT 무시 또는 FORMERR 응답
```

- EDNS는 헤더를 바꾸지 않고 OPT 의사 레코드(pseudo-RR)를 Additional 섹션에 실어 기능을 확장하는 방식 (RFC 6891)
- DNSSEC, ECS 같은 확장 기능이 모두 이 OPT 레코드 위에서 동작

