---
draft: false
date: 2025-03-19
authors:
  - dotoryeee
categories:
  - Cloud
  - Server
hide:
  - toc
---
# DDoS 유형별 대응 방법 요약

<!-- more -->

## 비교표
| DDoS 공격 유형 | OSI 계층 | 방어 방법 | 방어 효과 | OWASP 순위 | 상세 설명 |
|--------------|---------|---------|---------|------------|---------|
| HTTP Flooding | 7 | Nginx: Rate Limiting | 높음 | OWASP 2020 Top 10 | limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s; 설정으로 IP당 요청 수를 제한하여 초당 수백만 건에 달하는 HTTP 요청을 효과적으로 차단. 2024년 1분기 93% 증가한 HTTP DDoS 공격에 대응 가능 |
| Application Layer Attacks | 7 | Nginx: WAF 모듈 활용 | 높음 | OWASP 2020 Top 3 | Nginx ModSecurity 모듈 설치로 SQL Injection, XSS 등 다양한 공격 패턴을 실시간 탐지하고 차단. 시그니처 기반 및 행동 기반 탐지 모두 지원 |
| Slowloris | 7 | Nginx: 연결 제한 및 타임아웃 설정 | 높음 | OWASP 2017 Top 6 | limit_conn_zone $binary_remote_addr zone=addr:10m; limit_conn addr 10; client_body_timeout 60; client_header_timeout 60; 설정으로 단일 IP 연결 제한 및 느린 연결 차단. 이벤트 기반 아키텍처로 Apache보다 효과적 방어 |
| DNS Amplification | 7 | Nginx: DNS 쿼리 제한 | 중간 | OWASP 2020 Top 5 | Nginx 설정에서 DNS 요청 속도 제한 및 캐싱 설정으로 2023년 80% 증가한 DNS 증폭 공격에 대응. 단, 대규모 공격에는 추가 대응책 필요 |
| SYN Flooding | 4 | OS 레벨: TCP SYN 쿠키 활성화 | 높음 | OWASP 2017 Top 4 | net.ipv4.tcp_syncookies=1 설정으로 SYN 백로그 큐 소진 방지. 2022년 넷스카우트 조사에서 2위로 많은 공격 유형인 TCP SYN 공격에 95% 이상의 방어 효과 |
| TCP Connection Flooding | 4 | Nginx: keepalive 최적화 | 중간 | OWASP 2017 Top 7 | keepalive_timeout 15; keepalive_requests 100; 설정으로 연결 유지 시간 감소. 2022년 넷스카우트 조사에서 1위 공격인 TCP ACK 공격에 약 70%의 방어 효과 |
| NTP Amplification | 7 | OS 레벨: UDP 123 포트 제한 | 높음 | OWASP 2020 Top 8 | iptables로 UDP 123 포트 제한하여 NTP 증폭 공격 차단. 최대 100배까지 증폭되는 NTP 공격에 90% 이상의 방어 효과 |
| UDP Flooding | 3 | OS 레벨: iptables 필터링 | 높음 | OWASP 2017 Top 8 | iptables -A INPUT -p udp --dport 포트번호 -m limit --limit 50/second -j ACCEPT 설정으로 UDP 트래픽 속도 제한. 2024년 증가하는 UDP 기반 공격에 85% 이상의 방어 효과 |
| UDP Deflection | 3 | OS 레벨: 불필요 UDP 포트 차단 | 높음 | OWASP 2020 Top 9 | iptables -A INPUT -p udp --dport 포트번호 -j DROP으로 사용하지 않는 포트 차단. 2024년 826% 증가한 젠킨스 기반 UDP 멀티캐스트 공격에 효과적 |
| ICMP Flooding | 3 | OS 레벨: ICMP 제한 | 높음 | OWASP 2017 Top 9 | iptables -A INPUT -p icmp -m limit --limit 1/s --limit-burst 4 -j ACCEPT 설정으로 ICMP 패킷 속도 제한. 초당 1개 패킷으로 제한하여 95% 이상의 방어 효과 |
| HTTP/2 Continuation | 7 | Nginx: HTTP/2 설정 최적화 | 높음 | OWASP 2023 Top 4 | http2_max_field_size 4k; http2_max_header_size 16k; 설정으로 HTTP/2 프로토콜 취약점 대응. 2023년 발견된 HTTP/2 래피드 리셋 취약점으로 인한 초당 수백만 건의 요청 공격에 효과적 |
