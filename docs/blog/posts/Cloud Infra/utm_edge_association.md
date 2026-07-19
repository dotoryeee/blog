---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - AWS
  - Network
  - Security
---

# Edge Association 기반 UTM 구성 정리

<!-- more -->

## Edge Association이란

Edge Association이란 라우트 테이블을 서브넷이 아닌 IGW에 연결하여, VPC로 들어오는 인바운드 트래픽을 VPC 내부의 보안 어플라이언스로 우회시키는 기능(VPC Ingress Routing)

- 일반 라우트 테이블: 서브넷에서 나가는 트래픽의 경로 제어
- Gateway 라우트 테이블(edge association): IGW를 통과해 들어오는 트래픽의 경로 제어
- Palo Alto VM-Series, FortiGate-VM 같은 UTM(Unified Threat Management) 어플라이언스를 인터넷과 워크로드 사이에 인라인 배치할 때 사용

---

## 구성 방식 비교

|비교 항목|ENI 직접 지정|GWLB(Gateway Load Balancer)|
|---|---|---|
|edge 라우트 target|UTM 인스턴스의 ENI|GWLB Endpoint(GWLBe)|
|어플라이언스 수량|단일 인스턴스 (HA는 자체 구성)|GWLB 뒤에 다수 배치, 자동 분산|
|고가용성|Active/Passive + 장애 시 라우트 교체 필요|GWLB가 헬스체크·페일오버 처리|
|캡슐화|없음 (라우팅만 변경)|GENEVE(UDP 6081)로 어플라이언스에 전달|
|ENI 설정|Source/Dest Check 비활성화 필수|GWLBe만 있으면 됨|
|확장성|수직 확장 위주|수평 확장 (Auto Scaling 연동 가능)|
|권장 규모|소규모/PoC|운영 환경 표준|

---

## 트래픽 흐름 (GWLB 방식)

``` mermaid
graph LR
    Internet((Internet)) --> IGW[IGW]
    IGW -->|"edge association RT<br>dest: 워크로드 서브넷 → GWLBe"| GWLBe[GWLB Endpoint]
    GWLBe --> GWLB[GWLB]
    GWLB -->|"GENEVE(6081)"| UTM["UTM 어플라이언스<br>(VM-Series / FortiGate-VM)"]
    UTM --> GWLB
    GWLB --> GWLBe
    GWLBe --> Workload[워크로드 EC2]
```

- 인바운드: IGW → edge 라우트 테이블이 GWLBe로 우회 → UTM 검사 → 워크로드 도달
- 아웃바운드(리턴): 워크로드 서브넷 라우트 테이블에서 0.0.0.0/0 → GWLBe → 검사 후 IGW로 나감
- 왕복이 같은 어플라이언스를 거치는 대칭 라우팅 구성이 핵심 → 비대칭 시 세션 기반 검사 불가

---

## 라우트 테이블 예시 (GWLB 방식)

|라우트 테이블|Destination|Target|
|---|---|---|
|edge association RT (IGW 연결)|10.0.1.0/24 (워크로드 서브넷)|GWLBe|
|워크로드 서브넷 RT|0.0.0.0/0|GWLBe|
|어플라이언스 서브넷 RT|0.0.0.0/0|IGW|

- edge RT의 destination은 반드시 해당 VPC CIDR 범위 내로만 지정 가능
- ENI 직접 지정 방식이면 Target을 GWLBe 대신 UTM ENI로 교체

---

## 벤더별 지원

|항목|Palo Alto VM-Series|FortiGate-VM|
|---|---|---|
|GWLB(GENEVE) 연동|지원|지원|
|배포 방식|Marketplace AMI, IaC 템플릿 제공|Marketplace AMI, IaC 템플릿 제공|
|Auto Scaling|Panorama 연동 스케일링|FortiGate Auto Scaling 템플릿|
|중앙 관리|Panorama|FortiManager|

---

## 주의할 점

- edge association 라우트의 target은 local, GWLBe, 동일 VPC 내 ENI만 가능 → TGW나 타 VPC 리소스로는 우회 불가
- destination은 해당 VPC CIDR 내로 제한 → 여러 VPC를 한곳에서 검사하려면 edge association이 아니라 TGW + inspection VPC 구성 사용
- ENI 방식은 UTM 인스턴스의 Source/Dest Check를 반드시 비활성화
- GWLB는 flow 단위로 어플라이언스에 고정(sticky) → 어플라이언스 장애 시 기존 flow 처리 동작 확인 필요
- GWLB는 원본 패킷을 GENEVE로 감싸 그대로 전달하므로 UTM에서 NAT 없이 투명(inline) 검사 가능

### 참고

- 출처: https://docs.aws.amazon.com/vpc/latest/userguide/gateway-route-tables.html

## 결론

- 단일 VPC 인바운드 검사는 edge association + GWLB 조합이 표준, ENI 직접 지정은 소규모/PoC용
- 멀티 VPC 검사가 필요하면 TGW 기반 inspection VPC로 분리 설계할 것
- UTM 구성에서 edge association은 "인바운드 우회 라우팅", GWLB는 "검사 계층의 확장"이라고 이해하면 됌
