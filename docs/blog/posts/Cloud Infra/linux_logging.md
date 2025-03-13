---
draft: false
date: 2025-03-13
authors:
  - dotoryeee
categories:
  - Server
---
# rsyslog, journald 비교

<!-- more -->

## 비교표

| 구분 | rsyslog | journald |
|------|--------|---------|
| 설명 | 기존 리눅스 시스템에서 사용되던 로깅 시스템 | `systemd`의 일부로 동작하는 로깅 시스템 |
| 로그 저장 방식 | 일반 텍스트 파일 (`/var/log/messages` 등) | 바이너리 형식 (`/var/log/journal/`) |
| 로그 확인 방법 | `cat`, `tail`, `grep` 등 | `journalctl` 명령어 사용 |
| 설정 파일 | `/etc/rsyslog.conf` | `/etc/systemd/journald.conf` |
| 검색 및 필터링 | 파일 기반 검색 | `journalctl`로 상세한 필터링 가능 |
| 로그 보존 방식 | 로그 파일 크기 제한 및 롤링 | 압축 및 저장 공간 자동 관리 가능 |
| 네트워크 전송 지원 | TCP, UDP 지원 (원격 서버 전송 가능) | 기본 미지원 (`journal-remote` 필요) |
| 보안 및 접근 제어 | root 및 특정 그룹만 접근 가능 | `journald` 자체 보안 기능 활용 |
| 성능 | 파일 I/O 기반, 빠르지만 로깅이 많으면 부하 증가 | 바이너리 저장 방식으로 빠른 검색 가능 |
| 메타데이터 포함 | 기본 텍스트만 저장 | 실행한 사용자, 프로세스 정보 등 추가 메타데이터 포함 |
| 장점 | 텍스트 기반으로 직관적이며 기존 시스템과 호환성이 높음, 원격 전송 지원 | 고급 메타데이터 저장 가능, 빠른 검색 및 필터링, 로그 압축 가능 |
| 단점 | 파일 I/O 부담이 크고 검색이 비효율적일 수 있음 | 바이너리 저장 방식으로 직접 읽기 어려움, 기본적으로 네트워크 전송 미지원 |


## journald CLI 예시
1. 기본 로깅 위치 `/var/log/journal/`가 아닌 다른 위치의 로그 읽기
```sh
sudo journalctl --directory=/mnt/recovery/var/log/journal/ --no-pager
```
2. 특정 시점 로그 읽기
```sh
sudo journalctl --since "2024-03-10 00:00:00" --until "2024-03-11 23:59:59"
```
3. sshd 서비스 로그만 읽기
```sh
sudo journalctl -u sshd
```
4. json으로 출력하기
```sh
sudo journalctl -o json-pretty
```
