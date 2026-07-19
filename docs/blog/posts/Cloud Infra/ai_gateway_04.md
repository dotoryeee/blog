---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - Cloud
  - AI
---

# AI Gateway 라우팅과 폴백 전략

<!-- more -->

## 목표

---

- 3편 끝에서 예고한 라우팅·폴백(Routing·Fallback) 전략을 2편 랩 환경에서 직접 실측해봅니다
- 같은 별칭에 백엔드 두 개를 묶어 로드밸런싱하고 weight와 routing_strategy로 분산을 조정합니다
- 재시도·타임아웃과 2단 폴백 체인을 응답 헤더와 컨테이너 로그로 검증합니다

!!! tip
    💡 2편에서 띄운 ollama·litellm 스택을 그대로 쓰므로 추가 비용이 없습니다

## 로드밸런싱

---

2편에서는 llama-small, qwen-small처럼 별칭 하나에 백엔드 하나를 붙였습니다. 로드밸런싱은 같은 별칭에 여러 배포(Deployment)를 등록해 하나의 모델 그룹(Model Group)으로 묶는 방식입니다.

1. 2편 model_list에 chat-small 그룹을 추가합니다. model_name이 같은 항목 두 개가 한 그룹이 됩니다

    ```s
    vi litellm_config.yaml
    ```

    ```yaml title="litellm_config.yaml"
    model_list:
      - model_name: chat-small          # 같은 별칭 = 하나의 모델 그룹
        litellm_params:
          model: ollama/llama3.2:1b
          api_base: http://ollama:11434
      - model_name: chat-small
        litellm_params:
          model: ollama/qwen2.5:0.5b
          api_base: http://ollama:11434

    router_settings:
      routing_strategy: simple-shuffle   # 기본값, 가중치 기반 무작위 분산
    ```

2. 게이트웨이를 재시작하고 chat-small로 10회 호출하면서 x-litellm-model-name 헤더로 어느 백엔드가 처리했는지 확인합니다

    ```s
    docker compose restart litellm

    for i in $(seq 1 10); do
      curl -s -D - -o /dev/null http://localhost:4000/v1/chat/completions \
        -H "Authorization: Bearer sk-dotoryeee-1234" -H "Content-Type: application/json" \
        -d '{"model":"chat-small","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' \
        | grep -i x-litellm-model-name
    done

    x-litellm-model-name: ollama/llama3.2:1b
    x-litellm-model-name: ollama/llama3.2:1b
    x-litellm-model-name: ollama/qwen2.5:0.5b
    x-litellm-model-name: ollama/llama3.2:1b
    x-litellm-model-name: ollama/llama3.2:1b
    x-litellm-model-name: ollama/llama3.2:1b
    x-litellm-model-name: ollama/qwen2.5:0.5b
    x-litellm-model-name: ollama/llama3.2:1b
    x-litellm-model-name: ollama/qwen2.5:0.5b
    x-litellm-model-name: ollama/llama3.2:1b
    ```

    요청 model은 계속 chat-small 하나인데 llama 7회, qwen 3회로 두 백엔드에 나뉘어 처리되었습니다.

3. 응답 헤더 전체를 보면 실제 처리한 배포의 id·모델·api_base와 소속 그룹이 함께 내려옵니다

    ```s
    ... | grep x-litellm-model

    x-litellm-model-id: 0aee5afdf1859546955d201eec6096e9214ce13d568906d08889fdcba9644a30
    x-litellm-model-name: ollama/qwen2.5:0.5b
    x-litellm-model-api-base: http://ollama:11434
    x-litellm-model-group: chat-small
    ```

!!! notice
    💡 두 배포가 같은 api_base라 분산은 x-litellm-model-name으로 구분합니다

## 가중치와 라우팅 전략

---

1. 특정 배포로 트래픽을 더 몰고 싶으면 weight를 지정합니다. qwen에 3, llama에 1을 주면 qwen이 3배 자주 선택됩니다

    ```yaml title="litellm_config.yaml"
    model_list:
      - model_name: chat-small
        litellm_params:
          model: ollama/llama3.2:1b
          api_base: http://ollama:11434
          weight: 1
      - model_name: chat-small
        litellm_params:
          model: ollama/qwen2.5:0.5b
          api_base: http://ollama:11434
          weight: 3
    ```

2. 재시작 후 20회 호출하면 지정한 1:3 비율에 맞게 갈립니다

    ```s
    # chat-small 20회 호출 집계
    llama3.2:1b  (weight 1) : 5
    qwen2.5:0.5b (weight 3) : 15
    ```

3. routing_strategy를 latency-based-routing으로 바꾸면 최근 응답이 빠른 배포를 우선합니다. 0.5b인 qwen이 1b인 llama보다 빨라 트래픽이 qwen으로 쏠립니다

    ```yaml title="litellm_config.yaml"
    router_settings:
      routing_strategy: latency-based-routing   # 최근 지연이 낮은 배포 우선
    ```

4. 워밍업 호출로 지연 표본을 쌓은 뒤 12회 호출한 집계입니다

    ```s
    # latency-based-routing, 워밍업 후 12회 호출 집계
    llama3.2:1b  : 1
    qwen2.5:0.5b : 11
    ```

    simple-shuffle의 절반씩 분산과 달리 대부분 빠른 qwen으로 갔습니다. 전략 한 줄로 분산 기준이 무작위에서 지연 기반으로 바뀝니다.

## 재시도와 타임아웃

---

배포가 실패하거나 느릴 때 게이트웨이가 어떻게 버티는지 정하는 값들입니다.

1. router_settings에 재시도·타임아웃·쿨다운을 함께 둡니다

    ```yaml title="litellm_config.yaml"
    router_settings:
      routing_strategy: simple-shuffle
      num_retries: 2        # 실패 시 그룹 내 다른 배포로 최대 2회 재시도
      timeout: 30           # 30초 초과 시 Timeout 처리
      allowed_fails: 3      # 1분 내 3회 실패하면 쿨다운 진입
      cooldown_time: 30     # 30초 동안 해당 배포를 라우팅에서 제외
    ```

2. 타임아웃을 확인하려고 timeout을 1로 낮추고 qwen-small에 긴 답변을 요청하면 1초에서 잘립니다

    ```s
    curl -s http://localhost:4000/v1/chat/completions \
      -H "Authorization: Bearer sk-dotoryeee-1234" -H "Content-Type: application/json" \
      -d '{"model":"qwen-small","messages":[{"role":"user","content":"Write a long essay."}],"max_tokens":300}'

    {"error":{"message":"litellm.APIConnectionError: OllamaException - litellm.Timeout:
     Connection timed out. Timeout passed=1.0, time taken=1.001 seconds. ..."}}
    ```

3. num_retries는 로그로 확인합니다. 고장난 백엔드로 요청하면 지정한 횟수만큼 재시도한 기록이 남습니다

    ```s
    docker logs litellm 2>&1 | grep "Retried"

    ... LiteLLM Retried: 2 times, LiteLLM Max Retries: 2
    ```

allowed_fails와 cooldown_time은 그룹에 정상 배포가 남아 있을 때 효과가 드러납니다. 고장난 배포가 allowed_fails를 넘겨 실패하면 cooldown_time 동안 후보에서 빠지고, 재시도가 정상 배포로 넘겨 앱은 200을 받습니다. 배포가 하나뿐이거나 전부 죽은 경우엔 그룹이 비지 않도록 쿨다운을 걸지 않습니다.

!!! warning
    💡 timeout 검증시 값을 1로 낮췄다가 확인 후 원래 값으로 되돌립니다

## 폴백 체인

---

2편의 폴백은 llama-small이 죽으면 qwen-small로 넘기는 1단이었습니다. 폴백은 후보를 순서대로 이어 체인으로 늘릴 수 있습니다.

1. primary가 죽으면 backup, 그다음 standby로 넘어가는 2단 체인을 정의합니다. 검증을 위해 primary와 backup은 열려있지 않은 포트로 두고 standby만 정상 백엔드에 붙입니다

    ```yaml title="litellm_config.yaml"
    model_list:
      - model_name: primary
        litellm_params:
          model: ollama/llama3.2:1b
          api_base: http://ollama:11435    # 고장
      - model_name: backup
        litellm_params:
          model: ollama/llama3.2:1b
          api_base: http://ollama:11436    # 고장
      - model_name: standby
        litellm_params:
          model: ollama/qwen2.5:0.5b
          api_base: http://ollama:11434    # 정상

    router_settings:
      num_retries: 2
      fallbacks:
        - primary: ["backup", "standby"]   # primary → backup → standby
    ```

2. primary로 요청해도 200이 돌아옵니다. 헤더를 보면 primary와 backup을 건너뛰고 standby가 처리했습니다

    ```s
    curl -s -D - -o /dev/null http://localhost:4000/v1/chat/completions \
      -H "Authorization: Bearer sk-dotoryeee-1234" -H "Content-Type: application/json" \
      -d '{"model":"primary","messages":[{"role":"user","content":"Reply with OK."}],"max_tokens":10}' \
      | grep x-litellm-model

    x-litellm-model-name: ollama/qwen2.5:0.5b
    x-litellm-model-api-base: http://ollama:11434
    x-litellm-model-group: standby
    ```

3. 컨테이너 로그에는 backup까지 재시도하고 실패한 뒤 체인을 넘어간 흔적이 남습니다

    ```s
    docker logs litellm 2>&1 | grep -E "Retried|Fallbacks"

    ... Fallbacks=[{'primary': ['backup', 'standby']}] LiteLLM Retried: 2 times, LiteLLM Max Retries: 2
    ```

컨텍스트 초과 같은 비일시적 오류는 재시도가 무의미하므로 별도 경로로 폴백합니다. 아래는 실측이 아니라 설정 예시입니다. 프롬프트가 모델의 컨텍스트 윈도우를 넘으면 context_window_fallbacks에 지정한 더 큰 모델로 곧장 넘깁니다.

```yaml title="litellm_config.yaml"
router_settings:
  context_window_fallbacks:
    - gpt-4o-mini: ["gpt-4o"]          # 컨텍스트 초과 시 더 큰 모델로 (설정 예시)
  content_policy_fallbacks:
    - gpt-4o: ["claude-3-5-sonnet"]    # 콘텐츠 정책 차단 시 타 모델로 (설정 예시)
```

## 결론

---

- 같은 model_name에 배포를 여러 개 등록하면 코드 변경 없이 하나의 모델 그룹으로 로드밸런싱됩니다
- weight는 분산 비율을, routing_strategy는 분산 기준(무작위·지연·사용량)을 정합니다
- num_retries·timeout·cooldown_time은 실패를 흡수하는 안전망이고, 폴백 체인은 배포가 순차로 죽어도 마지막 정상 후보까지 요청을 이어줍니다
- 다음 편에서는 캐싱과 비용 최적화로 같은 요청의 토큰 비용을 0으로 만드는 방법을 다룹니다
- 로드밸런싱은 "정상일 때 고르게", 폴백은 "고장났을 때 안 끊기게"로 나눠 두면 설정이 헷갈리지 않습니다
