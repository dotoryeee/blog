---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - Cloud
  - AI
---

# LiteLLM으로 AI Gateway 구축하기

<!-- more -->

## 목표

---

- AI Gateway를 로컬에서 직접 구축해봅니다
- LiteLLM Proxy 뒤에 Ollama 로컬 모델 2개를 붙여서 클라우드 비용 없이 진행합니다
- 통합 API 호출, virtual key 발급, rate limit 차단, 프로바이더 장애 폴백까지 실제로 동작을 확인합니다

!!! tip
    💡 백엔드가 Ollama 로컬 모델이라 API 키와 클라우드 비용이 전혀 들지 않습니다

## 구성

---

- LiteLLM Proxy: AI Gateway 본체, OpenAI 호환 엔드포인트 제공
- Ollama: 백엔드 LLM 서버 (llama3.2:1b, qwen2.5:0.5b 두 모델을 별도 프로바이더처럼 등록)
- PostgreSQL: virtual key 관리용 DB
- macOS의 Docker는 Metal GPU를 쓰지 못해 CPU 추론으로 동작하지만 게이트웨이 데모에는 충분합니다

!!! warning
    💡 네이티브 Ollama 설치 시 api_base를 host.docker.internal로 연결합니다

## 게이트웨이 구축

---

1. 작업 디렉터리를 생성하고 docker compose 파일을 작성합니다

    ```s
    mkdir ai-gateway-lab
    cd ai-gateway-lab
    vi docker-compose.yml
    ```

    ```yaml title="docker-compose.yml" linenums="1"
    services:
      ollama:
        image: ollama/ollama:latest
        container_name: ollama
        ports:
          - "11434:11434"
        volumes:
          - ollama_data:/root/.ollama

      db:
        image: postgres:16-alpine
        container_name: litellm_db
        environment:
          POSTGRES_USER: llmproxy
          POSTGRES_PASSWORD: dbpassword
          POSTGRES_DB: litellm
        volumes:
          - pg_data:/var/lib/postgresql/data

      litellm:
        image: ghcr.io/berriai/litellm:main-latest
        container_name: litellm
        ports:
          - "4000:4000"
        volumes:
          - ./litellm_config.yaml:/app/config.yaml
        command: ["--config", "/app/config.yaml", "--port", "4000"]
        environment:
          LITELLM_MASTER_KEY: sk-dotoryeee-1234    #관리자용 마스터 키
          UI_USERNAME: dotoryeee                     #Admin UI 로그인 계정
          DATABASE_URL: postgresql://llmproxy:dbpassword@db:5432/litellm
          STORE_MODEL_IN_DB: "True"
        depends_on:
          - ollama
          - db

    volumes:
      ollama_data:
      pg_data:
    ```

2. 게이트웨이 설정 파일을 작성합니다. 모델 별칭과 폴백 체인이 핵심입니다

    ```s
    vi litellm_config.yaml
    ```

    ```yaml title="litellm_config.yaml" linenums="1"
    model_list:
      - model_name: llama-small          # 게이트웨이에서 노출할 모델 별칭
        litellm_params:
          model: ollama/llama3.2:1b      # 실제 백엔드 모델
          api_base: http://ollama:11434

      - model_name: qwen-small
        litellm_params:
          model: ollama/qwen2.5:0.5b
          api_base: http://ollama:11434

    litellm_settings:
      drop_params: true

    router_settings:
      num_retries: 2
      fallbacks:
        - llama-small: ["qwen-small"]    # llama 실패 시 qwen으로 폴백
    ```

3. 스택을 기동하고 백엔드 모델 2개를 다운로드합니다

    ```s
    docker compose up -d
    docker exec ollama ollama pull llama3.2:1b
    docker exec ollama ollama pull qwen2.5:0.5b
    docker exec ollama ollama list
    NAME            ID              SIZE      MODIFIED
    qwen2.5:0.5b    a8b0c5157701    397 MB    Less than a second ago
    llama3.2:1b     baf6a787fdff    1.3 GB    45 seconds ago
    ```

4. 게이트웨이가 살아있는지, 모델이 등록됐는지 확인합니다

    ```s
    curl -s http://localhost:4000/health/liveliness
    "I'm alive!"

    curl -s http://localhost:4000/v1/models -H "Authorization: Bearer sk-dotoryeee-1234"
    {
        "data": [
            {"id": "llama-small", "object": "model", ...},
            {"id": "qwen-small", "object": "model", ...}
        ],
        "object": "list"
    }
    ```

## 통합 API 호출

---

1. OpenAI 호환 API로 호출합니다. 백엔드가 Ollama여도 앱 입장에서는 OpenAI SDK 그대로입니다

    ```s
    curl -s http://localhost:4000/v1/chat/completions \
      -H "Authorization: Bearer sk-dotoryeee-1234" \
      -H "Content-Type: application/json" \
      -d '{"model":"qwen-small","messages":[{"role":"user","content":"What is an API gateway? One sentence."}],"max_tokens":50}'
    ```

    ```json
    {
      "model": "qwen-small",
      "choices": [{"message": {"content": "An API (Application Programming Interface) gateway is a software component that enables APIs to be accessed and processed more efficiently..."}}],
      "usage": {"completion_tokens": 49, "prompt_tokens": 41, "total_tokens": 90}
    }
    ```

2. model 값만 바꾸면 다른 백엔드로 라우팅됩니다. 앱 코드 변경 없이 모델 교체가 되는 것이 통합 API의 핵심입니다

## Virtual Key 발급과 Rate Limit

---

1. 마스터 키로 팀용 virtual key를 발급합니다. 실제 백엔드 키는 게이트웨이만 알고, 앱에는 이 키만 배포합니다

    ```s
    curl -s http://localhost:4000/key/generate \
      -H "Authorization: Bearer sk-dotoryeee-1234" \
      -H "Content-Type: application/json" \
      -d '{"key_alias":"dotoryeee-key","models":["llama-small","qwen-small"],"rpm_limit":2}'
    {
      "key": "sk-2TLJ91iCDREGN_0mDJFFeA",
      "key_alias": "dotoryeee-key",
      "models": ["llama-small", "qwen-small"],
      "rpm_limit": 2
    }
    ```

2. 발급한 키를 Authorization 헤더에 넣고 연속 3회 호출하면 rpm_limit 2를 초과한 세 번째 요청이 차단됩니다

    ```s
    curl -s http://localhost:4000/v1/chat/completions \
      -H "Authorization: Bearer sk-2TLJ91iCDREGN_0mDJFFeA" \
      -H "Content-Type: application/json" \
      -d '{"model":"qwen-small","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'    #동일 요청 3회 반복

    call 1 -> HTTP:200
    call 2 -> HTTP:200
    call 3 -> HTTP:429
      에러: Rate limit exceeded for api_key: ebd5686b... Limit type: requests.
    ```

## 프로바이더 장애 폴백

---

1. llama-small의 api_base를 존재하지 않는 포트(11435)로 바꿔서 백엔드 장애를 만들고 게이트웨이를 재시작합니다

    ```s
    vi litellm_config.yaml    #api_base를 http://ollama:11435 로 변경
    docker compose restart litellm
    ```

2. 고장난 llama-small로 요청해도 폴백 덕분에 200 응답이 옵니다. 응답 헤더를 보면 실제로는 qwen이 처리했음을 확인할 수 있습니다

    ```s
    curl -s -D - http://localhost:4000/v1/chat/completions \
      -H "Authorization: Bearer sk-dotoryeee-1234" \
      -H "Content-Type: application/json" \
      -d '{"model":"llama-small","messages":[{"role":"user","content":"hi"}],"max_tokens":30}' | grep x-litellm

    x-litellm-model-name: ollama/qwen2.5:0.5b
    x-litellm-model-api-base: http://ollama:11434
    x-litellm-model-group: qwen-small
    ```

3. 앱은 장애를 전혀 모른 채 응답을 받습니다. 확인 후 api_base를 11434로 되돌립니다

!!! notice
    💡 폴백 검증시 응답 본문의 model 필드는 요청한 별칭을 그대로 보여주니 반드시 x-litellm 헤더로 확인합니다

## Admin UI 확인

---

1. http://localhost:4000/ui 에 접속해 dotoryeee 계정(비밀번호는 마스터 키)으로 로그인합니다

    ![login](ai_gateway_02/1.PNG)

2. Models 메뉴에 등록한 모델 2개가 올라와 있습니다

    ![model management](ai_gateway_02/2.PNG)

3. Virtual Keys 메뉴에는 발급한 키의 사용량과 예산이 표시됩니다

    ![virtual keys](ai_gateway_02/3.PNG)

    dotoryeee-key 키가 발급되어 있고 Spend 추적이 동작합니다

4. Logs 메뉴에서 요청별 처리 결과와 소요 시간을 추적할 수 있습니다

    ![request logs](ai_gateway_02/4.PNG)

    폴백 실습에서 발생시킨 Failure 기록까지 그대로 남아있습니다

## 결론

---

- 게이트웨이 하나로 통합 API, 키 관리, rate limit, 폴백이 전부 동작함을 확인했습니다
- 백엔드를 Ollama에서 OpenAI/Bedrock으로 바꿔도 model_list에 항목만 추가하면 됩니다. 당연히 앱 코드는 그대로입니다
