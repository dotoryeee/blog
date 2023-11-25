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
MSA 환경에서는 각 서비스별 DB가 분리되어 있어 트랜잭션 유지가 어렵다. 특히, A서비스의 DB가 업데이트되고 B서비스에 메시지를 전달해야 하는 순간에 서비스 단절이 발생하면 A서비스 DB와 B서비스 DB의 형상이 유지되지 않는다. 이를 해결하기 위해, A서비스의 DB 업데이트가 발생하는 시점에 Outbox라는 별도의 테이블을 생성한다. B서비스는 A서비스의 Outbox 테이블을 구독하여, 서비스 단절 발생 시에도 동작 재개 시점에서 완료되지 않은 메시지의 존재를 파악해 트랜잭션을 재개할 수 있다. 데이터베이스 변경사항이 발생할 때, 원래 테이블 업데이트와 함께 별도의 Outbox 테이블에 업데이트 사실을 기록한다. 이 두 업데이트를 하나의 트랜잭션으로 묶어 처리하여, 시스템 에러에도 불구하고 Outbox 테이블에 업데이트 사실이 반드시 기록될 수 있도록 함으로써, 최소 1회 전송 보장되는 큐의 효과를 낼 수 있다.

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

## SideCar
```mermaid
graph LR
    subgraph " "
        sidecar[사이드카]
        microservice[마이크로서비스]
    end
    external[외부 API]

    microservice -- "1. 사이드카에 요청 전송" --> sidecar
    sidecar -- "2. 외부 서비스에 요청 전달" --> external
    external -- "3. 사이드카에 응답 반환" --> sidecar
    sidecar -- "4. 마이크로서비스에 응답 반환" --> microservice

```
각 마이크로서비스의 옆에 '사이드카'라 불리는 보조 컴포넌트를 함께 배치한다. 이 사이드카 컴포넌트는 해당 마이크로서비스만을 위한 기능을 수행하고 마이크로서비스와 함께 생성되고 소멸한다. 사이드카는 마이크로서비스와 동일한 컨테이너나 Pod 내에서 실행되는 것이 일반적이다.

사이드카 패턴이 적용되는 예시

- 네트워크 트래픽 관리 및 프록시 기능
- 로깅과 모니터링
- 보안 관련 작업 (예: TLS 종료)
- 마이크로서비스의 설정이나 리소스 관리

## Ambassador
```mermaid
graph LR
    A[애플리케이션] -->|1. 연결 요청| B[앰배서더]
    B -->|2. 외부 시스템과의 연결 관리| C[외부 시스템]

    subgraph 외부 시스템
    C1[데이터베이스]
    C2[캐시 시스템]
    C3[메시지 큐]
    end

    C --> C1
    C --> C2
    C --> C3

```
'앰배서더' 컴포넌트가 마이크로서비스와 외부 시스템(예: 데이터베이스, 외부 API)과의 인터페이스 역할을 수행한다. 앰배서더는 마이크로서비스의 네트워크 요청을 중계하고 외부 시스템과의 통신을 단순화한다. 앰배서더 패턴은 보통 외부 리소스에 대한 액세스를 중앙화하고, 외부 리소스에 대한 요청을 보내기 위한 통합 엔드포인트를 제공하는 데 사용한다.

앰배서더 패턴을 사용하는 예시: 

- Service Discovery
- Request Routing
- Load Balancing
- Circuit Breaker pattern

### Sidecar 패턴과 Ambassador 패턴 차이점
| 기준        | 사이드카 패턴                                            | 앰배서더 패턴                                                 |
|-----------|--------------------------------------------------------|------------------------------------------------------------|
| 적용 범위    | 특정 마이크로서비스에 국한되며, 해당 서비스의 생명주기를 따름       | 하나 이상의 마이크로서비스에 공통적으로 사용되며, 외부 시스템의 인터페이스 역할 |
| 주요 목적    | 마이크로서비스의 부수적 기능(로깅, 모니터링 등) 처리                 | 외부 시스템(데이터베이스, 외부 API 등)과의 통신 중계 및 관리             |
| 실행 위치    | 마이크로서비스와 동일한 환경(컨테이너 또는 Pod) 내 실행              | 외부 시스템에 가깝게 위치하거나 마이크로서비스와 같은 환경에서 실행 가능      |
| 기능적 역할 | 네트워킹, 보안, 리소스 관리 등 마이크로서비스를 직접 지원하는 기능들 | 서비스 디스커버리, 로드 밸런싱, 요청 라우팅 등 외부 서비스와의 연결을 관리 |


## Anti-Corruption Layer(ACL)
```mermaid
graph LR
    A[새 시스템] -->|1. 요청| B[ACL]
    B[ACL] -->|2. 변환| C[레거시 시스템]
    C[레거시 시스템] -->|3. 응답| B[ACL]
    B[ACL] -->|4. 변환| A[새 시스템]

    style B fill:#f9f,stroke:#333,stroke-width:4px

```
빅뱅이 아닌 분할정복 전략으로 새 시스템을 구축하는 경우 새 시스템에 레거시 시스템과 통신을 위한 "옛날"기술을 굳이 탑재하여 새 시스템을 "오염"시키고싶지 않다. 이때 ACL이라는 중간 Layer를 삽입하여 레거시와 새 시스템의 호환성을 유지해주다가 레거시를 밀어버릴때 ACL도 같이 밀어버리면 깔끔하다.


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