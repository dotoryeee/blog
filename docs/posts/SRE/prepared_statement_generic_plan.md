---
draft: false
date: 2026-10-14
authors:
  - dotoryeee
categories:
  - Database
tags:
  - PostgreSQL
  - Prepared Statement
  - plan_cache_mode
  - asyncpg
  - SQLAlchemy
  - Performance
  - Troubleshooting
description: "PostgreSQL plan_cache_mode 정리. 준비된 문장이 6번째 실행부터 범용 계획으로 바뀌는 규칙과 드라이버 문장 캐시가 이 규칙을 부르는 과정, 로컬 테스트에서 0.17초 안팎이던 쿼리가 2초대로 느려진 사례와 재현 SQL, SET LOCAL 해결과 트레이드오프를 DB 입문자 눈높이로 다룸"
hide:
  - toc
---

# plan_cache_mode 정리

PostgreSQL 준비된 문장(Prepared Statement)과 드라이버 문장 캐시

<!-- more -->

클라우드 비용 분석 서비스에서 같은 조회를 같은 값으로 반복했더니 6번째부터 10배 넘게 느려졌음. 원인은 PostgreSQL이 같은 쿼리를 여러 번 받으면 6번째부터 실행 계획을 바꿔 쓰는 규칙이었고, 이 규칙을 조절하는 설정이 `plan_cache_mode`. 해결은 그 쿼리의 트랜잭션에만 `SET LOCAL plan_cache_mode = force_custom_plan`을 거는 것

문제의 쿼리는 그룹 ID와 기간을 파라미터로 받아 항목별 합계, 소계, 총계를 한 번에 계산하는 피벗 집계 쿼리. 파라미터는 쿼리를 실행할 때마다 바꿔 넣는 입력값이고, 여러 기준의 합계를 쿼리 한 번으로 내는 데는 SQL의 GROUPING SETS 문법을 씀. 로컬 테스트 환경에서 같은 값으로 20회 연속 실행한 결과

| 실행 순서 | 응답 시간 |
|---|---|
| 1~5번째 | 0.16~0.18초 |
| 6~20번째 | 2.2~2.5초(p95 2.45초) |

- p95는 측정값을 빠른 순으로 늘어놓았을 때 95% 지점의 값. 느린 쪽 끝을 보는 지표
- 측정 환경은 로컬 PC의 Docker 컨테이너로 띄운 PostgreSQL 16과 약 120만 행 시드 데이터. 이 글의 사내 수치는 모두 운영이 아니라 이 로컬 테스트 환경의 측정값
- 쿼리 문장, 파라미터 값, 데이터 모두 그대로. 바뀐 것은 실행 횟수뿐
- 같은 쿼리를 반복하면 보통 데이터가 메모리에 올라와 점점 빨라짐. 이번에는 반대로 느려졌고 그 시점이 정확히 6번째라 우연으로 보기 어려움
- 같은 로컬 환경에서 SQL 문장이 늘 같은 건수 확인용 `count(*)` 쿼리도 0.10초에서 6번째부터 1.5초로 느려짐

처음 떠올리기 쉬운 설명은 둘 다 틀렸음

| 흔한 오해 | 실제 |
|---|---|
| 무거운 쿼리를 반복하면 DB가 벌점을 주거나 OS nice 값처럼 우선순위를 낮춤 | PostgreSQL에는 쿼리별 벌점이나 우선순위 강등 장치가 없음. 같은 쿼리가 6번째부터 다른 계획으로 실행된 것 |
| 통계가 낡은 탓이니 `ANALYZE`를 다시 돌리면 풀림 | 데이터와 통계는 그대로. `ANALYZE`를 돌려도 PostgreSQL이 세어 둔 실행 횟수와 비교 기준이 남아 같은 계획이 다시 선택되기 쉬움 |

---

원인을 이해하려면 PostgreSQL이 쿼리를 처리하는 순서부터 알아야 함. PostgreSQL은 쿼리를 받으면 바로 데이터를 읽지 않고 어떤 방법으로 읽을지부터 정함. 이렇게 정한 읽기 방법을 실행 계획이라 하고, 계획을 세우는 부분을 플래너라고 부름

같은 결과를 얻는 방법은 여러 가지

| 읽는 방법 | 하는 일 | 유리한 경우 |
|---|---|---|
| 순차 읽기(Seq Scan) | 테이블을 처음부터 끝까지 전부 읽음 | 테이블 대부분을 읽어야 할 때 |
| 인덱스 스캔(Index Scan) | 인덱스로 조건에 맞는 행 위치를 찾아 그 행만 읽음 | 조건에 맞는 행이 적을 때 |

- 인덱스는 책 뒤의 찾아보기처럼 값으로 행 위치를 바로 찾게 해 주는 자료 구조. 찾을 행이 적으면 빠르지만 많은 행을 하나씩 찾아가면 전부 읽는 것보다 느려질 수 있음
- 플래너는 후보 계획마다 몇 행을 읽게 될지 어림해 예상 비용을 매기고 가장 낮은 계획을 고름. 예상 비용은 시간이 아니라 상대 점수
- 어림의 재료는 통계. PostgreSQL이 테이블 일부를 표본으로 읽어 행 수, 값 종류 수, 값 분포를 요약해 둔 것이고 자동으로, 또는 `ANALYZE` 명령으로 갱신됨
- 어림이 크게 틀리면 플래너가 느린 계획을 고를 수 있음. 이 글의 문제도 결국 어림이 틀린 이야기

---

앱은 보통 SQL에 값을 직접 써 넣지 않고 `$1`, `$2` 같은 자리 표시만 남긴 쿼리와 값을 따로 보냄. 준비된 문장은 이런 쿼리를 서버에 미리 등록해 두고 값만 바꿔 여러 번 실행하는 방식. 쿼리를 해석하는 일을 한 번만 하면 되므로 같은 쿼리를 자주 부르는 앱에 유리함. SQL로 직접 쓸 때는 `PREPARE`로 등록하고 `EXECUTE`로 실행함

- 등록된 문장은 그 연결 안에서만 살아 있음. 연결은 앱과 DB 사이에 열어 둔 통신 통로이고 연결이 끊기면 그 안의 준비된 문장도 사라짐
- 앱 코드에 `PREPARE`가 없어도 드라이버가 알아서 씀. 드라이버는 앱이 DB와 통신하게 해 주는 라이브러리이고 파이썬에서는 asyncpg가 그 역할을 맡음. SQLAlchemy는 그 위에서 쿼리를 다루기 쉽게 해 주는 라이브러리이며 실제 통신은 asyncpg에 맡김
- 드라이버는 준비한 문장을 연결마다 기억해 두고 같은 SQL이 다시 오면 재사용함. 이 저장 공간이 드라이버 문장 캐시
- 드라이버와 서버 사이의 통신은 확장 쿼리 프로토콜을 씀. SQL 준비, 값 연결, 실행을 Parse, Bind, Execute 메시지 세 개로 나눠 보내는 PostgreSQL 통신 방식

```mermaid
flowchart TD
    A[앱 코드<br/>같은 조회 함수를 반복 호출] --> B[SQLAlchemy<br/>준비된 문장을 연결마다 캐시]
    B --> C[asyncpg<br/>PostgreSQL과 실제 통신]
    C --> D[PostgreSQL 연결<br/>같은 준비된 문장의 실행 횟수가 쌓임]
```

| 레이어 | 설정 | 기본값 | 하는 일 |
|---|---|---|---|
| [asyncpg](https://magicstack.github.io/asyncpg/current/api/index.html) | `statement_cache_size` | 100 | asyncpg를 직접 쓸 때의 드라이버 문장 캐시. 연결마다 문장을 100개까지 기억하고, 꽉 차면 가장 오래 안 쓴 문장부터 버림(LRU 방식). 항목은 만들어진 지 300초(`max_cached_statement_lifetime` 기본값)가 지나면 버려지고 다시 준비됨 |
| [SQLAlchemy](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html#prepared-statement-cache) asyncpg 방언 | `prepared_statement_cache_size` | 100 | 방언(dialect)은 SQLAlchemy가 드라이버별 차이를 맞추는 모듈. 모든 문장을 asyncpg의 `prepare()`로 준비하고 연결마다 따로 캐시. asyncpg 자체 캐시 대신 이 캐시를 씀 |

- 앱은 같은 함수를 부를 뿐인데 PostgreSQL 쪽에서는 같은 준비된 문장의 실행 횟수가 1, 2, 3으로 쌓여 6번째에 도달함
- 횟수는 연결마다, 문장마다 따로 셈. 커넥션 풀은 연결을 매번 새로 맺는 대신 미리 여러 개 열어 두고 돌려 쓰는 장치인데, 연결마다 6번째가 따로 오므로 느려지는 시점이 들쭉날쭉하게 보일 수 있음
- asyncpg 풀은 연결을 돌려받을 때 연결에 걸어 둔 설정을 되돌리지만 준비된 문장은 지우지 않음. 다시 빌린 연결에서도 횟수가 이어짐

---

준비된 문장은 같은 쿼리를 여러 번 실행하므로 실행 계획을 세우는 방법을 고를 수 있음. 방법은 두 가지

| 항목 | 맞춤 계획(custom plan) | 범용 계획(generic plan) |
|---|---|---|
| 계획에 쓰는 값 | 이번 실행에 들어온 실제 값 | 값 없이 `$1`, `$2` 같은 자리 표시 그대로 |
| 계획 시점 | 실행할 때마다 새로 | 한 번 세워 같은 연결에서 재사용 |
| 계획 수립 시간 | 실행마다 듦 | 처음 한 번만 |
| 잘 맞는 쿼리 | 값에 따라 읽을 양이 크게 달라지는 쿼리 | 어떤 값이 와도 읽을 양이 비슷한 쿼리 |
| EXPLAIN 표기 | `group_id = 200`처럼 실제 값 | `group_id = $1`처럼 자리 표시 |

범용 계획은 내비게이션이 목적지를 모른 채 평균 거리만 가정해 경로를 미리 정해 두는 것과 비슷함. 평균에 가까운 목적지면 문제없지만 아주 먼 목적지면 크게 돌아감

`plan_cache_mode`가 기본값 `auto`일 때 파라미터가 있는 준비된 문장은 아래 순서로 둘 중 하나를 고름. [PREPARE](https://www.postgresql.org/docs/16/sql-prepare.html) 공식 문서에 적힌 동작

| 실행 순서 | 쓰는 계획 | 내용 |
|---|---|---|
| 1~5번째 | 맞춤 계획 | 매번 새로 계획하고 각 계획의 예상 비용을 기록 |
| 6번째 | 범용 계획을 처음 세워 비교 | 범용 계획의 예상 비용을 맞춤 계획 5번의 평균과 비교 |
| 6번째 이후 | 범용 계획이 이기면 계속 재사용 | 이 뒤로는 맞춤 계획을 세우지 않아 평균이 그대로이므로 판단이 거의 바뀌지 않음 |

```mermaid
flowchart TD
    A[EXECUTE 요청] --> B{plan_cache_mode}
    B -->|force_custom_plan| C[맞춤 계획<br/>실제 값으로 매번 계획]
    B -->|force_generic_plan| D[범용 계획<br/>한 번 세워 재사용]
    B -->|auto 기본값| E{맞춤 계획을<br/>5번 세웠나}
    E -->|아니오| C
    E -->|예| F{범용 계획 예상 비용이<br/>계획 수립 비용 추정치를 더한<br/>맞춤 계획 평균보다 작은가}
    F -->|예| D
    F -->|아니오| C
```

흐름도는 파라미터가 있는 문장 기준. 파라미터가 없는 문장은 `plan_cache_mode`와 상관없이 처음부터 범용 계획을 씀

- 판단 근거는 예상 비용 점수. 실제로 몇 초 걸렸는지는 보지 않음
- 범용 계획이 실제로 느려도 되돌리는 장치가 없음. 통계가 갱신되거나 테이블 구조가 바뀌어 계획이 무효화되기 전까지는 같은 계획을 계속 씀
- 무효화되면 범용 계획을 다시 세워 그 점수로 다시 비교함. 다만 실행 횟수와 맞춤 계획 평균은 초기화되지 않음
- 문서에는 범용 계획이 "크게 비싸지 않으면" 쓴다고 적혀 있음. 소스 코드를 보면 맞춤 계획은 매번 계획을 새로 세우는 수고가 드니 그 몫을 점수에 조금 얹어 비교하는 방식. 테이블 하나짜리 단순 쿼리면 기본 설정에서 5.0점
- 6번째에 범용 계획이 지면 맞춤 계획을 계속 쓰고 실행할 때마다 다시 비교함
- 실행 횟수는 값과 무관하게 셈. 사내 쿼리를 로컬에서 다시 잴 때 작은 그룹으로 5번 실행한 뒤 큰 그룹을 처음 조회해도 바로 범용 계획이 쓰였음. 범용 계획이 이길지는 처음 5번에 들어온 값들의 맞춤 계획 점수 평균에 따라 달라짐
- 같은 문서는 범용 계획의 예상 비용이 크게 틀릴 때 `force_custom_plan`을 쓰라고 안내함

---

이 쿼리는 그룹과 기간 값에 따라 읽을 양이 크게 달라짐. 범용 계획은 이 값을 모른 채 세워지므로 어림이 틀리기 쉬운 조건

증상을 처음 본 쿼리는 계획 비교 기록이 남아 있지 않음. 계획 수준의 근거는 같은 증상을 보인 이전 버전 피벗 쿼리를 같은 로컬 환경에서 다시 잰 결과. PostgreSQL 16, 시드는 전체 1,224,000행에 그룹 2개(큰 그룹 120만 행, 대조용 작은 그룹 2.4만 행). 같은 연결, 같은 값으로 8회 실행해 1~5번째 0.18~0.21초, 6번째부터 2.5~2.7초(약 14배). `pg_prepared_statements`의 `custom_plans`가 5에서 멈추고 6번째부터 `generic_plans`가 늘어남

| 항목 | 맞춤 계획 | 범용 계획 |
|---|---|---|
| 읽는 방식 | 순차 읽기 위주의 병렬 해시 집계 | 복합 인덱스 스캔과 중첩 루프(Nested Loop). 행마다 테이블 데이터 페이지를 하나씩 읽음 |
| 예상 행 수 | 기록 없음 | 3,060 |
| 실제 행 수 | 기록 없음 | 약 120만 |
| 데이터 페이지 접근(EXPLAIN 버퍼) | 기록 없음 | 약 120만 회 |
| EXPLAIN 실행 시간 | 약 219ms | 약 3,186ms |

- 병렬 해시 집계는 여러 프로세스가 테이블을 나눠 읽고 값별로 묶어 합계를 내는 방식. 중첩 루프는 바깥쪽에서 찾은 행마다 안쪽을 한 번씩 찾아가는 방식이라 행이 많으면 느려짐
- 실행 시간 칸은 EXPLAIN ANALYZE 값이라 앱에서 잰 응답 시간과 다름
- 선택도는 조건에 맞을 것으로 보는 행의 비율. 0.005면 1,000행 중 5행
- 범용 계획의 예상 행 수 3,060은 1,224,000 × 1/2 × 0.005로 나온 값. 그룹 컬럼의 서로 다른 값이 2개라 1/2. 실제의 400분의 1 수준이라 인덱스로 조금만 읽으면 끝날 것처럼 보임
- 0.005(0.5%)는 기간 같은 범위 조건의 값을 모를 때 플래너가 쓰는 기본 선택도. 실제 기간과 상관없이 같은 추정이라 기간이 길수록 범용 계획이 실제보다 싸 보임
- 작은 그룹은 범용 계획으로도 0.016초라 문제가 드러나지 않음. 행이 많은 큰 그룹에서만 느려짐

사내 스키마는 공개할 수 없어 같은 원리를 단순한 테이블 하나로 재현함. 계획 모양은 사내 쿼리와 다르지만 범용 계획이 기본 선택도 때문에 읽을 양을 크게 낮춰 잡고 인덱스로 조금만 읽으면 되는 계획을 고르는 원리는 같음

- 1년치 일별 비용 1,204,500행, 그룹 200개
- 그룹 크기 편차가 큼. 가장 큰 그룹 206,241행, 가장 작은 그룹 1,952행
- 인덱스는 `group_id`와 `usage_date`에 하나씩

가장 작은 그룹을 1년 기간으로 조회했을 때 5번째와 6번째 실행 비교

| 항목 | 5번째(맞춤 계획) | 6번째(범용 계획) |
|---|---|---|
| 읽는 경로 | `group_id` 인덱스로 그룹의 행만 집음 | `usage_date` 인덱스로 기간 안의 행을 전부 훑음 |
| 조건 표기 | `group_id = 200`, 기간도 `'2025-01-01'::date` 같은 실제 값 | `usage_date >= $2 AND usage_date <= $3`, `group_id = $1` |
| 스캔 노드 예상 행 수 | 2,417 | 30 |
| 스캔 노드 실제 행 수 | 1,952 | 1,952 |
| 필터로 버린 행 수 | 0 | 1,202,548 |
| 예상 비용 | 5,587 | 211 |
| 실행 시간 | 1.7ms | 62.2ms |

EXPLAIN은 실행 계획을 보여 주는 명령이고 `ANALYZE`를 붙이면 실제로 실행해 실제 행 수와 시간도 보여 줌. `TIMING OFF`는 노드별 시간 측정을 꺼 측정 부하를 줄이는 옵션. 출력은 들여쓰기가 깊은 줄이 먼저 데이터를 읽어 위 줄로 넘겨 주는 구조이고, `cost=` 뒤 두 숫자 중 뒤쪽이 예상 비용, `rows`가 예상 행 수, `actual rows`가 실제 행 수. 아래 출력에서 메모리 사용량, Heap Blocks, Planning Time 줄은 생략

5번째 실행, 맞춤 계획

```text
MixedAggregate  (cost=31.16..5587.06 rows=26 width=47) (actual rows=26 loops=1)
  Hash Key: service, region
  Hash Key: service
  Group Key: ()
  ->  Bitmap Heap Scan on daily_cost  (cost=31.16..5550.48 rows=2417 width=21) (actual rows=1952 loops=1)
        Recheck Cond: (group_id = 200)
        Filter: ((usage_date >= '2025-01-01'::date) AND (usage_date <= '2025-12-31'::date))
        ->  Bitmap Index Scan on daily_cost_group_id_idx  (cost=0.00..30.55 rows=2417 width=0) (actual rows=1952 loops=1)
              Index Cond: (group_id = 200)
Execution Time: 1.663 ms
```

6번째 실행, 범용 계획

```text
MixedAggregate  (cost=0.43..210.65 rows=22 width=47) (actual rows=26 loops=1)
  Hash Key: service, region
  Hash Key: service
  Group Key: ()
  ->  Index Scan using daily_cost_usage_date_idx on daily_cost  (cost=0.43..209.92 rows=30 width=21) (actual rows=1952 loops=1)
        Index Cond: ((usage_date >= $2) AND (usage_date <= $3))
        Filter: (group_id = $1)
        Rows Removed by Filter: 1202548
Execution Time: 62.181 ms
```

범용 계획이 예상 행 수 30을 내놓은 과정

- 플래너는 `group_id = $1`의 값을 모르므로 그룹 하나를 전체의 1/200로 잡음
- `usage_date BETWEEN $2 AND $3`도 값을 모르므로 범위 조건 기본 선택도 0.005를 씀
- 1,204,500 × 1/200 × 0.005 ≈ 30
- 기간을 1년의 0.5%, 2일이 채 안 되는 기간으로 가정한 셈. `usage_date` 인덱스에서 약 6,000행(1,204,500 × 0.005)만 읽으면 된다고 봄. 데이터가 날짜순으로 쌓여 있어 이 인덱스로 읽는 비용도 싸게 잡힘
- 실제 기간은 1년 전체. 인덱스로 1년치 1,204,500행을 모두 읽고 그중 1,202,548행을 그룹 조건으로 버림

예상 비용만 보면 범용 계획이 26배 싸 보였고 실제로는 이 실행에서 37배 느렸음(반복 측정 중앙값으로는 30배 안팎). 비교 규칙이 예상 비용만 보기 때문에 범용 계획이 그대로 채택됨

값 조합을 바꿔 보면 범용 계획 하나로 모든 값을 감당할 수 없는 쿼리라는 점이 드러남. 각 조합을 `force_custom_plan`, `force_generic_plan`으로 고정하고 11회 실행해 첫 회를 뺀 10회의 중앙값

| 그룹 | 기간 | 맞춤 계획 | 범용 계획 |
|---|---|---|---|
| 작은 그룹(1,952행) | 1주 | 0.6ms | 1.2ms |
| 작은 그룹 | 1년 | 2.0ms | 58.5ms |
| 큰 그룹(206,241행) | 1주 | 2.0ms | 2.2ms |
| 큰 그룹 | 1년 | 70.3ms | 115.0ms |

- 값을 모르고 세운 계획은 그룹을 평균 크기로, 기간을 고정 기본값 0.5%로 가정함. 기간이 짧을 때는 맞춤 계획과 비슷하고 기간이 길수록 손해가 커짐
- 그룹 크기와 기간 길이 둘 다 값마다 읽을 양을 크게 바꾸는 축

사내 쿼리와 재현 테이블을 나란히 놓으면 계획 모양은 달라도 같은 원리가 보임

| 항목 | 사내 이전 버전 쿼리 | 재현 테이블 |
|---|---|---|
| 맞춤 계획 모양 | 순차 읽기 위주의 병렬 해시 집계 | 그룹 인덱스로 비트맵 스캔 |
| 범용 계획 모양 | 복합 인덱스 스캔, 중첩 루프 | 기간 인덱스 스캔, 그룹은 필터로 거름 |
| 손해가 큰 값 | 큰 그룹 | 긴 기간 |
| 느려진 배수 | 약 14배 | 약 25배(드라이버 측정)에서 37배(EXPLAIN 1회) |

- 어느 값에서 손해가 큰지는 범용 계획이 고른 모양에 따라 다름
- 공통점은 범용 계획이 기본 선택도 0.005 때문에 읽을 양을 실제보다 크게 낮춰 잡았다는 것. 사내 쿼리는 3,060행 예상에 실제 약 120만 행, 재현 테이블은 인덱스에서 약 6,000행 예상에 실제 1,204,500행
- 그 오차를 실행 시간으로 확인하는 단계가 없어서 범용 계획이 그대로 채택됨

---

직접 확인하려면 Docker로 PostgreSQL 16 컨테이너 하나를 띄우면 충분. psql은 PostgreSQL에 접속해 SQL을 직접 입력하는 명령줄 도구

```bash
docker run -d --name pg16 -e POSTGRES_PASSWORD=pg -p 5432:5432 postgres:16-alpine
docker exec -it pg16 psql -U postgres
```

그룹마다 행 수가 크게 다른 테이블을 만듦. `setseed`로 난수를 고정해 데이터는 매번 같게 나옴. `ANALYZE`가 고르는 통계 표본은 고정되지 않아 맞춤 계획의 예상 행 수와 비용은 재현할 때마다 조금씩 다를 수 있음

```sql
SELECT setseed(0.5);

CREATE TABLE daily_cost (
  usage_date date    NOT NULL,
  group_id   int     NOT NULL,
  service    text    NOT NULL,
  region     text    NOT NULL,
  cost       numeric NOT NULL
);

-- 365일 × 하루 3,300행. 그룹 번호가 클수록 행이 적음
INSERT INTO daily_cost
SELECT d::date,
       1 + floor(200 * power(random(), 3))::int,
       (ARRAY['compute','storage','network','database','analytics'])[1 + floor(random() * 5)::int],
       (ARRAY['seoul','tokyo','virginia','frankfurt'])[1 + floor(random() * 4)::int],
       round((random() * 100)::numeric, 4)
FROM generate_series('2025-01-01'::date, '2025-12-31'::date, '1 day') AS d,
     generate_series(1, 3300);

CREATE INDEX ON daily_cost (group_id);
CREATE INDEX ON daily_cost (usage_date);
VACUUM ANALYZE daily_cost;
```

준비된 문장을 만들고 같은 값으로 5회 실행

```sql
PREPARE pivot(int, date, date) AS
SELECT service, region, sum(cost) AS total
FROM daily_cost
WHERE group_id = $1 AND usage_date BETWEEN $2 AND $3
GROUP BY GROUPING SETS ((service, region), (service), ());

EXECUTE pivot(200, '2025-01-01', '2025-12-31');
EXECUTE pivot(200, '2025-01-01', '2025-12-31');
EXECUTE pivot(200, '2025-01-01', '2025-12-31');
EXECUTE pivot(200, '2025-01-01', '2025-12-31');
EXECUTE pivot(200, '2025-01-01', '2025-12-31');
```

6번째를 EXPLAIN으로 실행

```sql
EXPLAIN (ANALYZE, TIMING OFF) EXECUTE pivot(200, '2025-01-01', '2025-12-31');
```

- 계획에 `$1`, `$2`, `$3`이 보이면 범용 계획. 맞춤 계획이면 `200`, `'2025-01-01'::date`처럼 실제 값이 들어가 있음
- 계획 모양과 예상치는 앞에서 본 6번째 실행 계획과 같음
- `EXPLAIN EXECUTE`도 실행 횟수에 들어감. `ANALYZE` 없이 계획만 보는 경우도 마찬가지. 처음부터 5회 모두 `EXPLAIN (ANALYZE) EXECUTE`로 돌려도 6번째에 바뀌는 모습을 볼 수 있음

맞춤 계획과 범용 계획을 몇 번 썼는지는 `pg_prepared_statements` 뷰로 확인. 이 뷰는 조회하는 연결이 만든 문장만 보여 주므로 `EXECUTE`를 돌린 같은 psql 창에서 조회

```sql
SELECT name, generic_plans, custom_plans FROM pg_prepared_statements;
```

```text
 name  | generic_plans | custom_plans
-------+---------------+--------------
 pivot |             1 |            5
```

PostgreSQL 16부터는 `EXPLAIN (GENERIC_PLAN)`으로 준비하지 않은 쿼리의 범용 계획도 미리 볼 수 있음. 이 명령은 범용 계획의 모양만 보여 줌. 앱 연결의 문장이 지금 범용 계획을 쓰는지는 알 수 없음. 쿼리를 실제로 실행하지 않으므로 `ANALYZE`와 함께 쓰면 오류

```sql
EXPLAIN (GENERIC_PLAN)
SELECT service, region, sum(cost) AS total
FROM daily_cost
WHERE group_id = $1 AND usage_date BETWEEN $2 AND $3
GROUP BY GROUPING SETS ((service, region), (service), ());
```

드라이버로 확인하려면 asyncpg로 같은 쿼리를 여러 번 부르면 됨. 코드에는 `PREPARE`가 없음

```python
import asyncio, time, datetime as dt
import asyncpg

SQL = """
SELECT service, region, sum(cost) AS total
FROM daily_cost
WHERE group_id = $1 AND usage_date BETWEEN $2 AND $3
GROUP BY GROUPING SETS ((service, region), (service), ())
"""

async def main():
    conn = await asyncpg.connect("postgresql://postgres:pg@localhost:5432/postgres")
    for i in range(1, 9):
        t = time.perf_counter()
        await conn.fetch(SQL, 200, dt.date(2025, 1, 1), dt.date(2025, 12, 31))
        print(f"{i}번째 {(time.perf_counter() - t) * 1000:.1f}ms")
    await conn.close()

asyncio.run(main())
```

```text
1번째 6.7ms
2번째 2.8ms
3번째 2.3ms
4번째 2.3ms
5번째 2.4ms
6번째 59.8ms
7번째 59.0ms
8번째 62.1ms
```

asyncpg 0.32.0으로 확인한 결과. SQLAlchemy 2.1.4의 `AsyncEngine`으로 `text()` 쿼리를 반복해도 6번째부터 같은 식으로 느려졌음

---

고치는 방법은 계획 고르는 방식을 어디까지 바꾸느냐에 따라 네 가지. 먼저 알아 둘 말이 둘 있음. 트랜잭션은 여러 SQL을 한 묶음으로 처리해 함께 반영하거나 함께 취소하는 단위이고, `SET LOCAL`은 설정을 그 트랜잭션 안에서만 바꾸고 트랜잭션이 끝나면 원래대로 돌려놓는 명령

적용 범위가 좁은 것부터 나열

| 선택지 | 적용 범위 | 효과 | 부작용 |
|---|---|---|---|
| 트랜잭션 안에서 `SET LOCAL plan_cache_mode = force_custom_plan` | 그 트랜잭션의 쿼리 | 그 트랜잭션의 쿼리만 매번 실제 값으로 계획 | 실행마다 계획 수립 시간과 `SET LOCAL` 문장 비용. 트랜잭션 밖에서 쓰면 효과 없음. 서버는 경고를 보내지만 asyncpg는 로그 리스너가 없으면 버려 앱에서는 조용히 무시됨 |
| 연결 설정 `server_settings`에 `plan_cache_mode` 지정 | 그 엔진이나 풀이 맺는 모든 연결의 모든 쿼리 | 앱 코드는 연결 설정 한 곳만 수정. 문장 재사용과 왕복 수는 그대로 | 그 연결의 파라미터 있는 쿼리 전부 매번 계획 |
| 드라이버 문장 캐시 끄기 | 그 엔진이나 연결의 모든 쿼리 | 문장 준비는 그대로 하지만 실행마다 새 문장이라 횟수가 쌓이지 않음. 범용 계획 전환 자체가 안 생김 | 모든 문장이 실행 전에 준비 요청을 따로 보내 서버 왕복이 늘어남. SQLAlchemy에서 URL 설정만으로 끄면 직전 문장을 닫는 요청까지 더해짐. 원격 DB면 네트워크 왕복 시간만큼 매번 손해 |
| 서버, DB, 역할 단위 설정 변경 | 그 서버, DB, 역할을 쓰는 모든 클라이언트 | 앱 코드 수정 없음 | 파라미터가 있는 쿼리는 범용 계획이 유리한 짧은 쿼리까지 매번 계획해 계획 CPU가 늘어남. 작은 인스턴스일수록 부담이고 다른 서비스에도 영향이 감 |

연결 설정과 드라이버 문장 캐시는 엔진이나 연결을 만들 때 지정

```python
# 연결 설정으로 plan_cache_mode 지정 (SQLAlchemy)
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@host/db",
    connect_args={"server_settings": {"plan_cache_mode": "force_custom_plan"}},
)

# 드라이버 문장 캐시 끄기 (SQLAlchemy)
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@host/db?prepared_statement_cache_size=0"
)

# 드라이버 문장 캐시 끄기 (asyncpg 직접 사용)
conn = await asyncpg.connect(dsn, statement_cache_size=0)
pool = await asyncpg.create_pool(dsn, statement_cache_size=0)
```

- SQLAlchemy를 쓰더라도 `connect_args={"statement_cache_size": 0}`으로 asyncpg 쪽 캐시를 끄면 이름 없는 문장으로 준비되어 실행마다 다시 파싱되므로 같은 효과가 남
- 서버 전체는 `postgresql.conf`나 `ALTER SYSTEM`, DB 단위는 `ALTER DATABASE`, 역할 단위는 `ALTER ROLE`로 바꿈. `ALTER DATABASE`와 `ALTER ROLE` 값은 새 연결부터 적용되므로 커넥션 풀의 기존 연결은 다시 맺어야 반영됨

선택지별 비용(로컬 측정)

| 항목 | 측정 대상 | 값 |
|---|---|---|
| 맞춤 계획 수립 시간(Planning Time) | 사내 이전 버전 쿼리 | 약 1.0ms(EXPLAIN 실측) |
| 맞춤 계획 수립 시간 | 재현 테이블 | 중앙값 0.13ms, 연결의 첫 실행은 0.8ms 안팎 |
| `SET LOCAL` 문장 추가 비용 | 사내 쿼리(로컬) | 문장당 약 0.04~0.07ms |
| 드라이버 문장 캐시를 껐을 때 늘어난 시간 | 사내 쿼리(로컬) | 문장당 약 0.58ms. 원격 DB면 네트워크 왕복 시간만큼 더 늘어남 |

계획을 매번 세우는 시간은 2초 손해와 비교하면 무시할 수준

실제로 고른 방법은 `SET LOCAL`

- `SET LOCAL`은 문제 쿼리에만 걸리므로 나머지 쿼리는 문장 재사용과 범용 계획의 이점을 그대로 누림
- 드라이버 문장 캐시 끄기는 모든 문장에 서버 왕복을 더하고, 서버 설정 변경은 모든 문장의 계획 CPU를 늘려 작은 인스턴스에서 부담이라 제외
- 같은 로컬 테스트 환경에서 적용 후 20회 연속 실행 p50 0.154초, p95 0.169초. p50은 가운데 값. 6번째 이후에도 처음 5번과 같은 수준

```python
from sqlalchemy import text

async with engine.begin() as conn:
    await conn.execute(text("SET LOCAL plan_cache_mode = force_custom_plan"))
    result = await conn.execute(pivot_query, params)
```

- `engine.begin()`이 트랜잭션을 열고, 블록이 끝나면 트랜잭션을 확정하면서 설정도 원래대로 돌아감
- `plan_cache_mode`는 준비할 때가 아니라 실행할 때 읽힘. 이미 준비되어 범용 계획을 쓰던 문장에도 `SET LOCAL`이 바로 적용됨
- 커넥션 풀로 연결이 돌아가도 그 연결을 다음에 빌려 쓰는 요청에 설정이 남지 않음
- asyncpg를 직접 쓸 때 `conn.execute()`를 트랜잭션 없이 부르면 문장마다 자동 커밋이라 `SET LOCAL`이 효과가 없음. 오류도 없고 경고도 앱에 보이지 않음. `async with conn.transaction():` 안에서 실행. SQLAlchemy도 `isolation_level="AUTOCOMMIT"`이면 같음
- 재현 테이블에서도 `SET LOCAL`을 넣은 뒤로는 6번째 이후 중앙값 2.7ms, p95 4.0ms로 처음 5번과 같은 수준

---

같은 문제를 의심해 볼 만한 증상

- 같은 쿼리, 같은 값인데 처음 5번만 빠르고 6번째부터 느림
- 앱을 재시작하거나 새 연결을 맺은 직후에는 다시 빠름
- asyncpg를 직접 쓰면 5분쯤마다 5번 빨라졌다가 다시 느려짐. 문장 캐시 항목이 사용 여부와 상관없이 만들어진 지 300초가 지나면 다시 준비되어 횟수가 0부터 다시 쌓이기 때문. SQLAlchemy asyncpg 방언은 자체 캐시를 써서 이 현상이 없음
- psql에 값을 직접 넣어 돌리면 빠른데 앱에서만 느림. 값을 직접 넣은 SQL은 준비된 문장이 아니라서 실행할 때마다 그 값으로 새로 계획되기 때문. psql에서도 `PREPARE`, `EXECUTE`로 돌리면 앱과 같은 규칙을 탐
- 필터 값에 따라 읽을 양이 크게 다른 쿼리. 그룹 크기 편차, 기간 길이 편차가 대표적

확인하는 방법

- `EXPLAIN EXECUTE` 결과에 `$1` 같은 자리 표시가 보이면 범용 계획
- `pg_prepared_statements`의 `generic_plans`, `custom_plans` 숫자 확인. 앱 연결의 문장은 psql 연결에서 보이지 않으므로 앱과 같은 연결에서 조회하거나 psql에서 `PREPARE`로 재현
- `EXPLAIN (GENERIC_PLAN)`으로 실행 없이 범용 계획 미리 보기
- 범용 계획의 예상 행 수와 실제 행 수가 크게 어긋나는지 비교
- 확인용 `EXPLAIN EXECUTE`도 실행 횟수에 들어간다는 점 감안
- `ANALYZE`로 통계를 갱신해도 실행 횟수와 맞춤 계획 평균은 초기화되지 않음. 범용 계획을 다시 세워 비교할 뿐이라 통계 갱신만으로 풀린다고 기대하기 어려움

어디까지 바꿀지 고르는 기준

| 상황 | 선택 |
|---|---|
| 값에 따라 계획이 달라져야 하는 쿼리가 소수 | 그 쿼리의 트랜잭션에만 `SET LOCAL`. 반드시 트랜잭션 안에서 |
| 앱의 쿼리 대부분이 그런 모양 | 연결 설정이나 드라이버 문장 캐시 끄기 검토 |
| 앱 코드를 고칠 수 없음 | 서버, DB, 역할 단위 설정. 영향 범위를 먼저 따져 봄 |

기능별로 필요한 PostgreSQL 버전

| 기능 | 도입 버전 |
|---|---|
| `plan_cache_mode` | PostgreSQL 12 |
| `pg_prepared_statements`의 `generic_plans`, `custom_plans` | PostgreSQL 14 |
| `EXPLAIN (GENERIC_PLAN)` | PostgreSQL 16 |
