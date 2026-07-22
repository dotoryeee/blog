---
draft: false
date: 2026-07-21
authors:
  - dotoryeee
categories:
  - Linux
tags:
  - systemd
  - Boot
  - Logging
  - Cgroups
description: "systemd의 유닛 종류와 서비스 Type, 의존성, Restart 정책, cgroup 리소스 제어, 타이머, target 부팅, journald 구조를 표로 정리"
hide:
  - toc
---
# systemd 정리

<!-- more -->

## systemd란
systemd란 PID 1로 뜨는 init 겸, 서비스·소켓·타이머·마운트를 유닛(Unit)이라는 단일 모델로 선언적으로 감독하는 시스템·서비스 관리자

- 성격: 부팅 초기화부터 데몬 감독·로깅·리소스 제어까지 한 계층으로 통합
- 모델: 셸 스크립트 대신 `[Unit]` 형식의 선언적 유닛 파일로 상태를 기술
- 실행: 의존성 그래프를 계산해 독립 유닛을 병렬로 기동 → 부팅 시간 단축
- 추적: PID 파일이 아니라 cgroup으로 프로세스 그룹 전체를 소유·추적
- 관리 도구: 상태·제어는 `systemctl`, 로그는 `journalctl`로 단일화

### SysV init과의 차이

| 비교 항목 | SysV init | systemd |
|-----------|-----------|---------|
| PID 1 범위 | init 프로세스만 | init + 서비스·소켓·타이머·마운트 통합 |
| 기동 방식 | rc 셸 스크립트 순차 실행 | 선언적 유닛 + 의존성 기반 병렬 실행 |
| 부팅 상태 | runlevel 0~6 숫자 | 명명된 target 유닛 |
| 서비스 제어 | service·chkconfig | systemctl |
| 프로세스 추적 | PID 파일에 의존 | cgroup으로 그룹 단위 추적 |
| 로깅 | 외부 syslog 의존 | journald 내장 |
| 자동 복구 | 없음, 외부 도구 필요 | Restart·Watchdog 내장 |
| 온디맨드 기동 | 없음 | 소켓·경로·타이머 활성화 지원 |

---

## 유닛 종류 정리
유닛은 systemd가 관리하는 자원의 단위이며, 접미사가 종류를 결정함(총 11종)

| 유닛 | 용도 |
|------|------|
| .service | 데몬·프로세스 실행·감독 |
| .socket | 소켓 listen 후 트래픽 도달 시 서비스 온디맨드 기동 |
| .timer | 시각·경과 시간 기준으로 유닛 활성화(cron 대체) |
| .target | 유닛 묶음·동기화 지점(부팅 상태 표현) |
| .mount | 파일시스템 마운트 지점 관리 |
| .automount | 접근 시점에 마운트를 지연 트리거 |
| .path | 파일·디렉터리 변화 감시 후 유닛 활성화 |
| .slice | cgroup 계층 노드, 리소스 제어 그룹 |
| .swap | 스왑 장치·파일 관리 |
| .device | udev가 노출한 커널 장치 |
| .scope | systemd가 아닌 외부에서 생성된 프로세스 그룹 관리 |

---

## 서비스 유닛 구조
서비스 유닛은 `[Unit]`·`[Service]`·`[Install]` 세 섹션으로 구성됨

| 섹션 | 담는 내용 |
|------|-----------|
| [Unit] | 설명(Description)·의존성(After·Requires 등)·조건(Condition) |
| [Service] | 실행 명령(ExecStart)·Type·Restart·타임아웃·리소스 제어 |
| [Install] | enable 시 심링크 대상(WantedBy·RequiredBy) |

### Type 종류

Type은 systemd가 "기동 완료"를 판정하는 기준을 정함

| Type | 완료 판정 시점 |
|------|----------------|
| simple | 메인 프로세스 fork 직후(기본값), execve 이전 |
| exec | 메인 바이너리 execve 완료까지 대기 |
| forking | 부모가 fork 후 종료하면 완료, 전통 UNIX 데몬 방식 |
| oneshot | 메인 프로세스 종료 후 완료, active 유지엔 RemainAfterExit=yes |
| dbus | BusName에 지정한 D-Bus 이름 획득 시 완료 |
| notify | 서비스가 sd_notify()로 READY=1 전송 시 완료 |
| notify-reload | notify + reload 시 RELOADING=1·READY=1 처리 |
| idle | 다른 active 작업 완료까지 실행 지연, 콘솔 출력 정돈용 |

### 의존성 지시자

요구(requirement)와 순서(ordering)는 별개 축이며 각각 따로 지정해야 함

| 지시자 | 의미 |
|--------|------|
| Requires | 강한 요구, 함께 활성화. 요구 대상 실패 시(After 병행) 기동 중단 |
| Wants | 약한 요구, 함께 시도하되 실패해도 본 유닛엔 영향 없음 |
| Requisite | 요구 대상이 이미 떠 있지 않으면 즉시 실패, After와 병행 권장 |
| BindsTo | Requires + 대상이 예기치 않게 멈추면 본 유닛도 정지 |
| PartOf | 단방향 전파, 대상의 정지·재시작만 본 유닛에 반영 |
| Conflicts | 부정 의존, 한쪽 기동 시 상대 유닛 정지 |
| After / Before | 순서만 지정, 요구 여부와 무관 |

- 요구 지시자는 순서를 만들지 않음 → 순서가 필요하면 After·Before를 따로 지정
- 흔한 조합: Wants + After → "있으면 좋고, 있다면 그 뒤에 기동"

---

## 감독과 자동 복구
프로세스 종료를 감지해 정책에 따라 재기동하는 감독 기능이 [Service]에 내장됨

| Restart 값 | 재시작 조건 |
|------------|-------------|
| no | 재시작 안 함(기본값) |
| on-success | 정상 종료(exit 0·지정 시그널)에만 재시작 |
| on-failure | 비정상 exit·시그널·타임아웃·워치독 실패 시 재시작 |
| on-abnormal | 시그널·타임아웃·워치독 등 비정상 종료에만 재시작 |
| on-watchdog | 워치독 타임아웃 만료 시에만 재시작 |
| on-abort | clean 처리되지 않은 시그널로 중단 시 재시작 |
| always | 종료 원인과 무관하게 항상 재시작 |

- RestartSec: 재시작 전 대기 시간, 기본 100ms
- RestartSteps·RestartMaxDelaySec: 재시작 간격을 지수 백오프로 증가(예: 10s→20s→40s→상한)
- WatchdogSec: 서비스가 주기적으로 WATCHDOG=1을 보내야 하는 데드라인. 놓치면 failed 처리 후 SIGABRT
- StartLimitIntervalSec·StartLimitBurst: 지정 구간 안의 재시작 횟수 상한. 초과 시 재시작을 멈춰 크래시 루프 차단

---

## 리소스 제어
서비스마다 cgroup v2 노드가 매핑되어 메모리·CPU·I/O를 유닛 단위로 제한함

| 지시자 | 대응 cgroup 속성 | 효과 |
|--------|------------------|------|
| MemoryMax | memory.max | 절대 상한, 초과 시 cgroup 내부 OOM killer 발동 |
| MemoryHigh | memory.high | 스로틀 지점, 넘으면 프로세스가 강하게 감속 |
| MemoryMin | memory.min | reclaim 보호, 이 값까지는 회수 대상에서 후순위 |
| CPUQuota | cpu.max | % 값으로 CPU 시간 쿼터 지정 |
| CPUWeight | cpu.weight | 같은 slice 내 CPU 시간 비례 분배 |
| IOWeight | io.weight | 같은 slice 내 블록 I/O 대역 비례 분배 |
| TasksMax | pids.max | 생성 가능한 태스크(프로세스·스레드) 수 상한 |
| AllowedCPUs | cpuset.cpus | 실행 가능한 CPU 코어 집합 고정 |

### slice 계층

slice는 cgroup 트리의 중간 노드이며 리소스 제어가 계층으로 상속됨

```s
-.slice                 #루트 slice
├─ system.slice         #시스템 데몬(sshd 등)
├─ user.slice           #로그인 사용자
│  └─ user@1000.service #uid 1000 사용자 매니저
└─ machine.slice        #가상머신·컨테이너
```

- Max·High는 절대 한도, Weight는 형제 유닛 사이의 상대 비율
- 상위 slice에 건 제한이 하위 유닛 합계에 함께 적용됨

---

## 부팅과 target
target은 유닛 묶음이자 동기화 지점이며, SysV의 runlevel 숫자를 명명된 상태로 대체함

| target | 역할 | runlevel 별칭 |
|--------|------|---------------|
| sysinit.target | 초기 마운트·스왑 등 기본 초기화 | 없음 |
| basic.target | 소켓·타이머·경로까지 준비된 기본 동기화 지점 | 없음 |
| multi-user.target | 비그래픽 다중 사용자 환경 | runlevel3.target |
| graphical.target | GUI 로그인, multi-user.target을 포함 | runlevel5.target |
| rescue.target | 기본 서비스 + 마운트만 올린 복구 모드 | runlevel1.target |
| emergency.target | PID 1과 셸만 뜨는 최소 모드 | 없음 |
| poweroff.target / reboot.target | 종료·재부팅 상태 | runlevel0 / runlevel6 |

- default.target: 부팅 시 진입하는 목표, 보통 multi-user.target이나 graphical.target으로 심링크
- graphical.target은 multi-user.target을 pull in → 그래픽 상태는 다중 사용자 상태의 상위 집합
- 부팅은 target 도달에 필요한 유닛을 의존성 그래프로 계산해 독립분을 병렬 기동

---

## 타이머 vs cron
systemd timer는 유닛 활성화 방식의 스케줄러이며 cron 대비 의존성·로깅·복구가 강함

| 비교 항목 | cron | systemd timer |
|-----------|------|---------------|
| 정밀도 | 분 단위 | 초 단위 + AccuracySec로 조정 |
| 트리거 종류 | 벽시계(realtime)만 | OnCalendar(realtime) + OnBootSec·OnUnitActiveSec 등 monotonic |
| 유닛 의존성 | 없음 | After·Requires 등 유닛 의존성 지정 |
| 로깅 | mail·syslog 별도 | journald에 서비스 로그로 통합 |
| 놓친 작업 보정 | 없음(anacron 별도) | Persistent=true로 비활성 중 놓친 실행 catch up |
| 랜덤 분산 | 없음 | RandomizedDelaySec로 동시 실행 분산 |
| 리소스 제어 | 없음 | 대상 서비스에 cgroup·slice 그대로 적용 |

- 타이머 유닛은 실행을 직접 하지 않고, 동명 `.service`(또는 Unit= 지정 유닛)를 활성화
- monotonic 타이머는 이벤트 경과 기준(OnBootSec 등), realtime 타이머는 달력 표현(OnCalendar)
- AccuracySec 기본 1분 → wake-up을 묶어 전력 절약, 정밀 실행엔 값을 낮춤

---

## journald 정리
journald는 로그를 구조화된 인덱스 바이너리 저널로 수집·저장하는 systemd 로깅 데몬

- 수집원: 커널 메시지·syslog 호출·네이티브 API·서비스 stdout/stderr·audit
- 구조화: 레코드마다 필드가 붙어 필드 단위 필터링 가능(journalctl 검색이 빠른 이유)
- 신뢰 필드: `_PID`·`_UID`·`_SYSTEMD_UNIT`처럼 밑줄 접두 필드는 journald가 검증해 부여
- 사용자 필드: `MESSAGE`·`PRIORITY`처럼 접두 없는 필드는 애플리케이션이 제공

| 항목 | 설정·값 |
|------|---------|
| 저장 위치 | 휘발 `/run/log/journal`, 영속 `/var/log/journal` |
| Storage 옵션 | volatile · persistent · auto · none |
| rate limit | 기본 30초당 10000건 초과 시 드롭(RateLimitIntervalSec·RateLimitBurst) |
| 용량 관리 | SystemMaxUse 기본 파일시스템 10%(상한 4GB), SystemKeepFree 15%(상한 4GB) |
| 압축 | 512바이트 초과 객체 압축(Compress) |
| syslog 연동 | ForwardToSyslog로 rsyslog 등에 동시 전달 |

- rsyslog와의 저장 방식·원격 전송·메타데이터 차이는 별도 글([rsyslog, journald 비교](linux_logging.md))로 위임
- journald는 systemd의 한 유닛(systemd-journald.service)이라 부팅·감독·cgroup 모델을 그대로 공유

---

## 주요 명령 정리
상태·제어는 systemctl, 로그 조회는 journalctl로 나뉨

| 명령 | 용도 |
|------|------|
| `systemctl status <unit>` | 상태·최근 로그·cgroup 트리 확인 |
| `systemctl start/stop/restart <unit>` | 유닛 기동·정지·재기동 |
| `systemctl enable/disable <unit>` | 부팅 시 자동 기동 등록·해제 |
| `systemctl list-units --type=service` | 로드된 서비스 유닛 목록 |
| `systemctl list-dependencies <unit>` | 의존성 트리 출력 |
| `systemctl cat/edit <unit>` | 유닛 파일 열람·드롭인 오버라이드 |
| `systemctl get-default / set-default` | default.target 조회·변경 |
| `journalctl -u <unit>` | 특정 유닛 로그만 조회 |
| `journalctl -f` | 실시간 로그 추적(tail) |
| `journalctl -b` | 이번 부팅 이후 로그만 |
| `journalctl -p err` | 우선순위(err 이상)로 필터 |
| `systemd-analyze blame` | 유닛별 기동 소요 시간 정렬 |

---

## 결론
- systemd는 init·서비스 감독·타이머·마운트·로깅을 유닛이라는 한 모델로 묶은 관리자
- 서비스는 Type으로 기동 완료를, Restart·Watchdog으로 자동 복구를, cgroup·slice로 리소스를 통제
- 부팅은 target 도달을 위한 의존성 그래프 병렬 실행, 스케줄은 timer가 cron을 대체
- cron은 "시각이 되면 명령을 실행", systemd timer는 "시각이 되면 유닛을 활성화"로 이해하면 됌
