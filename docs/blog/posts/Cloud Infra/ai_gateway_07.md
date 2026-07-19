---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - Cloud
  - AI
  - SRE
hide:
  - toc
---
# AI Gateway 관측성 정리

<!-- more -->

관측성(Observability)이란 게이트웨이를 지나는 요청의 내부 상태를 로그·메트릭·트레이스로 밖에서 파악 가능하게 만드는 성질

---

## LLM 관측이 다른 이유

일반 백엔드 지표에 토큰·비용·첫 토큰 지연 차원이 더해지는 것이 LLM 관측의 특징

|관측 차원|일반 API 백엔드|LLM 백엔드|
|--------|-------------|---------|
|지연|요청~응답 시간|요청~응답 + TTFT(첫 토큰까지) 분리|
|처리량|초당 요청 수(RPS)|RPS + 초당 토큰 수|
|비용|인프라 고정비|요청마다 토큰 종량 과금|
|실패|4xx/5xx|4xx/5xx + 폴백·재시도 발생|

- 스트리밍 응답은 전체 지연 하나로 못 봄 → 첫 토큰(TTFT)과 완료 시간을 분리 측정
- 비용이 요청마다 달라지고 폴백·재시도가 정상 경로에 섞임 → 토큰·spend와 실제 처리 백엔드를 요청 단위로 기록 필요

---

## 요청 단위 관측: 응답 헤더

응답 헤더 한 벌이 요청별 지연 분해와 라우팅 결과를 그대로 실음

```s
curl -s -D - -o /dev/null http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-dotoryeee-1234" -H "Content-Type: application/json" \
  -d '{"model":"qwen-small","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

x-litellm-call-id: 4fca4ae9-2075-4c3f-8b74-8655cccb42dd
x-litellm-response-duration-ms: 395.33
x-litellm-overhead-duration-ms: 6.84
x-litellm-model-group: qwen-small
x-litellm-attempted-retries: 0
x-litellm-attempted-fallbacks: 0
```

|헤더|의미|
|----|----|
|`x-litellm-call-id`|요청 추적용 고유 ID, 로그·트레이스 상관에 사용|
|`x-litellm-response-duration-ms`|백엔드 응답까지 총 소요 시간|
|`x-litellm-overhead-duration-ms`|게이트웨이 자체 처리로 더해진 시간|
|`x-litellm-attempted-retries`|이 응답이 나오기까지 재시도 횟수|
|`x-litellm-attempted-fallbacks`|폴백 발생 횟수, 0 초과면 대체 백엔드가 처리|

- response-duration과 overhead-duration이 분리돼 지연 원인이 백엔드인지 게이트웨이인지 구분 가능
- attempted-fallbacks가 0보다 크면 요청한 별칭이 아닌 대체 백엔드가 응답 (2편 폴백과 같은 신호)
- 키 단위 누적 spend는 5편 key/info, 요청 단위 감사 로그는 `/spend/logs`로 조회

```json
{"request_id":"chatcmpl-db7a1fa7-ea4f-4b80-8a53-21b3f5bae931","call_type":"acompletion",
 "model":"ollama/llama3.2:1b","total_tokens":124,"spend":0.0,"cache_hit":null}
```

---

## TTFT 실측

TTFT(Time To First Token)이란 요청 전송부터 첫 토큰이 도착하기까지의 시간으로, 스트리밍 체감 속도를 좌우하는 지표

- 전체 지연은 마지막 토큰까지, TTFT는 첫 토큰까지 → 사용자 체감은 TTFT가 결정
- curl -w의 time_starttransfer(첫 바이트)와 time_total(완료)로 분해 측정

```s
WFMT='TTFB=%{time_starttransfer}s  total=%{time_total}s\n'

# 논스트리밍 (stream:false)
TTFB=2.785s  total=2.785s

# 스트리밍 (stream:true)
TTFB=0.208s  total=4.009s
```

- 논스트리밍은 TTFB와 total이 사실상 같음 → 전체 생성이 끝날 때까지 클라이언트가 대기
- 스트리밍은 첫 바이트가 0.2초, 완료가 약 4초 → 첫 토큰을 먼저 흘려보내 체감 지연을 줄임
- 프로메테우스 `litellm_llm_api_time_to_first_token_metric`도 스트리밍 호출에서만 기록됨 (같은 요청 sum=0.181)

---

## 메트릭: Prometheus

callbacks에 prometheus 한 줄로 /metrics 엔드포인트가 열리고 요청·지연·토큰·비용이 시계열로 쌓임

```yaml title="litellm_config.yaml"
litellm_settings:
  drop_params: true
  callbacks: ["prometheus"]     # /metrics 엔드포인트 노출
```

```s
curl -sL http://localhost:4000/metrics -H "Authorization: Bearer sk-dotoryeee-1234"

litellm_proxy_total_requests_metric_total{requested_model="qwen-small",status_code="200",...} 3.0
litellm_request_total_latency_metric_bucket{le="0.5",model="qwen2.5:0.5b",...} 3.0
litellm_llm_api_time_to_first_token_metric_sum{model="qwen2.5:0.5b",...} 0.181239
litellm_overhead_latency_metric_sum{model_group="qwen-small",...} 0.003282
litellm_deployment_success_responses_total{model_group="qwen-small",...} 3.0
```

|메트릭|관측 대상|
|------|--------|
|`litellm_request_total_latency_metric`|요청 전체 지연 히스토그램|
|`litellm_llm_api_time_to_first_token_metric`|TTFT 히스토그램(스트리밍)|
|`litellm_overhead_latency_metric`|게이트웨이 자체 오버헤드|
|`litellm_spend_metric` / `litellm_total_tokens_metric`|비용·토큰 누적|
|`litellm_deployment_success/failure_responses_total`|백엔드별 성공·실패 수|
|`litellm_deployment_successful_fallbacks_total`|폴백 발생 횟수|

- 이 랩은 LiteLLM 1.94.0 community이며 `has_license:false` 상태에서 `/metrics`가 그대로 동작 → 프로메테우스 메트릭은 무료 코어에 포함
- Enterprise 티어가 더하는 것은 SSO·RBAC·감사 로그 같은 거버넌스 기능이지 기본 메트릭·트레이싱이 아님 (3편 라이선스 경계와 동일)
- 다만 프로메테우스 통합의 무료·유료 경계는 버전마다 달라진 이력 → 배포 버전에서 직접 확인 권장

---

## 트레이싱: OpenTelemetry

요청 하나를 내부 단계별 span으로 쪼개 어느 구간에서 시간이 샜는지 추적하는 표준이 OpenTelemetry(OTEL)

```yaml title="litellm_config.yaml"
litellm_settings:
  callbacks: ["otel"]                          # 트레이스 전송
```

```yaml title="docker-compose.yml"
    environment:
      OTEL_EXPORTER: otlp_http
      OTEL_ENDPOINT: http://otel-collector:4318 # 수집기 주소
```

otel-collector를 debug exporter로 띄우고 요청 한 건을 보내면 하나의 trace_id 아래 내부 span이 도착함

```s
service.name: litellm
Trace ID: c69af1f904d85841782a2f8bb8d585c2
  auth                # 키 인증
  postgres            # 사용자 조회
  proxy_pre_call      # pre-call 훅
  router              # 배포 선택
  litellm_request
  raw_gen_ai_request  # 실제 백엔드 LLM 호출
  batch_write_to_db   # spend 비동기 기록
```

- 한 요청 = 한 trace_id, 인증·라우팅·백엔드 호출이 각각 span → 지연이 게이트웨이 내부인지 백엔드인지 분리
- OTEL도 community 무료. 같은 OTLP로 Jaeger·Tempo·Datadog 등 백엔드에 그대로 전송
- 프롬프트·응답 본문까지 보는 LLM 특화 관측은 `callbacks: ["langfuse"]` + LANGFUSE_* 환경변수로 교체 (설정 예시)

---

## 운영: 무엇에 알람을 거는가

관측의 목적은 대시보드가 아니라 개입 시점을 잡는 것 → 아래 네 축을 우선 알람화

|축|메트릭|알람 신호|
|--|------|--------|
|오류율|`litellm_proxy_failed_requests_metric`|5xx 비율이 기준선 초과|
|폴백 발생|`litellm_deployment_successful_fallbacks_total`|증가 시 주 프로바이더 장애 조기 신호|
|예산 소진|`litellm_remaining_api_key_budget_metric`|키별 잔여 예산이 임계 이하|
|TTFT 악화|`litellm_llm_api_time_to_first_token_metric`|p95 TTFT가 기준 초과|

- 게이트웨이 자체 병목은 `litellm_overhead_latency_metric` 급증으로 잡음 → 백엔드가 멀쩡한데 지연이 늘면 게이트웨이 의심
- 폴백은 200으로 응답되는 "성공한 장애"라 지표를 안 보면 놓침 → 폴백 카운터를 반드시 알람에 포함

---

## 결론

- 응답 헤더·`/spend/logs`로 요청 단위, 프로메테우스로 시계열, OTEL로 요청 내부까지 세 층위로 관측이 완성됨
- 프로메테우스·OTEL 모두 LiteLLM community에서 무료 동작을 확인, Enterprise는 거버넌스 기능에 한정
- 알람은 오류율·폴백·예산·TTFT 네 축이면 대부분의 사고를 조기에 포착
- 1편 개념부터 구축·비교·라우팅·캐싱·가드레일을 지나 관측까지, 게이트웨이 한 겹으로 LLM 운영을 모았음
- 게이트웨이를 세우는 일이 "한 곳으로 모으기"였다면, 관측성은 "그 안을 밖에서 들여다보기"
