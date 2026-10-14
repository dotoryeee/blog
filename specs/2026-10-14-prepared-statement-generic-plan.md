# 준비된 문장 범용 계획 전환 글 기획과 주장 원장

작성일 2026-10-14. 상태: 게시 완료(2026-10-14, draft false). 검증 5종(공식 문서 리서치, PostgreSQL 사실, 드라이버, 재현 재실행, 국문) 뒤 최종 원장 대조 반영. 사용자 지시로 제목을 "plan_cache_mode 정리", 부제를 "PostgreSQL 준비된 문장(Prepared Statement)과 드라이버 문장 캐시"로 바꾸고, 글 안의 소제목(##, ###)을 모두 없앤 뒤 DB 입문자용 설명(실행 계획, 플래너, 인덱스, 통계, 선택도, 드라이버, 연결, 커넥션 풀, 트랜잭션, EXPLAIN 읽는 법)을 덧붙여 게시.

| 산출물 | 경로 |
|---|---|
| 글 | `docs/posts/SRE/prepared_statement_generic_plan.md` (categories Database) |
| 재현 컨테이너 | `blog-plancache-pg` (postgres:16-alpine, PostgreSQL 16.14, 127.0.0.1:55499). DB `repro`가 글의 SQL 그대로 시드한 데이터(setseed 0.5). DB `postgres`는 시드 없이 만든 첫 실험 데이터 |
| 드라이버 재현 | `python:3.12-slim` 컨테이너에서 asyncpg 0.32.0, SQLAlchemy 2.1.4 |

## 요청

cloud-intelligence-finops 세션이 사용자 지시로 전달. 사내 클라우드 비용 분석 서비스의 피벗 집계 쿼리가 같은 값 반복 실행 시 6번째부터 느려진 사례.

조건
- 회사, 고객사 이름, 내부 시스템명, 코드 경로, 인프라 정보 금지. "클라우드 비용 분석 서비스"까지만
- 제목과 본문에 em dash, en dash, 하이픈, 가운뎃점 금지(쉼표로 대체). 개조식 문체. layer는 항상 "레이어"
- 사내 수치는 로컬 테스트 측정값이라고 밝힘
- 증상 절 쿼리(2단계 집계 구조)의 노드 수준 EXPLAIN 기록은 없음. 계획 수준 근거는 같은 증상을 보인 이전 버전 피벗 쿼리의 로컬 재측정(C39~C46)을 쓰고, 재현 테이블은 원리 설명용으로 구분해 실음. 증상 절 쿼리의 병렬 계획 여부는 쓰지 않음

사용자 확정 구조
1. 증상과 흔한 오해
2. 준비된 문장과 드라이버 자동 재사용
3. 처음 5번 맞춤 계획, 6번째 비교, 예상 비용 기준
4. 왜 이 쿼리에서 손해였나, EXPLAIN 나란히 비교
5. 직접 재현하기
6. 해결 선택지와 트레이드오프, 고른 방법과 이유
7. 정리 체크리스트

## 제목과 도입 후보

최종: 제목 "plan_cache_mode 정리", 부제 "PostgreSQL 준비된 문장(Prepared Statement)과 드라이버 문장 캐시" (사용자 지정)

| 안 | 제목 | 부제 |
|---|---|---|
| A (초안) | 같은 쿼리가 여섯 번째부터 느려지는 이유 | PostgreSQL 준비된 문장의 범용 계획 전환 |
| A2 (국문 검토 제안) | 같은 쿼리가 6번째 실행부터 느려지는 이유 | PostgreSQL 준비된 문장의 범용 계획 전환과 plan_cache_mode |
| B | plan_cache_mode 정리(맞춤 계획과 범용 계획) | 같은 쿼리가 6번째부터 느려진 사례로 알아보기 |
| C | 0.17초 쿼리가 6번째부터 2.2초가 된 이유 | PostgreSQL 준비된 문장과 드라이버 문장 캐시 |

도입
- 1안 (적용): 원인과 해결 한 줄. "결론부터 적으면", "A가 아니라 B" 표현은 국문 검토에서 빼기로 함
- 2안: 도입 없이 바로 증상 절

## 주장 원장

근거 종류: 사내(전달받은 사내 측정 기록), 재현(이 세션 로컬 재현), 문서(공식 문서), 소스(공식 소스 코드, 코드 기반 판단)

| ID | 주장 | 근거 종류 | 근거 |
|---|---|---|---|
| C1 | 같은 값 20회 연속, 1~5회 0.16~0.18초, 6~20회 2.2~2.5초, p95 2.45초 | 사내 | 전달 메시지 |
| C2 | 로컬 Docker PostgreSQL 16, 약 120만 행 시드, 운영 수치 아님 | 사내 | 전달 메시지 |
| C3 | 적용 후 20회 p50 0.154초, p95 0.169초 | 사내 | 전달 메시지 |
| C4 | 계획 수립 1ms 안팎 | 사내 | 구현 기록 문구. Planning Time 실측 여부는 미기록 |
| C5 | 준비된 문장은 세션 안에서만 살아 있음 | 문서 | https://www.postgresql.org/docs/16/sql-prepare.html |
| C6 | asyncpg `statement_cache_size` 기본 100, 연결별 LRU, 0이면 끔 | 문서 | https://magicstack.github.io/asyncpg/current/api/index.html |
| C7 | SQLAlchemy asyncpg 방언은 모든 문장을 `prepare()`로 준비, 연결별 캐시, `prepared_statement_cache_size` 기본 100, 0이면 끔 | 문서 | https://docs.sqlalchemy.org/en/21/dialects/postgresql.html#prepared-statement-cache (2.0 문서와 같은 문장, 글은 2.1 링크) |
| C8 | SQLAlchemy는 asyncpg 자체 LRU 대신 자기 캐시를 씀 | 소스 | sqlalchemy rel_2_1_4(rel_2_0_54 동일) asyncpg.py `_prepare`, asyncpg v0.32.0 `prepare()`가 `use_cache=False` |
| C9 | 횟수는 연결마다 따로 셈 | 문서, 소스 | 세션 범위(C5), plancache는 문장(CachedPlanSource)별 카운터 |
| C10 | auto에서 처음 5번 맞춤 계획, 평균 예상 비용, 6번째 범용 계획 생성과 비교 | 문서 | PREPARE 문서 Notes |
| C11 | "크게 비싸지 않으면"의 구현은 맞춤 계획 비용에 1000 × cpu_operator_cost × (rtable 수 + 1) 가산, 테이블 1개면 5.0. 범용 비용 < 맞춤 평균이면 범용 | 소스 | REL_16_STABLE plancache.c `choose_custom_plan`, `cached_plan_cost` |
| C12 | 판단은 예상 비용 기준, 실행 시간 미반영, 되돌리는 장치 없음 | 소스 | plancache.c (실행 시간을 읽는 코드 없음) |
| C13 | 6번째에 범용이 지면 매 실행 재비교, 이기면 맞춤 통계가 더 쌓이지 않아 고정 | 소스 | plancache.c `GetCachedPlan` |
| C14 | PREPARE 문서가 force_custom_plan 쓰임새를 범용 계획 예상 비용이 크게 틀릴 때로 안내 | 문서 | PREPARE 문서 "primarily useful if the generic plan's cost estimate is badly off" |
| C15 | 재현 테이블 1,204,500행, 그룹 200개, 최대 206,241행, 최소 1,952행, 인덱스 2개 | 재현 | DB repro |
| C16 | 범용 계획 예상 30행 = 1,204,500 × 1/200 × 0.005. `= $1`은 1/n_distinct 계열, 범위 쌍은 DEFAULT_RANGE_INEQ_SEL 0.005 | 소스, 재현 | selfuncs.h, selfuncs.c `var_eq_non_const`, clausesel.c. EXPLAIN rows=30 |
| C17 | 데이터가 날짜순이라 usage_date 인덱스 읽기 비용이 싸게 잡힘 | 재현 | pg_stats correlation usage_date 1.0, group_id 0.026 |
| C18 | 5번째 맞춤 계획 예상 비용 5,587, 1.7ms. 6번째 범용 211, 62.2ms, Rows Removed 1,202,548. 26배 싸 보였고 이 실행에서 37배, 반복 중앙값 30배 안팎 느림 | 재현 | DB repro EXPLAIN (ANALYZE, TIMING OFF). 재현 검증 28~31배. 맞춤 계획 예상치는 ANALYZE 표본에 따라 rows 2,4xx, cost 5,6xx로 변동 |
| C19 | 값 조합 표 (0.6/1.2, 2.0/58.5, 2.0/2.2, 70.3/115.0 ms) | 재현 | DB repro, 조합별 11회 중 첫 회 제외 10회 중앙값 |
| C20 | asyncpg 스니펫 출력 6.7, 2.8, 2.3, 2.3, 2.4, 59.8, 59.0, 62.1 ms. 59.8/2.4 ≈ 25배 | 재현 | DB repro |
| C21 | asyncpg 0.32.0, SQLAlchemy 2.1.4에서 6번째 점프, SQLAlchemy text()도 동일 | 재현 | DB postgres, 8회 측정 |
| C22 | EXPLAIN EXECUTE도 실행 횟수에 포함 | 재현, 소스 | pg_prepared_statements 카운터, prepare.c `ExplainExecuteQuery`가 `GetCachedPlan` 호출 |
| C23 | 범용 계획이면 $n 기호, 맞춤 계획이면 실제 값 | 문서 | PREPARE 문서 |
| C24 | pg_prepared_statements generic_plans, custom_plans는 14부터, 현재 세션 문장만 | 문서 | view-pg-prepared-statements, 14 릴리스 노트 |
| C25 | EXPLAIN (GENERIC_PLAN) 16부터, ANALYZE와 함께 불가, 캐시된 문장의 실제 계획을 보여 주지는 않음 | 문서, 재현 | sql-explain, 16 릴리스 노트, 재현 오류 메시지 |
| C26 | SET LOCAL은 트랜잭션 끝나면 복귀, 트랜잭션 밖에서는 경고만 | 문서, 재현 | sql-set, 재현 WARNING |
| C27 | plan_cache_mode는 12부터 | 문서 | 12 릴리스 노트 |
| C28 | 캐시를 꺼도 준비는 하지만 실행마다 새 문장이라 횟수가 쌓이지 않음 | 소스, 재현 | asyncpg `_get_statement` unnamed, SQLAlchemy `_prepare`. 재현에서 캐시 0이면 점프 없음 |
| C29 | SQLAlchemy URL `?prepared_statement_cache_size=0` | 문서 | SQLAlchemy 문서 |
| C30 | asyncpg `connect(..., statement_cache_size=0)` | 문서 | asyncpg 문서 |
| C31 | asyncpg `server_settings`, SQLAlchemy `connect_args={"server_settings": ...}` | 문서, 재현 | asyncpg 문서, SQLAlchemy JIT 절 예시. 재현에서 server_settings로 점프 없음 |
| C32 | plan_cache_mode는 실행 시점에 읽혀 이미 준비된 문장에도 SET LOCAL 적용 | 문서, 재현 | runtime-config "considered when a cached plan is to be executed", 재현 |
| C33 | 재현 맞춤 계획 Planning Time 중앙값 0.13ms, 연결 첫 실행 0.8ms 안팎 | 재현 | DB postgres 21회, 재현 검증 3세션 첫 실행 0.75~0.84ms |
| C34 | 재현에서 SET LOCAL 적용 후 6번째 이후 중앙값 2.7ms, p95 4.0ms | 재현 | asyncpg 3세트 × 20회 |
| C35 | asyncpg에서 트랜잭션 없이 실행하면 자동 커밋이라 SET LOCAL 효과 없음 | 문서 | sql-set, asyncpg는 명시 트랜잭션 밖에서 자동 커밋 |
| C36 | psql에 값을 넣은 SQL은 준비된 문장이 아니라 매번 그 값으로 계획. psql의 PREPARE, EXECUTE는 같은 규칙 | 문서, 소스 | app-psql(기본은 단순 쿼리 프로토콜), protocol-flow, postgres.c `exec_simple_query`가 문장마다 계획. 단순 쿼리로 보낸 EXECUTE는 prepare.c `ExecuteQuery`가 `GetCachedPlan` 사용 (1차 근거 "단순 쿼리는 계획 캐시를 안 씀"은 틀려서 수정) |
| C37 | PostgreSQL이 느린 쿼리의 우선순위를 알아서 낮추지는 않음 | 소스 | REL_16_STABLE 전체에 setpriority, nice, sched_setscheduler, ioprio 호출 없음. 비용 지연은 VACUUM, ANALYZE용뿐(runtime-config-resource 20.4.4) |
| C38 | 설정 범위: postgresql.conf와 ALTER SYSTEM은 서버 전체, ALTER DATABASE는 DB, ALTER ROLE은 역할, 둘 다 새 세션부터 | 문서 | https://www.postgresql.org/docs/16/config-setting.html (1차 표현 "DB 전역"이 부정확해 수정) |
| C39 | 이전 버전 피벗 쿼리 로컬 PG16 약 120만 행, 같은 연결 같은 값 8회, 1~5회 0.18~0.21초, 6회부터 2.5~2.7초(약 14배), custom_plans 5에서 멈추고 generic_plans 증가 | 사내 | 전달 메시지 2차 |
| C40 | 이전 버전 쿼리 맞춤 계획: 병렬 해시 집계 계열, 순차 읽기 위주, 약 219ms, Planning Time 약 1.0ms(EXPLAIN 실측) | 사내 | 전달 메시지 2차 |
| C41 | 이전 버전 쿼리 범용 계획: 복합 인덱스 스캔과 중첩 루프, 약 3,186ms, 버퍼 약 120만 페이지(행마다 힙 페이지 1개) | 사내 | 전달 메시지 2차 |
| C42 | 범용 계획 예상 약 3,060행 vs 실제 약 120만, 예상치는 행 수 × 1/n_distinct × 0.005 | 사내, 소스 | 전달 메시지 2차, C16과 같은 근거. 3차 확인: 시드 1,224,000행(큰 그룹 1,200,000 + 작은 그룹 24,000), ANALYZE 후 그룹 컬럼 n_distinct 2.0, 1,224,000 × 1/2 × 0.005 = 3,060 |
| C43 | SQL 문자열이 늘 같은 count(*) 사전 점검 쿼리도 0.10초에서 6회부터 1.5초 | 사내 | 전달 메시지 2차 |
| C44 | 작은 그룹은 범용 계획에서도 0.016초, 큰 그룹에서만 느려짐. 작은 그룹 5회 뒤 큰 그룹 첫 조회도 바로 범용 계획 | 사내, 소스 | 전달 메시지 2차. num_custom_plans는 값과 무관하게 증가 |
| C45 | SET LOCAL 직후 0.15초로 회복, 문장당 추가 비용 약 40~70µs | 사내 | 전달 메시지 2차 |
| C47 | asyncpg는 서버 WARNING을 로그 리스너가 없으면 버림. 트랜잭션 밖 SET LOCAL은 앱에서 조용히 무시됨. SQLAlchemy AUTOCOMMIT도 같음 | 소스, 재현 | asyncpg connection.py `_process_log_message`, 검증 에이전트 실행 |
| C48 | SQLAlchemy URL로만 캐시를 끄면 실행마다 새 이름 있는 문장 준비와 직전 문장 Close가 붙어 왕복이 2회 늘어남. asyncpg 쪽 statement_cache_size=0이면 이름 없는 문장 | 소스, 재현 | SQLAlchemy `_prepare`, asyncpg `_maybe_gc_stmt`, `_cleanup_stmts`, 내부 호출 계수 |
| C49 | asyncpg 직접 사용 시 캐시 항목은 생성 후 300초에 만료(사용해도 연장 안 됨)되어 다시 준비, 처음 5번이 다시 빨라짐. SQLAlchemy 경로는 해당 없음 | 소스, 재현 | asyncpg `_set_entry_timeout`, `_on_entry_expired`, 검증 에이전트 302초 실험 |
| C50 | asyncpg 풀 반납 리셋(RESET ALL 등)은 준비된 문장을 지우지 않음. server_settings 값은 리셋 뒤에도 유지 | 재현 | 검증 에이전트 실행 |
| C46 | 드라이버 문장 캐시 끄기는 모든 문장에 왕복 1회 추가(로컬 +0.58ms, 원격은 RTT만큼), DB 전역 변경은 계획 CPU 증가로 작은 인스턴스에서 비권장 | 사내, 소스 | 전달 메시지 2차. SQLAlchemy `_prepare`가 캐시 0이면 실행마다 `prepare()` 호출(Parse, Describe 왕복) 후 실행 |
| C51 | 범용 계획은 기간 조건만으로 usage_date 인덱스에서 약 6,000행(1,204,500 × 0.005)을 읽는다고 봄 | 재현 | EXPLAIN (GENERIC_PLAN) 기간 조건 단독 rows=6022 |
| C52 | 증상 절 쿼리는 GROUPING SETS를 쓰는 피벗 집계, 그룹 ID와 기간을 파라미터로 받음, 그룹과 기간 값에 따라 읽을 양이 크게 달라짐 | 사내 | 전달 메시지 1차 |
| C53 | 통계 갱신이나 DDL 무효화 뒤에도 실행 횟수와 맞춤 계획 평균은 리셋되지 않고 범용 계획만 다시 세워 비교 | 소스 | plancache.c `RevalidateCachedQuery` 주석 "we do not reset generic_cost or total_custom_cost", `GetCachedPlan`의 generic_cost 갱신 |

## 검증 기록

| 검증 | 결과 | 반영 |
|---|---|---|
| 공식 문서 리서치 | 6번째 이후 재비교 규칙, 계획 수립 비용 가산 5.0, SQLAlchemy가 asyncpg LRU 우회, pg_prepared_statements 세션 한정 | 초안 수정 |
| 재현 재실행 | 핵심 수치 전부 재현. setseed는 데이터만 고정, 37배는 단발 값, SET LOCAL 첫 호출 제외 필요 | 문구 수정 |
| PostgreSQL 사실 확인 | 고정 표현 과장(무효화 시 재비교), 설정 범위 부정확, 파라미터 없는 문장 예외, 이틀 남짓 오류 | 전부 반영, C36 C37 C38 근거 교체 |
| 드라이버 확인 | 트랜잭션 밖 SET LOCAL 경고가 앱에 안 보임, SQLAlchemy URL로 끄면 왕복 2회, asyncpg 300초 수명 현상 | 전부 반영, C47~C50 추가 |
| 국문 검토 | 로컬 표기 보강, 맞춤 계획과 범용 계획 비교 표, server_settings 행, 용어 정의, 표기 통일, 제목 6번째 통일 | 전체 재작성으로 반영 |
| 최종 원장 대조 | 검산 전부 일치. 사내 계획 서술 3곳이 기록보다 강함, 근거 없는 범위 서술 2곳, 재현 수치 1곳 | 전부 반영, C52 C53 추가, C7 C8 C20 C34 정정 |
