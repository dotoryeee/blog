---
draft: false
date: 2025-05-11
authors:
  - dotoryeee
categories:
  - Network
---
# HTTP status code 정리

<!-- more -->

## HTTP 상태 코드 주요 20개 정리

| **상태 코드** | **메시지**               | **원인** | **동작 방식** |
|--------------|----------------|-----------------------------------|-----------------------------------|
| **200**      | OK             | 요청이 정상적으로 처리됨 | 서버가 요청된 리소스를 정상 반환 |
| **201**      | Created        | 요청이 성공하여 리소스가 새로 생성됨 | `POST` 요청으로 리소스 생성 시 반환 |
| **204**      | No Content     | 요청 성공, 응답 본문이 없음 | `DELETE` 요청 등에서 응답 없이 완료됨 |
| **301**      | Moved Permanently | 요청한 리소스가 영구적으로 이동됨 | 클라이언트는 새로운 URL로 자동 리다이렉트 |
| **302**      | Found          | 리소스가 임시로 이동됨 | `Location` 헤더를 사용해 임시 URL 제공 |
| **304**      | Not Modified   | 클라이언트가 가진 캐시된 데이터가 최신 상태임 | `If-Modified-Since` 요청 헤더와 함께 동작 |
| **400**      | Bad Request    | 요청이 잘못되었거나 서버가 이해할 수 없음 | 잘못된 쿼리, JSON 형식 오류 등에서 발생 |
| **401**      | Unauthorized   | 클라이언트가 인증되지 않음 | `WWW-Authenticate` 헤더로 인증 요구 |
| **403**      | Forbidden      | 클라이언트가 접근 권한 없음 | 인증되었지만 권한 부족 (예: 관리자 전용 페이지) |
| **404**      | Not Found      | 요청한 리소스를 찾을 수 없음 | 존재하지 않는 URL 요청 시 발생 |
| **405**      | Method Not Allowed | 요청한 HTTP 메서드가 지원되지 않음 | `GET` 요청만 허용된 엔드포인트에 `POST` 요청한 경우 |
| **408**      | Request Timeout | 클라이언트가 요청을 너무 오래 걸림 | 서버가 일정 시간 내 응답을 받지 못하면 종료 |
| **409**      | Conflict       | 요청이 현재 서버 상태와 충돌 | 중복된 리소스 생성 시 발생 |
| **413**      | Payload Too Large | 요청 본문이 서버가 허용하는 크기를 초과 | 대용량 파일 업로드 시 발생 |
| **429**      | Too Many Requests | 클라이언트가 너무 많은 요청을 보냄 | `Rate Limiting` 정책에 의해 차단 |
| **500**      | Internal Server Error | 서버 내부 오류 발생 | 예외 처리 미흡으로 인해 발생 |
| **502**      | Bad Gateway    | 게이트웨이 또는 프록시 서버가 잘못된 응답 수신 | 백엔드 서버 다운 시 발생 |
| **503**      | Service Unavailable | 서버가 과부하 또는 유지보수 중 | 서버가 일시적으로 요청을 처리할 수 없음 |
| **504**      | Gateway Timeout | 서버가 백엔드 서버로부터 응답을 받지 못함 | 프록시 서버에서 백엔드 서버 응답 지연 시 발생 |

---

## 주요 상태 코드 설명

### 200 OK
- 요청이 정상적으로 처리되었으며, 응답 본문이 함께 전달됨
- `GET`, `POST`, `PUT`, `DELETE` 요청이 성공적으로 완료되었을 때 사용됨

### 301 Moved Permanently
- 요청한 URL이 영구적으로 이동되었음을 의미
- 클라이언트는 `Location` 헤더의 새 URL로 자동 리다이렉트해야 함

### 401 Unauthorized vs 403 Forbidden
| 상태 코드 | 의미 |
|----------|------|
| **401** Unauthorized | 인증이 필요하지만 제공되지 않았거나 실패함 (예: 로그인 필요) |
| **403** Forbidden | 인증되었지만 접근 권한 없음 (예: 관리자가 아닌 사용자가 관리자 페이지 접근 시) |

### 500 Internal Server Error vs 502 Bad Gateway vs 503 Service Unavailable
| 상태 코드 | 원인 |
|----------|------|
| **500** Internal Server Error | 서버 내부 코드 오류 발생 |
| **502** Bad Gateway | 서버가 백엔드 서버로부터 잘못된 응답 수신 |
| **503** Service Unavailable | 서버가 유지보수 중이거나 과부하 상태 |
