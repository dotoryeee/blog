---
draft: false
date: 2025-03-11
authors:
  - dotoryeee
categories:
  - Cloud
  - Server
---
# Swap 정리

<!-- more -->

## swap이란
운영체제에서 RAM(메모리)이 부족할 때 디스크 공간을 임시 메모리처럼 사용하는 기술

## Swap 공간의 종류
1. Swap Partition (스왑 파티션)
디스크의 특정 영역을 스왑 전용으로 설정
시스템이 부팅될 때 자동으로 마운트됨
일반적으로 리눅스 설치 시 기본적으로 설정됨
2. Swap File (스왑 파일)
기존 파티션을 변경하지 않고, 파일 시스템 내부에 스왑 파일을 생성하여 사용
동적으로 크기를 조정할 수 있어 유연함
SSD를 사용할 경우, 수명 단축을 방지하기 위해 가급적 피하는 것이 좋음

|항목|Swap Partition|Swap File|
|----|------------------------|--------------------|
|개념|디스크의 특정 파티션을 Swap으로 설정|기존 파일 시스템 내에서 일반 파일을 Swap으로 사용|
|설정 방식|리눅스 설치 시 또는 fdisk로 직접 생성|fallocate 또는 dd 명령어로 파일 생성|
|속도|더 빠름 (디스크의 연속된 공간을 사용)|상대적으로 느림 (파일 시스템을 통해 접근)|
|유연성|크기 변경이 어려움 (재파티셔닝 필요)|크기 조정이 용이 (fallocate 사용)|
|설치 난이도|초기 설정이 필요함 (파티션 생성 & 포맷 필요)|간단 (swapfile 생성 후 swapon 실행)|
|파일 시스템 영향|파일 시스템과 독립적 (파티션 레벨)|파일 시스템의 영향을 받음 (파일 조각화 가능)|
|디스크 사용 방식|연속된 블록을 사용하여 성능 최적화|파일 시스템 내부에서 일반 파일로 할당|
|보안|Swap 파티션 전체를 암호화하려면 별도 설정 필요|파일 기반 암호화 가능 (chattr +C, chmod 600)|
|권장 환경|서버, 성능이 중요한 시스템|데스크탑, 가상머신, 유동적인 환경|

## swap 상태 확인
```sh
free -h # 명령 시 아래와 같이 swap usage 확인 가능

              total        used        free      shared  buff/cache   available
Mem:           8.0G        5.6G        1.2G        0.5G        1.2G        2.1G
Swap:          2.0G        1.0G        1.0G
```

## Swapfile 생성방법
```sh
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048  # 1MB 블록 2048개 작성하여 2GB 파일 생성
sudo chmod 600 /swapfile #스왑 파일의 보안을 위해 다른 사용자 접근을 차단
sudo mkswap /swapfile
sudo swapon /swapfile #일회성 swap 마운트 명령어
sudo swapoff -v /swapfile #swap ummount
# 시스템 재시작 후에도 swap 사용하려면 fstab에 아래 내용 추가
/swapfile none swap sw 0 0
sudo mount -a
```

## swap 용량
1. Database 서버 (MySQL, PostgreSQL 등)<br>
DB 서버는 보통 RAM을 적극적으로 캐싱에 사용하지만, RAM이 부족한 경우 Swap이 부족하면 DB가 강제 종료될 수 있음<br>
vm.swappiness=10 정도로 설정하여 Swap을 최대한 적게 사용하도록 조정
2. 웹 서버 (Nginx, Apache, Node.js 등)<br>
웹 서버는 대부분 RAM을 많이 쓰지 않으므로 Swap을 2GB~4GB 설정<br>
3. 가상 머신 (VM) & 컨테이너 서버 (Docker, K8s)<br>
Swap은 가상 머신이나 컨테이너 환경에서 성능 저하를 일으킬 수 있음<br>
RAM이 충분하면 Swap을 비활성화 (swapoff -a)<br>
RAM이 부족하면 최소한의 Swap(2GB~4GB)만 설정
4. RAM이 매우 작은경우(4GB 이하 등)에는 OOM 방지를 위해 충분한 swap 용량을 확보해줄것
5. 데이터 분석, 머신러닝, 영상 렌더링 등에서 RAM을 초과하는 연산을 수행할 경우 Swap이 부족하면 프로그램이 강제 종료될 수 있으므로 RAM의 1.5배~2배 용량 확보


## swap 파라미터
### Swappiness
- 기본 값: 60 (값이 클수록 적극적으로 스왑 사용)
- 낮은 값(예: 10~20)으로 설정하면, RAM을 최대한 사용하고 스왑을 적게 사용하도록 조정 가능
- swappiness = 0<br>
RAM을 최대한 활용하고, 거의 스왑을 사용하지 않음<br>
메모리가 거의 가득 차야 스왑을 사용
- swappiness = 100<br>
메모리가 남아 있어도 적극적으로 스왑을 사용<br>
RAM이 빠르게 확보되지만, 디스크 I/O가 증가하여 성능 저하 가능성
- 데스크톱은 일반적으로 swappiness=10~20 사용
- 서버는 안정성이 중요하기 때문에 기본값인 swappiness=60을 유지
- DB 서버나 캐시 서버의 경우, RAM을 우선적으로 사용하고 스왑을 최소화 (swappiness=10~30)

```sh
cat /proc/sys/vm/swappiness #현재 swappiness 값 확인
sudo sysctl vm.swappiness=10 # 10으로 변경 (일회성)
# 시스템 재시작 후에도 10을 유지하려면 /etc/sysctl.conf 에 아래 내용 추가
vm.swappiness=10
```

## 컨테이너 환경에서 swap을 최소화해야하는 이유
1. Kubernetes는 컨테이너의 메모리 리소스를 엄격하게 제한하기 위해 기본적으로 Swap을 비활성화해야 한다고 권장함.
2. 컨테이너는 프로세스 격리 기술을 사용하므로, Swap이 많으면 리소스 예측이 어려움
3. Swap이 많으면 OOM Killer가 즉시 실행되지 않고, Swap을 먼저 사용하여 프로세스를 유지하려고 하는데 이로 인해 프로세스가 Swap을 과도하게 사용하다가 결국 시스템 전체가 느려질 수 있음 -> 컨테이너 환경에서는 OOM Killer을 이용해 죽였다 다시 살리는게 나을 수 있다