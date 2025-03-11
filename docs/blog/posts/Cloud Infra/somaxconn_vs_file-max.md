---
draft: false
date: 2025-03-11
authors:
  - dotoryeee
categories:
  - Cloud
  - Server
---
# net.core.somaxconn vs fs.file-max 파라미터

<!-- more -->

## 위 파라미터가 왜 중요할까
!!! tip
    리눅스에서는 "모든 것은 파일이다" 라는 철학을 따르기 때문에, 파일, 소켓, 파이프, 디바이스 등도 파일 디스크립터(File Descriptor, FD)를 사용

**HTTP/1.1을 이용해 6개의 TCP 세션을 열면, 리눅스에서는 6개의 파일 디스크립터(FD)가 생성**


### TCP 소켓이 파일로 취급되는 이유
- 리눅스에서 파일 디스크립터(FD)란?<br>
파일 디스크립터는 리눅스 커널에서 파일, 소켓, 파이프, 디바이스 등 다양한 리소스를 핸들링하는 식별자<br>
프로세스가 무언가를 읽거나 쓸 때, FD를 통해 접근
- TCP 소켓도 FD를 사용<br>
네트워크 소켓(TCP/UDP)은 socket() 시스템 호출을 통해 생성되며, 내부적으로 파일 디스크립터를 할당받음<br>
즉, 소켓이 생성될 때 파일처럼 다뤄지며 FD가 할당됨<br>
소켓 FD는 일반 파일처럼 read(), write(), close() 등의 시스템 호출을 사용할 수 있음


## `net.core.somaxconn`란?
네트워크 서버가 클라이언트 연결을 받을 때, 큐(대기열)의 크기를 결정하는 파라미터.

### 개념
- 서버가 동시에 받을 수 있는 연결 요청 개수(대기 큐 크기)를 조절.
- 리눅스 시스템에서는 `listen()` 시스템 호출을 사용하여 대기 큐를 설정하는데, 이때 최대 큐 크기가 `net.core.somaxconn` 값에 의해 제한됨.

### 현재 설정 확인
```bash
sysctl net.core.somaxconn
```

### 변경 방법
```bash
sudo sysctl -w net.core.somaxconn=1024
```

`/etc/sysctl.conf`에 영구 적용:
```bash
echo 'net.core.somaxconn=1024' | sudo tee -a /etc/sysctl.conf
```

---

## `fs.file-max`란?
리눅스 시스템이 동시에 열 수 있는 최대 파일 개수(파일 디스크립터 개수)를 제한하는 파라미터.

### 개념
- 서버에서 실행되는 모든 프로세스는 파일 디스크립터(File Descriptor, FD) 를 사용함.
- 파일뿐만 아니라 소켓(socket), 파이프(pipe), 장치(device) 등도 파일 디스크립터를 사용.
- `fs.file-max`는 시스템 전체에서 열 수 있는 최대 FD 개수를 제한하는 역할을 함.
- 기본값은 보통 2097152 (2M, 시스템에 따라 다름).

### 현재 설정 확인
```bash
sysctl fs.file-max
```

### 변경 방법
```bash
sudo sysctl -w fs.file-max=2097152
```

`/etc/sysctl.conf`에 영구 적용:
```bash
echo 'fs.file-max=2097152' | sudo tee -a /etc/sysctl.conf
```

---

## `net.core.somaxconn`, `fs.file-max` 차이점

| 항목 | net.core.somaxconn | fs.file-max |
|------|----------------------|-----------------|
| 역할 | 서버가 수신할 수 있는 연결 대기 큐 크기 설정 | 시스템 전체에서 열 수 있는 최대 파일 디스크립터 개수 제한 |
| 대상 | 네트워크 요청(TCP/UDP 소켓) | 파일, 소켓, 파이프 등 모든 FD |
| 기본값 | 128 | 2097152 |
| 최적화 목적 | 동시 접속 요청이 많은 웹서버(Nginx, Apache, Redis 등)의 성능 향상 | 다중 프로세스를 실행하는 서버의 파일 핸들 제한 해제 |
| 설정 위치 | `sysctl net.core.somaxconn` | `sysctl fs.file-max` |
| 변경 효과 | - `listen()` 호출에서 허용하는 대기 큐 크기 증가<br>- 동시 연결 요청을 더 많이 수용 가능 | - 서버에서 열 수 있는 파일 개수 증가<br>- 많은 소켓, 로그 파일을 사용하는 애플리케이션 최적화 |
| 적용 사례 | 웹 서버, DB 서버, 메시지 큐 서버 | DB 서버, 로그 분석 서버, 대량 파일 처리 서버 |

---

## 사용 예시
### `net.core.somaxconn`을 조정해야 하는 경우

- 웹 서버(Nginx, Apache, Tomcat 등)에서 많은 동시 접속을 처리해야 할 때
- DB 서버(MySQL, PostgreSQL, Redis, MongoDB)에서 많은 클라이언트 요청을 받을 때
- `dmesg` 로그에서 "TCP: drop request" 또는 "listen queue overflow" 오류가 발생할 때

### `fs.file-max`를 조정해야 하는 경우

- DB 서버에서 많은 커넥션을 처리해야 할 때
- 로그 서버(ELK, Prometheus 등)에서 대량의 파일을 다룰 때
- Node.js 같은 이벤트 기반 서버에서 많은 소켓 핸들을 유지해야 할 때
- `ulimit -n` 명령어를 실행했을 때 파일 핸들 제한이 너무 낮은 경우

---

## 최적화 예시
```bash
# TCP 연결 대기 큐 크기 증가
sudo sysctl -w net.core.somaxconn=1024

# 시스템 전체에서 열 수 있는 파일 개수 증가
sudo sysctl -w fs.file-max=2097152
```

부팅 후에도 유지하려면 `/etc/sysctl.conf`에 추가
```bash
echo 'net.core.somaxconn=1024' | sudo tee -a /etc/sysctl.conf
echo 'fs.file-max=2097152' | sudo tee -a /etc/sysctl.conf
```

## fs.file-max와 ulimit -n(open files)의 차이점
|항목|fs.file-max|ulimit -n (open files)|
|----|----------------|----------------|
|역할|시스템 전체에서 열 수 있는 파일 개수 제한|각 프로세스가 열 수 있는 파일 개수 제한|
|적용 범위|커널 전역 설정 (시스템 전체)|각 사용자 또는 특정 프로세스에 적용|
|확인 방법|sysctl fs.file-max|ulimit -n 또는 ulimit -a|
|설정 방법|sysctl -w fs.file-max=값|ulimit -n 값 또는 /etc/security/limits.conf|
|기본값 예시 (Ubuntu 22.04)|9223372036854775807 (이론적 최대)|1024 (Soft Limit) / 1048576 (Hard Limit)|

!!! tip
    file-max와 ulimit open files 파라미터 모두 값이 부족할 때 Too many open files 에러 발생하는 점은 동일

## 시스템 기본값
### net.core.somaxconn 기본값

|운영체제|기본값|
|---------|----|
|CentOS 7|128|
|Amazon Linux 2|128|
|Amazon Linux 2023|4096|
|Ubuntu 20.04|128|
|Ubuntu 22.04|4096|
|RHEL 8|128|
|RHEL 9|4096|

### fs.file-max 기본값

|운영체제|기본값|
|---------|----|
|CentOS 7|798004|
|Amazon Linux 2|524288|
|Amazon Linux 2023|9223372036854775807|
|Ubuntu 20.04|9223372036854775807|
|Ubuntu 22.04|9223372036854775807|
|RHEL 8|524288|
|RHEL 9|9223372036854775807|
