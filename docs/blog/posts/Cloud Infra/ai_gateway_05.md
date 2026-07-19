---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - Cloud
  - AI
---

# AI Gateway 캐싱과 비용 관리

<!-- more -->

## 목표

---

- 4편 끝에서 예고한 캐싱(Caching)으로 같은 요청의 토큰 비용을 0으로 만드는 방법을 2편 랩에서 실측해봅니다
- Redis 캐시를 붙여 동일 요청의 두 번째 호출이 백엔드를 거치지 않고 즉시 응답되는 것을 확인합니다
- 커스텀 단가로 spend를 쌓고, 예산을 건 키로 초과 호출이 차단되는지, 시맨틱 캐시는 어디가 다른지까지 봅니다

!!! tip
    💡 캐시 백엔드는 redis 컨테이너 하나만 추가하면 되어 별도 비용이 들지 않습니다

## Redis 캐시 구성

---

1. 2편 docker-compose.yml에 redis 서비스를 추가하고 litellm의 depends_on에 넣습니다

    ```yaml title="docker-compose.yml"
    services:
      redis:
        image: redis:7-alpine
        container_name: litellm_redis
        ports:
          - "6379:6379"
    ```

2. litellm_config.yaml의 litellm_settings에 캐시 설정을 붙입니다. type을 redis로 두고 컨테이너 이름을 host로 지정합니다

    ```s
    vi litellm_config.yaml
    ```

    ```yaml title="litellm_config.yaml"
    litellm_settings:
      drop_params: true
      cache: true
      cache_params:
        type: redis          # 완전 일치 요청을 해시로 캐싱
        host: redis          # compose 서비스 이름
        port: 6379
    ```

3. redis를 올리고 게이트웨이를 재시작한 뒤 캐시 상태를 확인합니다. cache/ping이 연결과 set 테스트까지 함께 알려줍니다

    ```s
    docker compose up -d redis
    docker compose restart litellm

    curl -s http://localhost:4000/cache/ping -H "Authorization: Bearer sk-dotoryeee-1234"
    {"status":"healthy","cache_type":"redis","ping_response":true,
     "set_cache_response":"success", ... "redis_version":"7.4.9"}
    ```

## 캐시 히트 실측

---

1. temperature를 0으로 고정한 동일 요청을 두 번 보냅니다. 응답 시간과 x-litellm-cache-key 헤더로 히트를 판별합니다

    ```s
    REQ='{"model":"qwen-small","messages":[{"role":"user",
      "content":"Name three primary colors. One line."}],"max_tokens":30,"temperature":0}'

    # 1회차 (miss)
    curl -s -o /dev/null -w '%{time_total}s\n' -D - ... -d "$REQ" | grep -i x-litellm-cache
    1.452753s
    (헤더 없음)

    # 2회차 (hit)
    curl -s -o /dev/null -w '%{time_total}s\n' -D - ... -d "$REQ" | grep -i x-litellm-cache
    0.003956s
    x-litellm-cache-key: 7640381168783f084d22e742fa267edf54c42976...
    ```

2. 1회차는 백엔드 추론이라 1.45초가 걸렸고, 2회차는 0.004초에 끝났습니다. 두 응답의 completion id가 chatcmpl-a527692f로 같아서 새로 생성하지 않고 저장된 응답을 그대로 내려보낸 것을 알 수 있습니다

!!! notice
    💡 캐시 히트 여부는 응답 본문의 model 값이 아니라 x-litellm-cache-key 헤더로 확인합니다

## 커스텀 단가와 비용 추적

---

Ollama 백엔드는 LiteLLM 기본 단가가 0이라 아무리 호출해도 spend가 쌓이지 않습니다. 유료 API의 비용 추적을 흉내내려면 model_list의 litellm_params에 토큰당 단가를 직접 넣습니다.

1. 두 모델에 입력·출력 단가를 지정합니다. 데모용 값이고 실제 요금과는 무관합니다

    ```yaml title="litellm_config.yaml"
    model_list:
      - model_name: llama-small
        litellm_params:
          model: ollama/llama3.2:1b
          api_base: http://ollama:11434
          input_cost_per_token: 0.0000005     # 입력 토큰당 0.5μ$
          output_cost_per_token: 0.0000015    # 출력 토큰당 1.5μ$
    ```

2. 마스터 키로 추적용 virtual key를 발급합니다. spend가 0.0에서 시작합니다

    ```s
    curl -s http://localhost:4000/key/generate \
      -H "Authorization: Bearer sk-dotoryeee-1234" -H "Content-Type: application/json" \
      -d '{"key_alias":"dotoryeee-spend-key","models":["llama-small","qwen-small"]}'
    {"key_alias":"dotoryeee-spend-key","spend":0.0,"key":"sk-06e-0bSJ-AqJ_E8jx8sK8g"}
    ```

3. 이 키로 서로 다른 프롬프트를 여러 번 호출하고 key/info로 누적 spend를 확인합니다. spend 반영은 비동기라 몇 초 뒤 값이 확정됩니다

    ```s
    # 서로 다른 프롬프트 여러 건 호출 후
    curl -s "http://localhost:4000/key/info?key=sk-06e-0bSJ-AqJ_E8jx8sK8g" \
      -H "Authorization: Bearer sk-dotoryeee-1234"

    "key_alias": "dotoryeee-spend-key",
    "spend": 0.0004005,
    "models": ["llama-small", "qwen-small"]
    ```

지정한 단가대로 토큰 사용량이 달러로 환산돼 키에 쌓였습니다. 단가를 넣지 않았다면 같은 호출에도 spend는 계속 0이었을 것입니다.

## 캐시 히트는 비용이 붙지 않습니다

---

1. 같은 키로 새 요청을 한 번(miss) 보내고 곧바로 동일 요청을 한 번 더(hit) 보낸 뒤 spend 변화를 봅니다

    ```s
    # spend before : 0.0004005
    # 새 요청 1회(miss) + 동일 요청 1회(hit)
    # spend after  : 0.0004385
    ```

2. 두 번 호출했는데 spend는 miss 한 건 값인 약 3.8e-5만 늘고 hit는 0을 더했습니다. 캐시는 지연을 줄이는 동시에 같은 요청의 토큰 비용을 없앱니다

## 예산 초과 차단

---

1. max_budget을 아주 작게 건 키를 발급합니다. 한 호출 비용보다 조금 큰 0.0001달러로 둡니다

    ```s
    curl -s http://localhost:4000/key/generate \
      -H "Authorization: Bearer sk-dotoryeee-1234" -H "Content-Type: application/json" \
      -d '{"key_alias":"dotoryeee-budget-key","models":["llama-small"],"max_budget":0.0001}'
    {"key_alias":"dotoryeee-budget-key","max_budget":0.0001,"spend":0.0}
    ```

2. 이 키로 호출을 반복하면 누적 spend가 예산을 넘는 순간 차단됩니다. 응답 코드는 400이 아니라 429이고 type이 budget_exceeded입니다

    ```s
    call 1 -> HTTP:200
    call 2 -> HTTP:200
    call 3 -> HTTP:429
      {"error":{"message":"Budget has been exceeded! Key=dotoryeee-budget-key
       (sk-...yC7w) Current cost: 0.000126, Max budget: 0.0001",
       "type":"budget_exceeded"}}
    ```

!!! warning
    💡 spend 반영이 비동기라 예산 직전 한두 건은 통과한 뒤 차단됩니다

## 시맨틱 캐시 설정 예시

---

지금까지의 redis 캐시는 요청을 해시로 비교하는 완전 일치 방식이라 프롬프트가 한 글자만 달라도 miss가 됩니다. 시맨틱 캐시(Semantic Cache)는 프롬프트를 임베딩으로 바꿔 유사도가 임계값 이상이면 히트로 처리합니다. 실측에는 임베딩 모델이 필요해 아래는 실행 결과가 아니라 설정 예시입니다.

```yaml title="litellm_config.yaml"
litellm_settings:
  cache: true
  cache_params:
    type: redis-semantic                          # 완전 일치 대신 의미 유사도로 매칭
    similarity_threshold: 0.8                      # 0.8 이상이면 히트로 간주 (설정 예시)
    redis_semantic_cache_embedding_model: my-embed # model_list에 등록된 임베딩 모델
```

임계값이 낮을수록 더 느슨하게 히트해 절감폭은 커지지만 엉뚱한 답을 재사용할 위험도 함께 올라갑니다. "리스트를 정렬하는 법"과 "파이썬에서 리스트 정렬"처럼 표현만 다른 질문을 한 답으로 묶고 싶을 때 씁니다.

## 캐시 운영 주의점

---

- TTL은 cache_params에 ttl로 초 단위 만료를 걸고, 요청별로 cache의 ttl이나 s-maxage로 덮어쓸 수 있습니다. 기본은 만료가 없어 값이 바뀌지 않는 질문에만 오래 두는 것이 안전합니다
- supported_call_types로 캐시를 적용할 엔드포인트를 좁힐 수 있습니다. 기본은 completion과 embedding을 포함한 전 유형이 켜져 있습니다
- 스트리밍 응답도 캐시돼 히트 시 저장된 내용을 청크로 재생하므로 앱 코드는 스트리밍인지 캐시인지 구분하지 않아도 됩니다

!!! warning
    💡 사용자·시간에 따라 답이 달라지는 요청은 캐시하면 오답을 재사용하니 TTL을 짧게 둡니다

## 결론

---

- redis 캐시 한 줄 설정으로 동일 요청의 두 번째 호출이 1.45초에서 0.004초로 줄고 토큰 비용은 0이 되었습니다
- 커스텀 단가는 Ollama처럼 무료 백엔드에서도 비용 추적을 흉내낼 수 있게 하고, key/info의 spend로 키별 누적을 확인합니다
- max_budget은 초과 시 429 budget_exceeded로 호출을 끊어 예산을 강제합니다. 완전 일치가 아쉬우면 시맨틱 캐시로 유사 질문까지 묶습니다
- 다음 편에서는 가드레일로 프롬프트 인젝션과 민감정보 유출을 게이트웨이 단에서 막는 방법을 다룹니다
- 캐시는 "같은 답은 다시 만들지 않기", 예산은 "정해진 만큼만 쓰기"로 나눠 두면 비용 설계가 헷갈리지 않습니다
