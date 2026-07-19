---
draft: false
date: 2025-03-13
authors:
  - dotoryeee
categories:
  - Cloud
  - Network
---
# IGW가 직접 연결되지 않은 VPC에서 EC2의 Public IP를 사용하는 예제(Edge Association)

<!-- more -->

!!! warning
    아래 "시도한 구성"은 AWS에서 성립하지 않음. IGW edge association 라우트 테이블은 TGW를 target으로 지정할 수 없고, destination도 IGW가 속한 VPC의 CIDR 범위 내여야 함. 상세와 대안은 "제약 사항"·"실제로 가능한 구성"에서 정정함

## 시도한 구성 (성립하지 않음)

``` mermaid
graph TD;
  Client["외부 클라이언트 (3.x.x.x)"]
  
  subgraph AWS_Cloud ["AWS 내부"]
    subgraph A_VPC ["A VPC (10.0.0.0/16) - IGW 포함"]
      A_TGW_Subnet["A TGW Subnet (10.0.2.0/24) - TGW Attachment"]
      IGW["Internet Gateway"]
    end

    subgraph B_VPC ["B VPC (10.1.0.0/16) - IGW 없음"]
      B_Subnet["B Subnet (10.1.1.0/24) - EC2 Public IP 포함"]
    end

    TGW["Transit Gateway"]

    subgraph AWS_Instances ["B Subnet에 위치한 EC2 Instance B"]
      EC2_B["B EC2 ENI (Public IP 52.x.x.x, Private IP 10.1.1.20)"]
    end
  end

  Client -->|"Public IP (52.x.x.x) 요청"| IGW
  IGW -->|"Edge Association Route Table을 참조하여 EC2_B의 Private IP 찾기"| A_TGW_Subnet
  A_TGW_Subnet -->|"트래픽 전달"| TGW
  TGW -->|"트래픽 전달"| B_Subnet
  B_Subnet -->|"EC2_B (Private IP 10.1.1.20)로 전달"| EC2_B

  EC2_B -->|"응답 트래픽"| B_Subnet
  B_Subnet -->|"트래픽 전달"| TGW
  TGW -->|"트래픽 전달"| A_TGW_Subnet
  A_TGW_Subnet -->|"트래픽 전달"| IGW
  IGW -->|"사용자에게 응답 반환"| Client

```
## ingress flow (의도)
1. 클라이언트 (3.x.x.x) → EC2_B Public IP (52.x.x.x) 요청
2. IGW가 요청을 받고, Edge Association Route Table을 통해 TGW로 전달
3. TGW가 트래픽을 B VPC로 전달
4. B VPC내 B subnet의 EC2_B (Private IP: 10.1.1.20) 가 트래픽 수신

## egress flow (의도)
1. EC2_B (Private IP: 10.1.1.20) → 클라이언트 응답 생성
2. B subnet 라우트 테이블에서 TGW로 전달
3. TGW가 트래픽을 A VPC로 전달
4. A TGW subnet에서 IGW를 통해 외부 인터넷으로 전달
5. 클라이언트(3.x.x.x) 가 응답을 수신


## 라우팅 설정 (의도)
```sh
IGW edge associate 라우트 테이블:
+--------------+-------------------+
| Destination  | Target            |
+--------------+-------------------+
| 10.1.0.0/16  | TGW (tgw-xxxxxxx) |
+--------------+-------------------+

A TGW Subnet 라우트 테이블:
+--------------+-------------------+
| Destination  | Target            |
+--------------+-------------------+
| 0.0.0.0/0    | IGW (igw-xxxxxxx) |
| 10.1.0.0/16  | TGW (tgw-xxxxxxx) |
+--------------+-------------------+

TGW 라우트 테이블:
+--------------+--------------------+
| Destination  | Target             |
+--------------+--------------------+
| 0.0.0.0/0    | A VPC Attachment   |
| 10.1.0.0/16  | B VPC Attachment   |
+--------------+--------------------+

B Subnet 라우트 테이블:
+--------------+-------------------+
| Destination  | Target            |
+--------------+-------------------+
| 0.0.0.0/0    | TGW (tgw-xxxxxxx) |
| 10.0.0.0/16  | TGW (tgw-xxxxxxx) |
+--------------+-------------------+

```

## 제약 사항
IGW edge association 라우트 테이블(gateway route table)의 제약으로 위 구성은 성립하지 않음.

- target은 local, Gateway Load Balancer endpoint, 동일 VPC 내 ENI(network interface)만 허용 → TGW 지정 불가
- destination은 IGW가 속한 VPC의 CIDR 내에서만 지정 가능(VPC 전체 CIDR 또는 VPC 내 서브넷 CIDR) → 위 예의 10.1.0.0/16은 A VPC(10.0.0.0/16) 범위 밖이라 라우트 추가 자체가 불가
- 따라서 IGW에서 TGW로 인바운드를 넘겨 B VPC EC2로 전달하는 흐름은 구성 불가
- Public IP NAT는 인스턴스가 속한 VPC의 IGW가 수행 → IGW 없는 B VPC의 EC2는 애초에 Public IP 매핑을 받지 못함

| 항목 | 허용 값 |
|------|--------|
| target | local, Gateway Load Balancer endpoint, 동일 VPC 내 ENI |
| destination | IGW가 속한 VPC의 전체 CIDR 또는 VPC 내 서브넷 CIDR |
| 불가 | TGW, NAT Gateway, 다른 VPC CIDR, 개별 호스트 IP |

## 실제로 가능한 구성
IGW 없는 B VPC의 워크로드를 외부에 노출하려면 퍼블릭 진입점을 A VPC에 두고 TGW로 B VPC에 private IP로 전달함.

### 방식 1: A VPC에 퍼블릭 로드밸런서 배치

``` mermaid
graph TD;
  Client["외부 클라이언트 (3.x.x.x)"]

  subgraph AWS_Cloud ["AWS 내부"]
    subgraph A_VPC ["A VPC (10.0.0.0/16) - IGW 포함"]
      IGW["Internet Gateway"]
      ALB["ALB/NLB (A VPC public 서브넷)"]
      A_TGW_Subnet["A TGW Subnet (10.0.2.0/24) - TGW Attachment"]
    end

    subgraph B_VPC ["B VPC (10.1.0.0/16) - IGW 없음"]
      EC2_B["B EC2 ENI (Private IP 10.1.1.20)"]
    end

    TGW["Transit Gateway"]
  end

  Client -->|"Public IP 요청"| IGW
  IGW -->|"A VPC public 서브넷"| ALB
  ALB -->|"타깃: B EC2 Private IP (10.1.1.20)"| A_TGW_Subnet
  A_TGW_Subnet -->|"트래픽 전달"| TGW
  TGW -->|"B VPC로 전달"| EC2_B
```

- A VPC public 서브넷에 ALB/NLB 생성 → A VPC IGW로 Public IP 확보
- 로드밸런서 타깃을 B VPC EC2의 private IP로 지정(IP 타깃), TGW 경유로 도달
- B VPC EC2는 private IP만 유지하며 별도 Public IP 불필요

### 방식 2: GWLB 기반 중앙 집중식 ingress
- IGW edge association 라우트의 target을 A VPC 내 GWLB endpoint(또는 검사 어플라이언스 ENI)로 지정(destination은 A VPC CIDR)
- 어플라이언스가 검사 후 TGW로 B VPC에 private IP로 포워딩
- 이 방식에서 검사 어플라이언스 ENI는 Source/Destination Check 해제 필요
