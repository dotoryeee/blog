---
draft: false
date: 2026-07-20
authors:
  - dotoryeee
categories:
  - Linux
tags:
  - eBPF
  - Cilium
  - Falco
  - Kubernetes
description: "eBPF의 verifier·JIT·maps·CO-RE 구조와 커널 모듈과의 차이, 훅 위치·개발 스택·Cilium·Falco 같은 대표 제품까지 정리"
hide:
  - toc
---
# eBPF 정리

<!-- more -->

## eBPF란
eBPF(extended Berkeley Packet Filter)란 커널 소스 수정이나 모듈 적재 없이, 검증(Verification)을 통과한 프로그램을 커널 이벤트 지점에 안전하게 로드해 실행하는 기술

- 성격: 커널 재컴파일·재부팅 없이 관측·네트워킹·보안 로직을 실행 중에 주입하는 커널 확장 계층
- 안전성: verifier가 로드 전 정적 검증 → 무한 루프·메모리 위반 프로그램은 로드 거부
- 실행: 검증 통과 후 JIT로 네이티브 기계어 변환 → 네이티브에 근접한 속도
- 데이터 교환: 커널 상주 key-value 저장소인 maps로 유저스페이스와 상태 공유
- 위치: 프로그램 타입(program type)이 attach 가능한 훅·헬퍼(helper)·맵 접근 범위를 결정

### 로드 파이프라인

```mermaid
graph LR
    Src["프로그램 작성<br>(C/Rust)"] --> BC["eBPF 바이트코드"]
    BC --> Ver["Verifier<br>정적 검증"]
    Ver --> JIT["JIT 컴파일<br>(네이티브 기계어)"]
    JIT --> Hook["훅 attach<br>(kprobe/XDP/tc/LSM)"]
    Hook --> Map["Maps<br>유저스페이스 데이터 교환"]
```

- 작성: C나 Rust로 작성한 소스를 clang/LLVM이 eBPF 바이트코드로 컴파일
- 검증: verifier가 제어 흐름·메모리·헬퍼 호출·종료 보장을 정적 분석 → 안전하지 않으면 거부
- 컴파일: 검증 통과분만 JIT가 호스트 ISA 기계어로 변환(미지원 아키텍처는 인터프리터 실행)
- attach: kprobe·XDP·tc·LSM 등 program type이 지정한 훅에 프로그램 연결
- 교환: 실행 결과를 maps에 적재 → 유저스페이스 로더가 읽어 집계·표시

### 핵심 구성요소

| 구성요소 | 역할 |
|----------|------|
| Verifier | 로드 전 안전성 정적 검증, 위반 시 거부 |
| JIT 컴파일러 | 검증된 바이트코드를 네이티브 기계어로 변환 |
| Maps | 커널·유저스페이스·프로그램 간 상태 공유 저장소 |
| Helper 함수 | 커널이 노출한 제한된 API(맵 접근·시각·리다이렉트 등) |
| program type | attach 가능한 훅과 접근 가능한 헬퍼·컨텍스트 결정 |

---

## 커널 모듈과의 차이
커널 모듈은 커널에 임의 코드를 직접 삽입하는 반면, eBPF는 verifier 검증을 거친 제한된 코드만 주입하는 것이 핵심 차이

| 비교 항목 | 커널 모듈(Kernel Module) | eBPF |
|-----------|--------------------------|------|
| 크래시 영향 | 버그 시 커널 패닉·전체 다운 | verifier가 사전 차단, 실패해도 로드 거부에 그침 |
| 안전 검증 | 없음, 개발자 책임 | 로드 전 정적 verifier 통과 필수 |
| 적재 방식 | insmod로 커널에 직접 삽입 | sys_bpf()로 검증 후 주입, 재부팅 불필요 |
| 이식성 | 커널 버전·빌드마다 재컴파일 | CO-RE로 단일 바이너리가 여러 커널 대응 |
| 실행 범위 | 커널 전역의 임의 코드 실행 | 허용된 헬퍼·훅·맵으로 범위 제한 |
| 권한 | CAP_SYS_MODULE, 사실상 전권 | CAP_BPF + 용도별 최소 권한 |

---

## 훅 위치 정리
program type별로 attach 지점이 정해지며, 크게 관측·네트워킹·보안 계층으로 갈림

| 훅 | 계층 | 용도 |
|----|------|------|
| kprobe/kretprobe | 커널 함수 진입·반환 | 임의 커널 함수 동적 추적(관측) |
| fentry/fexit | 커널 함수(BTF 기반) | kprobe보다 낮은 오버헤드의 진입·반환 추적(관측) |
| uprobe/uretprobe | 유저 함수 | 유저스페이스 애플리케이션 함수 추적(관측) |
| tracepoint | 커널 정적 지점 | 커널이 노출한 안정적 이벤트 추적(관측) |
| perf event | PMU·샘플링 | CPU 프로파일링·주기적 샘플링(관측) |
| XDP | NIC 드라이버 RX 경로 | 스택 진입 전 패킷 처리(네트워킹) |
| tc(clsact) | 커널 네트워크 스택 | ingress·egress 패킷 분류·정형(네트워킹) |
| BPF LSM | LSM 보안 훅 | 커널 보안 지점에 정책 부착·차단(보안) |

- seccomp는 eBPF가 아닌 classic BPF(cBPF) 필터를 사용 → eBPF의 보안 경로는 BPF LSM이 중심

### XDP가 빠른 이유

- 위치: NIC 드라이버 RX 경로에서 sk_buff 할당 이전에 실행 → 커널 스택 진입 전에 처리
- 생략: netfilter·conntrack·소켓 계층 등 스택 처리를 건너뜀
- 액션: XDP_PASS/DROP/TX/REDIRECT로 즉시 판정 → DDoS 드롭·L4 포워딩에 유리
- 모드: Native(드라이버 지원 필요, 최속)와 Generic(skb 기반, 범용이나 느림)으로 갈림

---

## verifier 동작
verifier는 로드 시점에 프로그램을 심볼릭 실행하며 안전성을 정적으로 증명하는 커널 검사기

- 종료 보장: 제어 흐름 그래프에 순환이 없어야 함, 유계 루프만 허용 → 무한 루프 거부
- 메모리 안전: 레지스터·스택·맵 접근 범위를 추적해 경계 밖 접근 차단
- 타입 안전: 포인터와 스칼라 타입을 구분해 잘못된 역참조 거부
- 헬퍼 검사: program type이 허용한 헬퍼만 호출 가능, 인자 타입도 검증
- 상태 가지치기: 이미 지난 동일 상태에 도달하면 탐색을 잘라 검증 비용 관리
- 실패 시: 로드 자체가 거부되어 실행 중 커널에는 아무 영향 없음

---

## maps 정리
maps는 eBPF 프로그램이 상태를 저장하고 유저스페이스와 데이터를 주고받는 커널 상주 저장소

| 맵 종류 | 설명 |
|---------|------|
| Array | 정수 인덱스 기반 고정 크기 배열 |
| Hash | 임의 key-value 해시 테이블 |
| LRU Hash | 용량 초과 시 오래된 항목부터 제거 |
| Per-CPU | CPU별 사본 유지로 락 경합 회피 |
| Ring Buffer | 커널에서 유저스페이스로 이벤트 스트리밍 |
| Prog Array | tail call 대상 프로그램 참조 배열 |

- 공유 범위: 프로그램 간·호출 간·유저스페이스와 상태 공유
- 접근: 유저스페이스는 파일 디스크립터(fd)로, 커널 프로그램은 헬퍼로 read/write

---

## 개발 스택 비교
관측 원라이너부터 이식성 있는 프로덕션 바이너리까지 도구별 적합 영역이 다름

| 도구 | 형태 | 언어 | 적합 |
|------|------|------|------|
| bcc | 트레이싱 툴킷 + 바인딩 | Python·Lua, 커널부 C | 런타임 컴파일 기반 커널 관측 도구 다수, 대상 노드에 커널 헤더·LLVM 필요 |
| bpftrace | 고수준 트레이싱 DSL | awk 유사 스크립트 | 일회성 커널·유저 관측을 짧은 스크립트로 수행 |
| libbpf | C 라이브러리(업스트림 커널) | C/C++ | CO-RE·BPF skeleton 지원, 단일 바이너리 배포 |
| cilium/ebpf | 순수 Go 라이브러리 | Go | libbpf 비의존, Go 앱에 eBPF 내장. Cilium·Tetragon 등이 사용 |
| aya | Rust 라이브러리 | Rust(유저·커널 모두) | libbpf 비의존, CO-RE 지원. 유저·커널 코드를 한 언어로 작성 |

- bcc는 대상 노드에서 커널 헤더로 런타임 컴파일 → libbpf CO-RE는 한 번 컴파일해 여러 커널에서 재사용
- 프로덕션 배포는 libbpf(C)·cilium/ebpf(Go)·aya(Rust) 중 앱 언어에 맞춰 선택

### 선택 가이드

| 상황 | 추천 | 사유 |
|------|------|------|
| 즉석 커널 관측 | bpftrace | 짧은 스크립트로 원라이너 추적 |
| 이식성 있는 C 배포 | libbpf | CO-RE·skeleton으로 단일 바이너리 |
| Go 앱에 내장 | cilium/ebpf | 순수 Go, 외부 의존 최소 |
| Rust 단일 언어 | aya | 유저·커널 코드를 Rust로 통일 |

---

## eBPF 기반 제품
관측·네트워킹·보안 각 영역에서 eBPF를 코어로 쓰는 대표 제품과 라이선스 정리

| 제품 | 영역 | 설명 |
|------|------|------|
| Cilium | 네트워킹·CNI | eBPF 기반 CNI, kube-proxy 대체 라우팅. Apache 2.0(CNCF) |
| Hubble | 관측 | Cilium 위에 얹는 네트워크 흐름·서비스 의존성 관측. Apache 2.0 |
| Falco | 런타임 보안 | 커널 이벤트 기반 이상 행위 탐지·알림. Apache 2.0(CNCF) |
| Tetragon | 보안 정책 | 프로세스·시스템콜 관측 + 실시간 런타임 시행(enforcement). Apache 2.0 |
| Pixie | 관측(APM) | 코드 수정 없이 자동 계측으로 애플리케이션 텔레메트리 수집. Apache 2.0(CNCF) |
| Katran | L4 로드밸런서 | XDP 기반 고성능 L4 LB 포워딩 플레인(C++ + eBPF). GPL-2.0(Meta) |

---

## 사용 사례
동일한 로드·검증·attach 구조가 관측·네트워킹·보안 세 영역에 그대로 재사용됨

### 관측(Observability)
- 시스템콜·커널 함수·네트워크 이벤트를 애플리케이션 코드 수정 없이 추적
- 커널·유저 양쪽 함수에 훅 가능 → 재배포 없이 관측 지점 추가
- 커널 안에서 집계 후 요약만 유저스페이스로 전달 → 데이터 복사·오버헤드 절감
- 사례: bpftrace 원라이너, Pixie 자동 계측, Hubble 서비스 흐름 관측

### 네트워킹(Networking)
- XDP·tc로 패킷을 스택 앞단에서 파싱·필터·리다이렉트
- kube-proxy의 iptables 규칙 대신 eBPF 맵 기반 로드밸런싱으로 대체
- 서비스 수 증가에도 룩업이 선형 규칙 스캔이 아닌 맵 조회라 확장에 유리
- 사례: Cilium CNI, Katran L4 로드밸런서, XDP 기반 DDoS 드롭

### 보안(Security)
- BPF LSM으로 커널 보안 훅에 정책을 부착하고 위반 시 차단
- 프로세스 실행·파일 접근·네트워크 연결을 실시간 관측·시행
- 커널 이벤트를 직접 보므로 유저스페이스 우회·후킹 회피에 강함
- 사례: Falco 이상 탐지, Tetragon 런타임 정책 시행

---

## 한계와 운영 주의
- verifier 제약: 무한 루프 금지, 유계 루프(bounded loop)만 허용. 명령어·분기 탐색량 상한 → 복잡 로직은 함수 분할·tail call로 우회
- 커널 버전 의존: program type·헬퍼·훅이 커널 버전별로 다름. BPF LSM은 5.7+, CAP_BPF는 5.8+ 등 최소 버전 존재
- CO-RE 전제: 이식성은 대상 커널의 BTF(BPF Type Format) 정보에 의존 → BTF 미제공 커널은 bcc식 헤더 기반 재빌드 필요
- 권한: 로드에 CAP_BPF, 네트워킹은 +CAP_NET_ADMIN, 트레이싱은 +CAP_PERFMON 필요. 과거엔 CAP_SYS_ADMIN 단일 요구, 6.9의 BPF token으로 위임 가능
- 오버헤드: 훅이 패킷·시스템콜 같은 핫패스에 직렬로 붙으면 지연 가산 → 관측 대상 빈도에 비례
- 디버깅: verifier 실패 메시지 해석 난이도↑, 커널 컨텍스트라 일반 디버거 사용 제약 → bpftool·verifier 로그에 의존

---

## 결론
- eBPF는 커널을 재컴파일·재부팅하지 않고 검증된 프로그램을 이벤트 지점에 안전하게 주입하는 실행 계층
- verifier(안전)·JIT(속도)·maps(데이터 교환)·CO-RE(이식성)가 커널 모듈 대비 우위의 네 축
- 관측은 bcc·bpftrace·Pixie, 네트워킹은 Cilium·Katran, 보안은 Falco·Tetragon으로 영역이 갈림
- 커널 모듈은 "커널에 직접 심는 코드", eBPF는 "커널이 검증하고 돌려주는 코드"로 이해하면 됌
