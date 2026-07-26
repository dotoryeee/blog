---
draft: false
date: 2026-07-26
authors:
  - dotoryeee
categories:
  - Security
tags:
  - SCP
  - IAM
  - VPC Endpoint
description: "자격 증명·리소스·네트워크 세 축으로 나눠 SCP와 RCP, 리소스 정책, 엔드포인트 정책이 각각 무엇을 막는지와 조건 키 사용법 정리"
hide:
  - toc
---
# AWS 데이터 경계 정리

<!-- more -->

## 데이터 경계란
데이터 경계(Data Perimeter)란 내 조직의 자격 증명이 내 조직의 리소스에만, 예상한 네트워크를 거쳐서만 닿도록 조직 단위로 못 박는 통제 설계

- 대상: 개별 권한이 아니라 조직 전체에 깔아 두는 최대 한도
- 성격: 권한을 주는 장치가 아니라 이미 준 권한의 상한을 깎는 장치
- 전제: 실제 권한은 여전히 자격 증명 기반 정책과 리소스 정책이 부여
- 목적: 잘못 설정된 정책 하나가 조직 밖으로 데이터를 흘리는 경로를 구조적으로 차단

---

## 세 가지 축
막고 싶은 상황이 다르면 쓰는 수단도 갈림

| 축 | 막는 상황 | 주 수단 |
|----|---------|--------|
| 신뢰할 수 있는 자격 증명 | 조직 밖 계정의 자격 증명이 내 리소스에 접근 | RCP, 리소스 정책 |
| 신뢰할 수 있는 리소스 | 내 자격 증명이 조직 밖 리소스로 데이터를 내보냄 | SCP, VPC 엔드포인트 정책 |
| 신뢰할 수 있는 네트워크 | 예상 밖 네트워크에서 내 자격 증명이 쓰임 | SCP, RCP·리소스 정책 |

- 세 축은 서로 다른 방향을 막으므로 하나만 걸어서는 경계가 닫히지 않음
- 자격 증명과 리소스는 서로 반대 방향 → 들어오는 쪽과 나가는 쪽을 각각 봐야 함

---

## 정책 유형별 역할
같은 Deny라도 어디에 붙느냐에 따라 제한하는 대상이 다름

| 정책 | 제한 대상 | 적용 범위 | 관리 계정 |
|------|---------|---------|---------|
| SCP | member 계정의 IAM 사용자·역할 | 조직·OU·계정에 부착 | 적용 안 됨 |
| RCP | member 계정의 리소스 | 조직·OU·계정에 부착 | 적용 안 됨 |
| 리소스 정책 | 해당 리소스 하나 | 리소스에 직접 부착 | 해당 없음 |
| VPC 엔드포인트 정책 | 그 엔드포인트를 지나는 요청 | 엔드포인트에 부착 | 해당 없음 |

- SCP도 RCP도 권한을 부여하지 않음 → 최종 권한은 네 종류가 모두 허용하는 교집합
- RCP는 조직 밖 프린시펄이 내 리소스를 건드리는 경우까지 막는다는 점에서 SCP와 방향이 반대
- 둘 다 서비스 연결 역할(Service-linked role)에는 적용되지 않음
- RCP는 AWS 관리형 KMS 키에도 적용되지 않음

### RCP 지원 범위
RCP는 모든 서비스에 걸리지 않고 지원 목록에 있는 서비스에만 적용됨

- 포함: S3, KMS, STS, SQS, Secrets Manager, CloudWatch Logs, DynamoDB, ECR 등 40여 개
- 미포함 서비스는 리소스 정책으로 개별 처리해야 함
- 조직에서 모든 기능(All features)이 켜져 있어야 사용 가능

---

## 조건 키
경계를 만드는 실체는 Deny 문에 붙는 조건 키

| 조건 키 | 값 | 쓰이는 축 |
|--------|----|---------|
| `aws:PrincipalOrgID` | 요청 주체가 속한 조직 ID | 자격 증명 |
| `aws:PrincipalOrgPaths` | 주체의 조직 경로. 다중값이라 `ForAnyValue` 필요 | 자격 증명 |
| `aws:ResourceOrgID` | 대상 리소스를 소유한 계정의 조직 ID | 리소스 |
| `aws:SourceVpc` | 요청이 통과한 엔드포인트가 붙은 VPC ID | 네트워크 |
| `aws:SourceVpce` | 요청이 사용한 VPC 엔드포인트 ID | 네트워크 |
| `aws:VpcSourceIp` | 엔드포인트를 지난 요청자의 사설 IP | 네트워크 |
| `aws:PrincipalIsAWSService` | AWS 서비스 주체의 직접 호출 여부 | 예외 처리 |
| `aws:ViaAWSService` | 다른 서비스를 거쳐 온 요청인지 여부 | 예외 처리 |

- `aws:SourceVpc`와 `aws:SourceVpce`는 VPC 엔드포인트를 지난 요청에만 값이 생김 → 인터넷 경유 요청에는 키 자체가 없음
- `StringNotEqualsIfExists`는 키가 아예 없는 요청에서도 조건이 참이 되어 Deny가 그대로 걸림 → 키 없이 오는 경로까지 차단 범위에 넣는 선택
- 키가 없는 정상 경로를 살리는 것은 `IfExists`가 아니라 `aws:PrincipalIsAWSService`·`aws:ViaAWSService` 예외 조건
- `aws:PrincipalOrgID`·`aws:ResourceOrgID`·`aws:SourceVpc`·`aws:SourceVpce`는 민감한 키로 분류돼 와일드카드를 쓰지 않는 것이 원칙
- `aws:PrincipalOrgPaths`는 예외로 `ForAnyValue:StringLike`와 와일드카드를 함께 씀
- `aws:PrincipalVpc`라는 키는 없음 → 주체 쪽 VPC는 `aws:SourceVpc`나 `aws:Ec2InstanceSourceVpc`로 봄

---

## 정책 예시

조직 밖 자격 증명이 내 S3 버킷에 접근하는 것을 조직 차원에서 막는 RCP

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyNonOrgPrincipals",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:PrincipalOrgID": "o-example12345"
        },
        "BoolIfExists": {
          "aws:PrincipalIsAWSService": "false"
        }
      }
    }
  ]
}
```

내 자격 증명이 조직 밖 리소스로 데이터를 내보내는 것을 막는 SCP

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyExternalResources",
      "Effect": "Deny",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:ResourceOrgID": "o-example12345"
        },
        "BoolIfExists": {
          "aws:ViaAWSService": "false"
        }
      }
    }
  ]
}
```

- `aws:PrincipalIsAWSService` 예외를 빼면 AWS 서비스가 대신 호출하는 정상 동작까지 막힘
- `aws:ViaAWSService` 예외도 같은 이유 → 서비스 경유 호출은 조건 키 값이 다르게 잡힘

---

## 적용 순서
한 번에 루트에 붙이면 조직 전체가 멈출 수 있어 단계를 나눔

1. 계정 하나에 붙여 영향 범위를 확인
2. 하위 OU로 올려 같은 정책을 검증
3. 문제가 없으면 조직 루트로 승격
4. 각 단계에서 CloudTrail의 Access Denied를 근거로 오탐을 걸러냄

- 먼저 조일 축은 자격 증명 쪽 → 조직 밖 접근 차단은 정상 트래픽에 미치는 영향이 가장 작음
- 네트워크 축은 마지막 → 온프레미스·서비스 경유 경로까지 다 걸러야 해서 오탐이 가장 많음

---

## 주의
- SCP와 RCP 모두 관리 계정에는 걸리지 않음 → 관리 계정에 워크로드를 두면 경계 밖에 남음
- 서비스 연결 역할은 어느 쪽으로도 못 막으므로 별도 통제가 필요
- 조건 키가 없는 정상 요청은 `IfExists`가 아니라 서비스 예외 조건으로 살릴 것
- 조직 밖 주체가 내 엔드포인트를 지나는 시도는 호출자 계정에만 기록됨 → 내 쪽 기록은 [CloudTrail 네트워크 활동 이벤트 정리](cloudtrail_network_events.md)에서 다룬 네트워크 활동 이벤트로 확보
- RCP 미지원 서비스가 남아 있어 전면 차단으로 오해하면 안 됨

---

## 결론
- 데이터 경계는 자격 증명·리소스·네트워크 세 축을 각각 다른 정책으로 막아 완성되는 설계
- SCP는 내 주체가 밖으로 나가는 것을, RCP는 밖의 주체가 내 리소스로 들어오는 것을 막아 방향이 서로 반대
- 조건 키는 서비스 예외를 함께 걸어야 AWS 서비스가 대신 호출하는 정상 동작을 깨뜨리지 않음
- 관리 계정과 서비스 연결 역할은 경계 밖에 남으므로 설계 단계에서 따로 다룰 것
- 차단은 정책이 맡고 기록은 CloudTrail이 맡는 구성으로 나눠 보는 편이 실용적
