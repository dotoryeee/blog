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



### Sequence
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
## Choreography
## Map Reduce
## Saga
## Transactional Outbox
## Materialized View
## CQRS
## CQRS + Materialized View
## SideCar & Ambassador
## Anti-Corruption Adaptor
## BFF(Backend For Frontend)
## Throttling and Rate Limiting
## Retry
## Circuit Braker
## DLQ(Dead Letter Queue)
## Rolling Deployment
## Blue-Green Deployment
## Canary Release, A/B test deployment
## Chaos Engineering