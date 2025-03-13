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
    EC2 ENI의 `Source/Destination Check`를 해제해야 함

## 네트워크 구성 관계 

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
## ingress flow
1. 클라이언트 (3.x.x.x) → EC2_B Public IP (52.x.x.x) 요청
2. IGW가 요청을 받고, Edge Association Route Table을 통해 TGW로 전달
3. TGW가 트래픽을 B VPC로 전달
4. B VPC내 B subnet의 EC2_B (Private IP: 10.1.1.20) 가 트래픽 수신

## egress flow
1. EC2_B (Private IP: 10.1.1.20) → 클라이언트 응답 생성
2. B subnet 라우트 테이블에서 TGW로 전달
3. TGW가 트래픽을 A VPC로 전달
4. A TGW subnet에서 IGW를 통해 외부 인터넷으로 전달
5. 클라이언트(3.x.x.x) 가 응답을 수신


## 라우팅 설정
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