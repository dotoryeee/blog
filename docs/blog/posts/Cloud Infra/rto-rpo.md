---
draft: false
date: 2025-05-11
authors:
  - dotoryeee
categories:
  - Cloud
  - Server
---
# RTO vs RPO

<!-- more -->


## RTO(Recovery Time Objective) vs. RPO(Recovery Point Objective) 개념

| 용어 | 정의 |
|------|------|
| RTO (Recovery Time Objective, 복구 시간 목표) | 시스템 장애 발생 후, 서비스가 정상적으로 복구되기까지 허용 가능한 최대 시간 |
| RPO (Recovery Point Objective, 복구 지점 목표) | 장애 발생 시, 복구할 수 있는 가장 최신 데이터의 기준 시점 |

---

## RTO와 RPO의 차이점

| 비교 항목 | RTO (복구 시간 목표) | RPO (복구 지점 목표) |
|----------|--------------------|--------------------|
| 목적 | 서비스 복구 속도 보장 | 데이터 손실 최소화 |
| 의미 | 장애 발생 후, 시스템을 복구할 수 있는 최대 시간 | 장애 발생 시, 복구 가능한 최신 데이터 시점 |
| 단위 | 시간(초, 분, 시간, 일) | 시간(초, 분, 시간) |
| 핵심 질문 | "시스템을 몇 시간 안에 복구해야 하는가?" | "최대 몇 시간 전의 데이터까지 복구 가능해야 하는가?" |
| 비즈니스 영향 | RTO가 길면 서비스 다운타임이 길어져 사용자 및 수익에 직접적인 영향 | RPO가 길면 데이터 손실 가능성이 커짐 |
| 백업 전략 | 장애 대응을 위한 재해 복구(DR) 및 고가용성(AWS Multi-AZ, Load Balancer 등) 활용 | 백업 빈도 및 데이터 복제(AWS S3, RDS 스냅샷, DynamoDB Streams 등) 활용 |
| 비용 고려 | RTO가 짧을수록(빠른 복구) 비용 증가 (HA, DR 구축 비용) | RPO가 짧을수록(데이터 손실 최소화) 비용 증가 (고빈도 백업, 지속적 복제) |

---

## RTO와 RPO의 이해를 돕는 예제

### 예제 1: 은행 시스템
- RTO: 장애 발생 후 5분 안에 서비스가 정상적으로 복구되어야 함.
- RPO: 장애 발생 전 최대 1초 전의 데이터까지 복구 가능해야 함 (거래 데이터 손실 불가).

### 예제 2: 블로그 서비스
- RTO: 장애 발생 후 1시간 안에 서비스가 정상적으로 복구되면 됨.
- RPO: 장애 발생 전 1일 전 데이터까지만 복구 가능해도 무방함.

### 예제 3: 온라인 쇼핑몰
- RTO: 장애 발생 후 10분 안에 서비스가 복구되지 않으면 매출 손실 발생.
- RPO: 장애 발생 전 10분 전의 데이터까지 복구 가능해야 함 (주문 정보 손실 최소화).

---

## AWS에서 RTO & RPO를 충족하는 방법

| AWS 서비스 | RTO 단축 (빠른 복구) | RPO 최소화 (데이터 보호) |
|------------|--------------------|--------------------|
| AWS Multi-AZ (RDS, DynamoDB 등) | 자동 장애 조치로 빠른 복구 | 실시간 데이터 복제 |
| AWS Backup | 신속한 백업 복구 가능 | 백업 빈도를 높이면 RPO 최소화 가능 |
| Amazon S3 Cross-Region Replication | 장애 시 빠르게 데이터 복구 가능 | 여러 리전에 걸쳐 데이터 복제 |
| AWS Lambda & S3 Event Notification | 장애 감지 후 자동으로 복구 수행 | 실시간 데이터 백업 가능 |
| Amazon Aurora Global Database | 다른 리전에 복제본을 유지하여 복구 가능 | 지속적인 데이터 동기화 |

---

## 결론
- RTO는 "얼마나 빨리 시스템을 복구할 것인가"를 의미함.
- RPO는 "얼마나 최신 데이터를 보장할 것인가"를 의미함.
- RTO와 RPO 목표가 낮을수록(복구 시간이 짧고, 데이터 손실이 적을수록) 비용이 증가함.
- 비즈니스 중요도에 따라 비용 vs. 복구 전략을 적절히 설계하는 것이 중요함.
- RTO는 "다운타임 최소화", RPO는 "데이터 손실 최소화"라고 이해하면 됌

# RTO, RPO 관련 용어 및 차이점

## 1. RTO & RPO와 관련된 주요 용어

| 용어 | 정의 | RTO & RPO와의 관계 | 사용처 |
|------|------|----------------|------|
| MTTR (Mean Time to Recovery, 평균 복구 시간) | 장애 발생 후 시스템이 복구되는 평균 시간 | RTO와 유사하지만, 실제 복구 시간이 포함됨 | IT 운영 및 장애 관리, 서비스 복구 전략 |
| MTBF (Mean Time Between Failures, 평균 고장 간격) | 두 번의 장애 발생 사이의 평균 시간 | 장애 발생 빈도가 높을수록 RTO와 RPO 요구사항이 더 중요해짐 | 시스템 안정성 평가, 유지보수 계획 |
| DR (Disaster Recovery, 재해 복구) | 장애 또는 재해 발생 시 시스템을 복구하는 전략 및 프로세스 | RTO/RPO 목표에 따라 DR 전략이 결정됨 | 고가용성 시스템, 데이터 보호 솔루션 |
| HA (High Availability, 고가용성) | 장애 발생 시에도 서비스가 지속적으로 운영될 수 있도록 하는 시스템 설계 | RTO를 최소화하기 위한 핵심 전략 | 금융 서비스, 미션 크리티컬 시스템 |
| BCP (Business Continuity Planning, 업무 연속성 계획) | 장애 발생 시 비즈니스 운영을 지속할 수 있도록 하는 계획 | RTO/RPO를 기반으로 DR 및 HA 전략을 포함 | 기업 IT 운영, 리스크 관리 |
| Failover (장애 조치) | 장애 발생 시 자동으로 대체 시스템으로 전환하는 프로세스 | RTO를 최소화하는 핵심 메커니즘 | 클라우드 서비스, 데이터센터 운영 |
| Backup (백업) | 데이터를 정기적으로 저장하여 장애 발생 시 복구 가능하도록 하는 방법 | RPO를 충족하는 데 필수적 | 데이터 보호, 법적 규제 준수 |
| Replication (복제) | 데이터를 실시간으로 다른 위치에 동기화하여 저장하는 방법 | RPO를 최소화하고 실시간 복구 가능하게 함 | 금융 시스템, AWS Multi-AZ, Redshift 복제 |

---


## 결론
- MTTR은 RTO와 유사하지만 실제 평균 복구 시간을 측정하는 데 사용됨.
- MTBF는 장애 발생 빈도를 나타내며, 장애 발생이 많을수록 RTO/RPO 요구사항이 더 중요해짐.
- DR(재해 복구)은 RTO/RPO 목표를 기반으로 수립되며, HA 및 백업 전략을 포함함.
- Replication은 RPO를 최소화하는 데 필수적이며, 실시간 데이터 보호가 필요한 환경에서 사용됨.
- AWS 환경에서는 Multi-AZ, Auto Scaling, S3 Cross-Region Replication 등의 서비스를 활용하여 RTO/RPO 목표를 달성할 수 있음.

# Legacy vs AWS 환경에서 RTO, RPO, MTTR, MTBF 최소화 방안

## 개념 정리
| 용어 | 정의 | 최소화해야 하는 이유 |
|------|------|----------------|
| RTO (Recovery Time Objective) | 장애 발생 후 서비스 복구까지 허용 가능한 최대 시간 | 서비스 다운타임 최소화 |
| RPO (Recovery Point Objective) | 장애 발생 시 데이터 손실 허용 범위 (최신 백업과의 차이) | 데이터 유실 최소화 |
| MTTR (Mean Time to Recovery) | 장애 발생 후 복구까지 걸리는 평균 시간 | 신속한 장애 대응 |
| MTBF (Mean Time Between Failures) | 장애 발생 후 다음 장애까지의 평균 시간 | 시스템 안정성 증가 |

---

## Legacy 환경 (온프레미스)에서 최소화 방안
| 요소 | 최소화 방법 | 설명 |
|------|-----------|------|
| RTO 최소화 | 이중화(HA) 서버 구성 | 물리적 서버 및 데이터센터 이중화 |
| | DR(재해 복구) 센터 운영 | 이중 데이터센터를 구성하여 장애 시 신속한 복구 |
| | 자동화된 장애 감지 및 복구 스크립트 | 장애 감지 후 자동 페일오버 수행 |
| RPO 최소화 | 고빈도 백업 수행 | RAID, SAN, NAS 백업 주기 단축 |
| | 실시간 데이터 복제 | DB 복제 (Active-Standby, Active-Active) |
| | 테이프 백업에서 디스크 기반 백업 전환 | 신속한 데이터 복구 가능 |
| MTTR 최소화 | 모니터링 시스템 구축 | 장애 탐지 시스템 (Nagios, Zabbix) |
| | 장애 대응 매뉴얼 운영 | 장애 복구 절차 표준화 |
| | 예비 부품/서버 유지 | 장애 발생 시 신속한 하드웨어 교체 |
| MTBF 최소화 | 정기적인 유지보수 및 점검 | 하드웨어 및 네트워크 점검 |
| | 서버/스토리지 이중화 | 단일 장애점(SPOF) 제거 |
| | 전원 및 냉각 시스템 보강 | UPS, 발전기 추가 구축 |

---

## AWS 환경에서 최소화 방안
| 요소 | 최소화 방법 | AWS 서비스 활용 |
|------|-----------|----------------|
| RTO 최소화 | Auto Scaling | EC2 자동 확장으로 장애 시 대체 인스턴스 생성 |
| | Multi-AZ 구성 | RDS, ElastiCache 등을 멀티 AZ로 구성하여 장애 시 자동 전환 |
| | AWS Elastic Load Balancer (ELB) | 트래픽을 자동으로 정상 인스턴스로 라우팅 |
| | AWS Route 53 | 장애 감지 후 자동 페일오버 수행 |
| RPO 최소화 | S3 Cross-Region Replication | S3 데이터를 다른 리전에 실시간 복제 |
| | RDS Read Replica | DB 복제를 통해 최신 데이터 유지 |
| | AWS Backup & EBS Snapshot | 정기적인 데이터 백업 |
| | DynamoDB Global Tables | 글로벌 데이터 복제 |
| MTTR 최소화 | CloudWatch + SNS 알림 | 장애 감지 후 즉시 알림 전송 |
| | AWS Lambda로 자동 복구 | 장애 감지 시 복구 스크립트 실행 |
| | AWS System Manager | 장애 원인 분석 및 원격 명령 실행 |
| | EC2 Auto Healing | 장애 발생 시 자동으로 대체 인스턴스 배포 |
| MTBF 최소화 | AWS Well-Architected Framework 적용 | 안정적인 아키텍처 설계 가이드 준수 |
| | Auto Scaling 활용 | 트래픽 급증 시 시스템 부하 방지 |
| | AWS Trusted Advisor | 보안 및 인프라 문제 사전 탐지 |

---

## Legacy vs AWS 비교 요약
| 요소 | Legacy 환경 | AWS 환경 |
|------|-----------|---------|
| RTO 최소화 | 이중화 서버, DR 센터 | Auto Scaling, Multi-AZ, ELB |
| RPO 최소화 | 고빈도 백업, 실시간 복제 | S3 Replication, RDS Read Replica, AWS Backup |
| MTTR 최소화 | 모니터링 시스템, 장애 대응 매뉴얼 | CloudWatch, Lambda 자동 복구, Auto Healing |
| MTBF 최소화 | 정기 유지보수, 이중화 | Well-Architected Framework, Auto Scaling |

---

## 결론
- Legacy 환경에서는 하드웨어 이중화, DR 센터 운영, 정기 점검이 필요하지만, 비용과 운영 부담이 큼.
- AWS 환경에서는 Auto Scaling, Multi-AZ, AWS Backup, CloudWatch 자동 모니터링 등을 활용하여 RTO/RPO/MTTR/MTBF를 자동화할 수 있음.
- AWS의 자동 복구 기능을 활용하면 Legacy 대비 더 빠르게 장애 복구 가능하며, 운영 비용도 절감할 수 있음.


# PITR (Point-In-Time Recovery) 개념과 동작 방식

## PITR(Point-In-Time Recovery)란?
PITR(시점 복구, Point-In-Time Recovery)는 데이터베이스에서 특정 시점으로 데이터를 복구할 수 있는 기능입니다.  
데이터 손실 또는 장애 발생 시, 사용자가 지정한 특정 시점으로 DB 상태를 복원할 수 있습니다.

---

## PITR의 원리 및 동작 방식
PITR은 주기적인 백업(snapshot) + 변경 로그(transaction log, WAL/Binlog)를 사용하여 원하는 시점으로 복구하는 방식입니다.

### PITR 동작 방식
1. Full Backup(스냅샷) 생성  
    주기적으로 전체 데이터베이스의 정확한 복사본(스냅샷)을 저장  
    MySQL은 `mysqldump`, PostgreSQL은 `pg_basebackup`과 같은 방법 사용
2. 변경 로그(트랜잭션 로그) 지속적 기록  
    백업 이후 발생하는 모든 변경 사항을 트랜잭션 로그(WAL, Binlog)에 저장  
    MySQL: Binary Log (Binlog) 사용  
    PostgreSQL: WAL(Write-Ahead Logging) 사용
3. 복구 요청 발생  
    데이터베이스 관리자(DBA)가 특정 시점(예: `2025-03-10 14:30:00`)으로 복구 요청
4. Snapshot(전체 백업) 복원 후 트랜잭션 로그 적용  
    가장 가까운 Full Backup(스냅샷)으로 복원  
    스냅샷 이후의 트랜잭션 로그를 차례로 적용하여 지정된 시점까지 복구  
    이 과정에서 특정 트랜잭션을 제외하고 적용 가능 (Selective Recovery)
5. 지정된 시점으로 DB 상태 복원 완료  
    해당 시점의 정확한 데이터 상태로 DB가 복구됨  

---

## PITR과 일반 백업 비교

| 비교 항목 | 일반 백업 | PITR |
|-----------|----------|------|
| 복구 가능 범위 | 특정 시점의 백업으로만 복구 가능 | 백업 이후 원하는 특정 시점으로 복구 가능 |
| 데이터 손실 가능성 | 백업 이후 변경된 데이터는 손실될 가능성이 있음 | 트랜잭션 로그를 활용하여 최소한의 데이터 손실 |
| 복구 속도 | 빠름 (백업된 시점으로만 복구) | 비교적 느림 (트랜잭션 로그를 순차적으로 적용해야 함) |
| 사용 사례 | 주기적인 백업만 필요할 때 | 데이터 실수 삭제 복구, 장애 발생 시 특정 시점 복구 |

---

## PITR이 유용한 사례
운영자의 실수로 인해 데이터 손실이 발생한 경우  
   - 실수로 `DELETE` 또는 `UPDATE` 실행 시 삭제되기 전 상태로 복구 가능

랜섬웨어 공격 또는 데이터 손상 발생 시  
   - 특정 시점(공격 발생 직전)으로 복구하여 피해 최소화

애플리케이션 장애 발생 후 롤백할 필요가 있는 경우  
   - 잘못된 배포 후 데이터가 변경된 경우, 배포 전 상태로 복원 가능

---

## AWS에서 PITR 적용 방법
AWS에서는 RDS, DynamoDB에서 PITR 기능을 제공(RDS 모든 엔진 사용 가능)

### Amazon RDS의 PITR
- Binary Log(Binlog) 또는 WAL을 사용하여 특정 시점 복구 가능
- RDS 콘솔, AWS CLI, API를 사용하여 특정 시점으로 복원 가능
- 최대 35일까지 트랜잭션 로그 보관 가능
