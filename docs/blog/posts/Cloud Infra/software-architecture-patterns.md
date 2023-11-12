---
draft: true
date: 2023-11-12
authors:
  - dotoryeee
categories:
  - AA
  - udemy
  - study
---
# Software Architecture Patterns 정리
!!! Warning ""
    [Udemy "The Complete Cloud Computing Software Architecture Patterns" 강의](https://www.udemy.com/course/the-complete-cloud-computing-software-architecture-patterns/)를 듣고 복습을 위해 정리하였음

    ```md linenums="1"
    Pipes and Filters
    Scatter Gather
    Execution Orchestrator
    Choreography
    Map Reduce
    Saga
    Transactional Outbox
    Materialized View
    CQRS
    CQRS + Materialized View
    SideCar & Ambassador
    Anti-Corruption Adaptor
    BFF(Backend For Frontend)
    Throttling and Rate Limiting
    Retry
    Circuit Braker
    DLQ(Dead Letter Queue)
    Rolling Deployment
    Blue-Green Deployment
    Canary Release, A/B test deployment
    Chaos Engineering
    ```

<!-- more -->

## Pipes and Filters
``` mermaid
graph LR
    사용자(User) --> 백엔드서비스(Backend Service)
    백엔드서비스 --> 필터1(Filter 1)
    필터1 --> 큐1(Queue 1)
    큐1 --> 필터2(Filter 2)
    필터2 --> 큐2(Queue 2)
    큐2 --> 필터3(Filter 3)
    필터3 --> 데이터베이스(Database)

    style 백엔드서비스 fill:#f9f,stroke:#333,stroke-width:2px
    style 필터1 fill:#ff9,stroke:#333,stroke-width:2px
    style 필터2 fill:#ff9,stroke:#333,stroke-width:2px
    style 필터3 fill:#ff9,stroke:#333,stroke-width:2px
    style 큐1 fill:#9cf,stroke:#333,stroke-width:2px
    style 큐2 fill:#9cf,stroke:#333,stroke-width:2px
    style 데이터베이스 fill:#f96,stroke:#333,stroke-width:2px

```

입력으로부터 결과물을 산출해내는 과정에 여러 처리 과정들이 포함되는 개념.<br> 데이터 핸들링의 ETL이나 로그수집의 ELK스택의 Logstash에서 많이 본 패턴이고 강의에서는 콘텐츠 provider가 제공한 video source를 다양한 format과 resolution으로 인코딩 후 chunk를 분리하여 고객의 네트워크 회선 상태에 따라 적합한 resolution의 video를 제공하는 예시를 알려준다.
## Scatter Gather
### Flow Graph
``` mermaid
graph LR
    사용자(사용자) --> |"쿼리 요청"| 마스터노드(Master Node)
    마스터노드 --> |"쿼리 분산"| 워커노드1(Worker Node 1)
    마스터노드 --> |"쿼리 분산"| 워커노드2(Worker Node 2)
    마스터노드 --> |"쿼리 분산"| 워커노드N(Worker Node N)
    워커노드1 --> |"데이터 찾음"| 결과결합(Result Aggregation)
    워커노드2 --> |"데이터 찾음"| 결과결합
    워커노드N --> |"데이터 찾음"| 결과결합
    결과결합 --> |"최종 결과"| 사용자

    style 사용자 fill:#f9f,stroke:#333,stroke-width:4px
    style 마스터노드 fill:#bbf,stroke:#f66,stroke-width:2px,stroke-dasharray: 5, 5
    style 워커노드1 fill:#bfb,stroke:#f66,stroke-width:2px,stroke-dasharray: 5, 5
    style 워커노드2 fill:#bfb,stroke:#f66,stroke-width:2px,stroke-dasharray: 5, 5
    style 워커노드N fill:#bfb,stroke:#f66,stroke-width:2px,stroke-dasharray: 5, 5
    style 결과결합 fill:#ff6,stroke:#333,stroke-width:2px
```



### Sequence Diagram
``` mermaid 
sequenceDiagram
    participant 사용자
    participant 마스터노드
    participant 워커노드1
    participant 워커노드2
    participant 워커노드N

    사용자->>+마스터노드: 쿼리 요청
    마스터노드->>+워커노드1: 샤드 1에 쿼리
    마스터노드->>+워커노드2: 샤드 2에 쿼리
    마스터노드->>+워커노드N: 샤드 N에 쿼리
    Note right of 워커노드N: 데이터를 찾는다
    워커노드1-->>-마스터노드: 결과 반환
    워커노드2-->>-마스터노드: 결과 반환
    워커노드N-->>-마스터노드: 결과 반환
    마스터노드->>+사용자: 최종 결과 반환
```
## Execution Orchestrator
```mermaid
graph LR
    orc(Orchestrator) --> 작업1(Task 1)
    작업1 --> orc
    orc --> 작업2(Task 2)
    작업2 --> orc
    orc --> 작업3(Task 3)
    작업3 --> orc
    orc --> |"결과 반환"| r(Final Result)

    style orc fill:#46bdc6,stroke:#333,stroke-width:2px
    style 작업1 fill:#f9f9c8,stroke:#333,stroke-width:2px
    style 작업2 fill:#f9f9c8,stroke:#333,stroke-width:2px
    style 작업3 fill:#f9f9c8,stroke:#333,stroke-width:2px
    style r fill:#ff9f9b,stroke:#333,stroke-width:2px

```
## Choreography
```mermaid
graph LR
    서비스A(Service A) --> |"이벤트 A 발행"| 이벤트허브(Event Hub)
    이벤트허브 --> |"이벤트 A 구독"| 서비스B(Service B)
    서비스B --> |"이벤트 B 발행"| 이벤트허브
    이벤트허브 --> |"이벤트 B 구독"| 서비스C(Service C)
    서비스C --> |"이벤트 C 발행"| 이벤트허브
    이벤트허브 --> |"이벤트 C 구독"| 서비스D(Service D)

    style 서비스A fill:#ff8c00,stroke:#333,stroke-width:2px
    style 서비스B fill:#6a5acd,stroke:#333,stroke-width:2px
    style 서비스C fill:#32cd32,stroke:#333,stroke-width:2px
    style 서비스D fill:#20b2aa,stroke:#333,stroke-width:2px
    style 이벤트허브 fill:#ffdead,stroke:#333,stroke-width:2px

```
## Map Reduce
### Flow Graph
```mermaid
graph TD
    데이터셋(Data Set) --> |"매핑"| 매퍼1(Map 1)
    데이터셋 --> |"매핑"| 매퍼2(Map 2)
    데이터셋 --> |"매핑"| 매퍼N(Map N)
    매퍼1 --> |"키-값 쌍"| 리듀서1(Reduce 1)
    매퍼2 --> |"키-값 쌍"| 리듀서2(Reduce 2)
    매퍼N --> |"키-값 쌍"| 리듀서N(Reduce N)
    리듀서1 --> |"결과 집합"| 최종결과1(Final Result 1)
    리듀서2 --> |"결과 집합"| 최종결과2(Final Result 2)
    리듀서N --> |"결과 집합"| 최종결과N(Final Result N)

    style 데이터셋 fill:#f96,stroke:#333,stroke-width:2px
    style 매퍼1 fill:#ff8c00,stroke:#333,stroke-width:2px
    style 매퍼2 fill:#ff8c00,stroke:#333,stroke-width:2px
    style 매퍼N fill:#ff8c00,stroke:#333,stroke-width:2px
    style 리듀서1 fill:#6a5acd,stroke:#333,stroke-width:2px
    style 리듀서2 fill:#6a5acd,stroke:#333,stroke-width:2px
    style 리듀서N fill:#6a5acd,stroke:#333,stroke-width:2px
    style 최종결과1 fill:#32cd32,stroke:#333,stroke-width:2px
    style 최종결과2 fill:#32cd32,stroke:#333,stroke-width:2px
    style 최종결과N fill:#32cd32,stroke:#333,stroke-width:2px

```
### Sequence Diagram
``` mermaid
sequenceDiagram
    participant Client as Client
    participant HDFS as Hadoop Distributed File System (HDFS)
    participant Map as Map Tasks
    participant Shuffle as Shuffle and Sort
    participant Reduce as Reduce Tasks

    Client->>+HDFS: Input Data Upload
    HDFS->>+Map: Distribute Data
    Map-->>-Shuffle: Emit Key-Value Pairs
    Shuffle->>+Reduce: Group by Key
    Reduce-->>-HDFS: Write Output

```

## Saga
```mermaid
graph TB
    시작(Start) --> 트랜잭션1(Transaction 1)
    트랜잭션1 --> |"이벤트 A 성공"| 트랜잭션2(Transaction 2)
    트랜잭션1 --> |"이벤트 A 실패"| 컴펜세이션1(Compensation 1)
    트랜잭션2 --> |"이벤트 B 성공"| 트랜잭션3(Transaction 3)
    트랜잭션2 --> |"이벤트 B 실패"| 컴펜세이션2(Compensation 2)
    트랜잭션3 --> |"이벤트 C 성공"| 트랜잭션4(Transaction 4)
    트랜잭션3 --> |"이벤트 C 실패"| 컴펜세이션3(Compensation 3)
    트랜잭션4 --> |"이벤트 D 성공"| 최종결과(Final Result)
    트랜잭션4 --> |"이벤트 D 실패"| 컴펜세이션4(Compensation 4)
    컴펜세이션4 --> 컴펜세이션3
    컴펜세이션3 --> 컴펜세이션2
    컴펜세이션2 --> 컴펜세이션1
    컴펜세이션1 --> 끝(End)

    style 시작 fill:#f9f,stroke:#333,stroke-width:2px
    style 트랜잭션1 fill:#ff9,stroke:#333,stroke-width:2px
    style 트랜잭션2 fill:#ff9,stroke:#333,stroke-width:2px
    style 트랜잭션3 fill:#ff9,stroke:#333,stroke-width:2px
    style 트랜잭션4 fill:#ff9,stroke:#333,stroke-width:2px
    style 최종결과 fill:#9cf,stroke:#333,stroke-width:2px
    style 컴펜세이션1 fill:#f99,stroke:#333,stroke-width:2px
    style 컴펜세이션2 fill:#f99,stroke:#333,stroke-width:2px
    style 컴펜세이션3 fill:#f99,stroke:#333,stroke-width:2px
    style 컴펜세이션4 fill:#f99,stroke:#333,stroke-width:2px
    style 끝 fill:#f9f,stroke:#333,stroke-width:2px

```
## Transactional Outbox
```mermaid
graph LR
    서비스 --> |"데이터 변경"| 데이터베이스
    데이터베이스 --> |"변경 이벤트 기록"| 아웃박스
    아웃박스 --> |"이벤트 전파"| 이벤트프로세서
    이벤트프로세서 --> |"이벤트 전송"| 메시지브로커

```
## Materialized View
```mermaid
graph LR
    데이터소스 --> |"변경 데이터 읽기"| 뷰업데이터
    뷰업데이터 --> |"뷰 갱신"| MaterializedView

```
## CQRS
```mermaid
graph LR
    커맨드 --> |"쓰기 작업"| 쓰기모델
    쿼리 --> |"읽기 작업"| 읽기모델

```
## CQRS + Materialized View
```mermaid
graph LR
    커맨드 --> |"쓰기 작업"| 쓰기모델
    쓰기모델 --> |"변경 이벤트"| 이벤트핸들러
    이벤트핸들러 --> |"뷰 갱신"| MaterializedView
    쿼리 --> |"읽기 작업"| MaterializedView

```
## SideCar & Ambassador
```mermaid

```
## Anti-Corruption Adaptor
```mermaid

```
## BFF(Backend For Frontend)
```mermaid

```
## Throttling and Rate Limiting
```mermaid

```
## Retry
```mermaid

```
## Circuit Braker
```mermaid

```
## DLQ(Dead Letter Queue)
```mermaid

```
## Rolling Deployment
```mermaid

```
## Blue-Green Deployment
```mermaid

```
## Canary Release, A/B test deployment
```mermaid

```
## Chaos Engineering
```mermaid

```