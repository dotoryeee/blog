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
---
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

입력으로부터 결과물을 산출해내는 과정에 여러 처리 과정들이 포함되는 개념. 데이터 핸들링의 ETL이나 로그수집의 ELK스택의 Logstash에서 많이 본 패턴이고 강의에서는 콘텐츠 provider가 제공한 video source를 다양한 format과 resolution으로 인코딩 후 chunk를 분리하여 고객의 네트워크 회선 상태에 따라 적합한 resolution의 video를 제공하는 예시를 알려준다.
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
### Flow Graph
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
### Sequence Diagram
```mermaid
sequenceDiagram
    participant orc as Orchestrator
    participant 작업1 as Task 1
    participant 작업2 as Task 2
    participant 작업3 as Task 3
    participant r as Final Result

    orc->>+작업1: Start
    작업1-->>-orc: Complete
    orc->>+작업2: Start
    작업2-->>-orc: Complete
    orc->>+작업3: Start
    작업3-->>-orc: Complete
    orc->>r: Return Result
```
Orchestrator가 모든 Task의 입력/출력 등 동작을 동기식으로 관리한다. 따라서 Coupling(결합도)가 높다.<br>
대표적인 예시: Kubernetes

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
Orchestrator는 동기식이지만 Choreography 패턴은 Event Hub(MQ, Kafka등)에 메시지를 발행하는 방식으로 비동기식이며 이벤트 발생에 따라 자동으로 반응하는 분산형 아키텍처를 허용한다. 따라서 Coupling(결합도)가 낮아 확장성과 유연셩이 높지만 복잡하다.<br>
특히 이슈 발생 시 대응이 매우매우 어렵다고 한다.(어디가 문제가 발생했는지 추적하기가 매우 어렵다)

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
### Sequence Diagram (Hadoop EcoSystem)
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
### Flow Graph
```mermaid
graph TB
    서비스(Service) -->|데이터 변경| DB트랜잭션{DB Transaction}
    DB트랜잭션 --> 데이터베이스(Database)
    DB트랜잭션 --> 아웃박스(Outbox)
    아웃박스 -->|이벤트 전파| 이벤트프로세서(Event Processor)
    이벤트프로세서 -->|이벤트 전송| 메시지브로커(Message Broker)

    style 서비스 fill:#f9f,stroke:#333,stroke-width:2px
    style DB트랜잭션 fill:#ff9,stroke:#333,stroke-width:2px
    style 데이터베이스 fill:#f96,stroke:#333,stroke-width:2px
    style 아웃박스 fill:#9cf,stroke:#333,stroke-width:2px
    style 이벤트프로세서 fill:#bbf,stroke:#333,stroke-width:2px
    style 메시지브로커 fill:#9f9,stroke:#333,stroke-width:2px
```
### Sequence Diagram
``` mermaid
sequenceDiagram
    participant 서비스 as Service
    participant DB트랜잭션 as DB Transaction
    participant 데이터베이스 as Database
    participant 아웃박스 as Outbox
    participant 이벤트프로세서 as Event Processor
    participant 메시지브로커 as Message Broker

    서비스->>DB트랜잭션: 데이터 변경 시작
    DB트랜잭션->>데이터베이스: 데이터 변경
    DB트랜잭션->>아웃박스: 이벤트 기록
    Note right of 아웃박스: 변경 사항과 이벤트는 같은 트랜잭션 내 기록
    DB트랜잭션->>서비스: 변경 완료
    loop 이벤트 폴링
        이벤트프로세서->>아웃박스: 새 이벤트 확인
    end
    아웃박스-->>이벤트프로세서: 새 이벤트
    이벤트프로세서->>메시지브로커: 이벤트 전송
```

Database 변경사항 발생 시 원래 Table 업데이트 뿐만 아니라 별개의 "outbox" table생성 후 Table update가 발생했음을 기록하여 다른 서비스에서 Database가 변경했음을 알 수 있게 한다. 이때 원래 Target table과 Outbox table의 업데이트를 하나의 트랜잭션으로 묶어 처리하는 것을 통해 Target Table의 업데이트가 발생했다는 정보는 시스템 에러와 무관라게 "반드시" Outbox테이블에 기록될 수 있으므로 "최소 1회 전송 보장"된 Queue를 사용하는 효과를 가진다.

## Materialized View
```mermaid
graph LR
    데이터소스(DataSource) -->|변경 데이터 감지| 변경감지기(Change Detector)
    변경감지기 --> |변경 데이터 읽기| 뷰업데이터(View Updater)
    뷰업데이터 --> |뷰 갱신| 구체화된뷰(Materialized View)

    style 데이터소스 fill:#f9f,stroke:#333,stroke-width:2px
    style 변경감지기 fill:#f96,stroke:#333,stroke-width:2px
    style 뷰업데이터 fill:#ff9,stroke:#333,stroke-width:2px
    style 구체화된뷰 fill:#9cf,stroke:#333,stroke-width:2px

```

- 미리 계산된 데이터의 스냅샷을 제공한다. 쓰기 작업의 결과로 발생하는 이벤트에 의해 업데이트되며 데이터 조회가 빨라져 읽기 작업이 많은 시스템에서 유리하다.
- Materialized View는 복잡한 조인이나 계산을 필요로 하는 쿼리에 대해 더 빠른 읽기 성능을 제공할 수 있다.

## CQRS
```mermaid
graph TB
    커맨드(Command) --> |"쓰기 작업"| 커맨드핸들러(Command Handler)
    커맨드핸들러 --> |"이벤트 생성"| 이벤트스토어(Event Store)
    이벤트스토어 --> |"이벤트 발행"| 프로젝션(Projection)
    프로젝션 --> |"읽기 모델 업데이트"| 읽기모델(Read Model)
    쿼리(Query) --> |"읽기 작업"| 쿼리핸들러(Query Handler)
    쿼리핸들러 --> 읽기모델

    style 커맨드 fill:#f96,stroke:#333,stroke-width:2px
    style 커맨드핸들러 fill:#ff9,stroke:#333,stroke-width:2px
    style 이벤트스토어 fill:#9cf,stroke:#333,stroke-width:2px
    style 프로젝션 fill:#f9f,stroke:#333,stroke-width:2px
    style 읽기모델 fill:#9f9,stroke:#333,stroke-width:2px
    style 쿼리 fill:#f96,stroke:#333,stroke-width:2px
    style 쿼리핸들러 fill:#ff9,stroke:#333,stroke-width:2px

```

- 시스템의 '쓰기(Command)'와 '읽기(Query)'를 명확히 분리하여 복잡한 도메인 로직이나 비즈니스 규칙을 갖는 시스템에서 성능과 확장성을 향상시키기 위해 사용한다.
- 쓰기 모델(Command Model): 커맨드를 통해 상태 변경 작업을 수행한다. 비즈니스 로직과 유효성 검사가 여기에 포함
- 읽기 모델(Query Model): 쿼리를 통해 데이터를 조회한다. 높은 조회 성능을 제공하기 위해 별도로 설계할 수 있다. 변경 사항은 이벤트 소싱을 통해 읽기 모델에 반영한다.
- 단점: Eventual Consistency만 적용 가능하다

## CQRS + Materialized View
```mermaid
graph TB
    커맨드(Command) --> |"쓰기 작업"| 커맨드모델(Command Model)
    커맨드모델 --> |"변경 이벤트"| 이벤트핸들러(Event Handler)
    이벤트핸들러 --> |"이벤트에 의한 뷰 갱신"| 구체화된뷰(Materialized View)
    쿼리(Query) --> |"읽기 작업"| 구체화된뷰

    style 커맨드 fill:#f96,stroke:#333,stroke-width:2px
    style 커맨드모델 fill:#ff9,stroke:#333,stroke-width:2px
    style 이벤트핸들러 fill:#9cf,stroke:#333,stroke-width:2px
    style 구체화된뷰 fill:#9f9,stroke:#333,stroke-width:2px
    style 쿼리 fill:#f96,stroke:#333,stroke-width:2px

```

- CQRS에 Materialized View를 추가하면, 읽기 모델의 데이터가 미리 계산되고 저장되어, 조회 요청에 대한 응답이 빨라진다.
- 읽기 성능: Materialized View는 미리 계산된 결과를 저장하여 읽기 작업이 빠르다.
- 데이터 동기화: Materialized View를 사용하면 쓰기 작업 후 읽기 모델의 데이터를 업데이트하는 과정이 필요하다.
- 복잡성: Materialized View를 도입하면 데이터 일관성을 관리하는 추가적인 복잡성이 발생한다.
- 스케일링: CQRS 자체는 읽기와 쓰기 작업의 분리를 통한 스케일링을 가능하게 하지만, Materialized View는 읽기 성능을 향상시키는 데  중점을 둔다.
- 결론: CQRS+Materialized View 구조는 CQRS만 사용할 때보다 더 빠른 읽기 작업을 위해 설계된 구조이다.
- 단점: CQRS특성 상 Eventual Consistency만 적용 가능하다

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