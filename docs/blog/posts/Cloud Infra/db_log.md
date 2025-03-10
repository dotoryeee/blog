---
draft: true
date: 2025-05-11
authors:
  - dotoryeee
categories:
  - Cloud
  - Server
---
# DB 로그와 Aurora 정리

<!-- more -->


## 데이터베이스 로그

| 로그 종류 | 역할 |
|----------|------|
| WAL (Write-Ahead Logging) | 데이터를 데이터 파일에 쓰기 전에 먼저 로그에 기록하여 장애 발생 시 복구 가능 |
| Redo Log | 커밋된 변경 사항을 기록하여 장애 발생 시 데이터 복원 |
| Undo Log | 트랜잭션 롤백을 위해 변경 이전의 데이터를 기록 |
| Binlog (Binary Log) | 변경된 데이터를 이진 형식으로 저장하여 복제 및 복구 용도로 사용 (MySQL) |
| Slow Query Log | 실행 시간이 긴 쿼리를 기록하여 성능 분석 및 최적화에 활용 |
| Error Log | DB에서 발생한 오류 및 경고 메시지 기록 |

## MySQL과 PostgreSQL의 로그 종류 비교

| 로그 종류 | MySQL | PostgreSQL |
|-----------|-------|------------|
| 에러 로그(Error Log) | 서버 시작 및 종료 정보, 오류 및 경고 메시지 기록 | 서버 시작 및 종료 정보, 오류 및 경고 메시지 기록 |
| 일반 쿼리 로그(General Query Log) | 클라이언트 연결 및 모든 SQL 문 기록 | 모든 SQL 문 및 연결 정보 기록 |
| 슬로우 쿼리 로그(Slow Query Log) | 실행 시간이 긴 쿼리 기록 | 실행 시간이 긴 쿼리 기록 |
| 바이너리 로그(Binary Log) | 데이터 변경 이벤트 및 트랜잭션 기록, 복제 및 복구에 사용 | 해당 없음 |
| 리두 로그(Redo Log) | InnoDB 스토리지 엔진에서 사용, 데이터 변경 사항을 기록하여 장애 발생 시 복구에 사용 | WAL(Write-Ahead Logging) 메커니즘으로 구현, 데이터 변경 사항을 기록하여 장애 발생 시 복구에 사용 |
| 언두 로그(Undo Log) | 트랜잭션 롤백 및 MVCC(다중 버전 동시성 제어)를 위해 사용 | 트랜잭션 롤백 및 MVCC를 위해 사용 |


---

## Write-Ahead Logging (WAL)의 동작 방식
- 트랜잭션이 변경을 수행하면 변경 사항을 먼저 WAL 로그에 기록
- WAL이 디스크에 안전하게 기록된 후 데이터 파일을 수정
- 장애 발생 시 WAL 로그를 활용하여 최근 트랜잭션을 재적용하거나 롤백
- PostgreSQL, MySQL InnoDB, Oracle 등의 주요 DBMS에서 사용됨

---

## AWS Aurora에서 로그의 작용 방식

AWS Aurora(MySQL 및 PostgreSQL 호환)에서는 기본적으로 WAL 및 Binlog를 내부적으로 관리하며 클러스터 기반으로 동작하여 고가용성을 제공함.

### Aurora의 로그 관련 특징
| 로그 유형 | Aurora에서의 역할 |
|----------|-----------------|
| Redo Log | Aurora 스토리지 계층에 비동기적으로 저장되어 빠른 장애 복구 지원 |
| Undo Log | InnoDB 기반에서 변경 전 데이터를 유지하여 트랜잭션 롤백 지원 |
| Binlog | Aurora 복제(Aurora Read Replica) 또는 외부 MySQL 복제를 위해 사용됨 |
| Slow Query Log | 성능 분석을 위해 활성화 가능하며, CloudWatch 및 S3로 내보내기 가능 |
| Error Log | 오류 및 이벤트 기록, RDS 콘솔 또는 CloudWatch에서 확인 가능 |

---

## Aurora에서 WAL 및 로그 활용 방식
### Aurora는 WAL 기반 Redo Log를 중앙 스토리지 계층에서 관리
- 일반적인 RDS와 달리, Aurora는 WAL을 공유 스토리지 계층에 저장하여 빠른 장애 복구 및 복제 지원
- 기존 MySQL은 InnoDB에서 Redo Log를 관리하지만, Aurora는 Redo Log를 스토리지에 저장하여 별도 장애 복구 불필요

### Aurora Replication (고가용성 및 읽기 확장)
- WAL을 Aurora 스토리지 계층에 저장하여 읽기 노드(Read Replica)로 실시간 복제  
- WAL이 공유되어 Aurora Replicas는 WAL을 직접 적용하여 빠른 읽기 성능 제공

### Aurora의 Crash Recovery (장애 복구)
- 기존 DBMS에서는 WAL을 적용하여 복구해야 하지만, Aurora는 WAL을 스토리지에서 직접 사용하므로 빠른 복구 가능
- Redo Log가 Aurora 스토리지 계층에 유지되므로 복구 시간이 거의 없음

---

## Aurora와 기존 MySQL/PostgreSQL 비교

| 항목 | 기존 MySQL / PostgreSQL | AWS Aurora |
|------|----------------|------------|
| WAL 적용 방식 | 개별 인스턴스에서 WAL을 관리 | 공유 스토리지 계층에서 WAL 관리 |
| Redo Log 위치 | 개별 서버 내 저장 | Aurora 스토리지 계층에서 직접 유지 |
| Failover 속도 | WAL을 재적용해야 하므로 느림 | 스토리지에서 바로 반영되어 매우 빠름 |
| Replication 방식 | Binlog 기반, Replica가 SQL을 다시 실행 | WAL을 스토리지에서 공유하여 더 빠름 |

---

## 결론
1. WAL (Write-Ahead Logging)은 장애 복구를 위한 핵심 기술로, Aurora에서는 이를 공유 스토리지 계층에서 관리하여 고속 복구 및 실시간 복제가 가능함.
2. Aurora의 WAL은 일반적인 MySQL/PostgreSQL보다 성능이 뛰어나며 Redo Log를 중앙에서 관리하여 복구 속도를 크게 향상시킴.
3. Aurora Replication은 WAL을 활용하여 빠르게 읽기 복제를 제공하므로, 읽기 부하가 큰 환경에서 뛰어난 확장성을 제공함.
4. 기존 RDS보다 Aurora의 복구 및 장애 대응이 더 빠르고 효율적이므로, 고가용성이 필요한 환경에서는 Aurora가 강력한 선택지가 될 수 있음.

Aurora의 WAL 및 로그 시스템은 단순한 DB 복제 수준이 아니라, 고가용성 및 빠른 복구를 위한 최적화된 구조로 설계됨

