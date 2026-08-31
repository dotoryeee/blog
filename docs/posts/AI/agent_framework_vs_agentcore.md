---
draft: false
date: 2026-08-31
authors:
  - dotoryeee
categories:
  - AI
tags:
  - AI Agent
  - LangChain
  - LangGraph
  - PydanticAI
  - Strands Agents
  - Bedrock AgentCore
  - Bedrock
description: "LangChain 1.x, LangGraph 1.2, Pydantic AI 2.x, Strands Agents, Bedrock AgentCore를 라이선스, 실행 모델, 내구 실행, HITL, 멀티에이전트, MCP, Bedrock 지원, 관측성, 배포, 비용, 서울 리전까지 30여 개 범주 표로 비교하고 상황별로 무엇을 쓸지 정리"
---

# LangChain, LangGraph, Pydantic AI, Strands, Bedrock AgentCore 비교

이름이 겹쳐 헷갈리는 LangChain 1.x, LangGraph 1.2, Pydantic AI 2.x, Strands Agents와 프레임워크가 아닌 관리형 인프라 Bedrock AgentCore를 층 관계부터 정리하고 30여 개 범주 표로 비교한 뒤 상황별로 무엇을 쓸지 정리했다(수치와 버전은 2026년 8월 말 1차 출처 기준).

<!-- more -->

## 관계 먼저

| 이름 | 층 | 한 줄 정의 |
|---|---|---|
| LangChain 1.x | 고수준 프레임워크 | `create_agent`로 도구 호출 루프를 만드는 라이브러리. 내부적으로 LangGraph 그래프를 컴파일해 반환 |
| LangGraph 1.2 | 저수준 런타임 | 상태 그래프로 제어 흐름을 직접 짜는 라이브러리. LangChain 없이 단독 사용 가능 |
| LangSmith | 상용 플랫폼 | 트레이싱, 평가, 배포(구 LangGraph Platform), Studio. 프레임워크가 아님 |
| Pydantic AI 2.x | 프레임워크 | 타입 계약 중심 에이전트 라이브러리. Pydantic 팀 |
| Strands Agents | 프레임워크 | 모델 주도 루프 중심 에이전트 SDK. AWS 오픈소스 |
| Bedrock AgentCore | 관리형 인프라 | 세션 격리 런타임, 메모리, 게이트웨이, 아이덴티티, 관측성 등. 프레임워크 무관 |

AgentCore의 구성 요소와 Bedrock Agents Classic 유지보수 모드는 [AI 에이전트 개발 스택 OSS 생태계와 AWS Bedrock 비교](ai_agent_stack_compare.md) 글에 있으므로 여기서는 반복하지 않음

---

## 기능 비교표

각 셀은 1차 출처(문서, PyPI, 릴리스 노트)로 확인한 내용. 정성 평가인 행은 셀 안에 표시

| 범주 | LangChain 1.x | LangGraph 1.2 | Pydantic AI 2.x | Strands Agents | Bedrock AgentCore(관리형 인프라, 프레임워크 아님) |
|---|---|---|---|---|---|
| 라이선스 | MIT | MIT(라이브러리) | MIT | Apache 2.0(AWS) | 상용 AWS 서비스. 종량 과금 |
| 상업 이용 시 주의 | 라이브러리 자체는 제약 없음 | 라이브러리는 MIT지만 Agent Server 패키지 langgraph api(0.13.2)는 Elastic License 2.0(OSI 비승인). 셀프호스트 프로덕션 서버는 라이선스 키 필수(Enterprise) | 제약 없음 | 제약 없음 | AWS 이용 약관 |
| 최신 버전 | PyPI 1.3.18 | PyPI 1.2.11 | PyPI 2.36.0 | GitHub 릴리스 python/v1.54.0 | 서비스라 버전 없음 |
| 주요 날짜 | 1.0 출시 2025년 10월 | 1.0 출시 2025년 10월(LangChain과 동시) | v2.0 출시 2026년 6월 23일 | 오픈소스 2025년 5월, 1.0 2025년 7월 15일. 최신 릴리스 2026년 8월 27일 | GA 2025년 10월. 관리형 Harness GA 2026년 7월 |
| 패키지, 의존관계 | `langchain`이 langchain core(1.6 이상 2 미만)와 langgraph(1.2.11 이상 1.3 미만)에 필수 의존. 레거시(체인, 리트리버, 인덱싱, 허브, community)는 langchain classic으로 분리 | langchain core, langgraph checkpoint, langgraph prebuilt, langgraph sdk, pydantic, xxhash에 의존. `langchain` 패키지에는 의존하지 않음 | 코어 경량화. Bedrock 등 제공자는 선택 설치 extra. 별도 Harness 라이브러리 | strands agents와 strands agents tools 두 패키지. TypeScript SDK 별도. 저장소명은 harness sdk로 개명 | boto3 SDK와 AgentCore 스타터 툴킷. 프레임워크 무관 |
| 추상화 수준 | 고수준. 에이전트 하나를 함수 호출 하나로 | 저수준. 노드, 엣지, 상태를 직접 설계 | 중간. 에이전트 클래스 + 타입 계약. 그래프가 필요하면 pydantic graph | 중간. 에이전트 클래스 + 모델 주도 루프 | 해당 없음. 코드가 아니라 실행 환경 |
| 성격 | 라이브러리 | 라이브러리(런타임). 별도로 상용 Agent Server | 라이브러리 | 라이브러리. 프로세스 내 실행, 호스팅 컨트롤플레인 없음 | 관리형 서비스 묶음 |
| 실행 모델 | 모델 호출 → tool_calls 파싱 → 도구 실행 → 메시지 추가 → 도구 호출이 없을 때까지 반복 → `response_format` 검증 | StateGraph. 파이썬 함수 노드, 엣지, 조건 분기, 서브그래프, 병렬 브랜치 | 에이전트 실행 루프. 출력 스키마 검증 실패 시 자동 재시도, `ModelRetry`로 모델 자기수정 | 모델 주도 루프. 모델이 도구 선택과 종료를 결정 | Runtime이 세션별 격리 microVM에서 코드를 실행. 루프는 올린 프레임워크가 담당 |
| 상태 저장 | `checkpointer`, `store`, `state_schema` 인자로 LangGraph 영속화를 그대로 사용 | 체크포인터 Memory, SQLite, Postgres. 슈퍼스텝 단위 스냅샷 | `RunContext` 의존성 주입. 실행 상태 영속화는 내구 실행 capability에 위임 | SessionManager File, S3, AgentCore Memory. 대화 관리자(슬라이딩 윈도우, 요약) | Memory 서비스(단기, 장기). 프레임워크 세션 백엔드로 연결 |
| 내구 실행(크래시 후 재개) | LangGraph 체크포인터 의존 | 체크포인터로 재개와 타임 트래블. 자동 재개 감독은 없음. Temporal LangGraph 플러그인 존재 | Temporal, DBOS, Prefect가 1st party capability. Restate, Kitaru, Airflow 통합 추가 | 세션 매니저로 대화 복원. 내구 실행 엔진은 내장하지 않음 | Runtime 세션은 최대 8시간. 장기 실행은 Instances(EC2 기반, 서울 미지원). 내구 실행 엔진은 아님 |
| 체크포인트 단위와 제약 | LangGraph와 동일 | 슈퍼스텝 단위 저장이라 노드 내부 부작용은 멱등해야 함 | DBOS 기준: 별도 서버 없이 프로세스 내, 저장소 Postgres 또는 SQLite. 실행 중 스트리밍 버퍼링, pickle 직렬화 약 2MB, 모델 인스턴스는 문자열 ID로, CancellationToken 불가, MCP 툴셋은 생성 시 고정 | 세션 단위 | 세션 단위 |
| HITL(사람 개입) | 내장 미들웨어 HumanInTheLoop | `interrupt`로 연결을 끊고 대기했다가 재개 | `DeferredToolRequests`, `DeferredToolResults` | Interrupts(hook 또는 도구에서 발생) | 프레임워크 기능에 의존. Policy 서비스로 도구 호출 정책 제어 |
| 스트리밍 | LangGraph 스트리밍 이벤트 사용 | 스트리밍 이벤트(토큰, 상태 업데이트) | `iter()`, `run_stream()` | 스트리밍 응답 지원 | Runtime이 스트리밍 응답 전달 |
| 멀티에이전트 패턴 | `create_agent` 결과를 LangGraph 노드로 배치 | 서브그래프, 병렬 브랜치, 조건 분기로 직접 구성 | 기본은 에이전트를 도구로 감싸는 위임. 그래프는 pydantic graph | Agents as Tools, Handoffs, Swarm, Graph, Workflow, A2A | 관리형 Harness는 에이전트를 도구로 감싸는 위임만. 커스텀 오케스트레이터는 Runtime에 코드 배포 |
| 구조화 출력 | `response_format` → `structured_response` | 상태 스키마(pydantic, TypedDict) | `Agent[Deps, Output]` 제네릭. 출력 스키마가 계약 | Pydantic 기반 구조화 출력 | 해당 없음 |
| 타입 안전 | 중간. 미들웨어와 상태는 타입 지정 가능 | 상태 스키마 수준 | 가장 강함. 제네릭으로 의존성과 출력 타입 고정, 검증 실패 자동 재시도 | Pydantic 모델 수준 | 해당 없음 |
| 도구 정의 | `@tool`, `init_chat_model`, `trim_messages`, `init_embeddings` 유틸 | `langgraph.prebuilt`의 ToolNode, tools_condition(구 create_react_agent는 `create_agent`로 대체 중) | 데코레이터 도구, `UsageLimits`로 호출 상한 | 데코레이터 도구, strands agents tools 패키지, steering handler, guardrails | Gateway가 REST와 Lambda를 MCP 도구로 노출. 내장 도구 Browser, Code Interpreter |
| MCP | 지원(어댑터) | 지원(어댑터) | 지원 | 1급 지원 | Gateway가 MCP 서버 역할 |
| A2A | 별도 | 별도 | 별도 | 지원 | Agent Registry는 서울 미지원 |
| 모델 제공자 | 제공자 패키지 방식(langchain aws 등) | 모델 중립. LangChain 채팅 모델 사용 | 제공자 중립. 제공자별 선택 설치 | Bedrock Converse 기본 제공자. 다른 제공자도 지원 | 프레임워크가 호출. Bedrock 외 모델도 Runtime에서 호출 가능 |
| Bedrock, Amazon Nova | langchain aws의 `ChatBedrockConverse`가 Nova 지원. 프롬프트 캐싱 미들웨어 있음(Nova는 TTL 5분만). 단 `create_agent` + Nova(Llama4, GPT OSS 포함)에서 스트리밍 토큰과 도구 실행 오류가 공식 포럼에 보고됨(2025년 11월 등록, 2026년 7월 재보고, 해결 게시 없음). 미해결로 보임 | LangChain 모델을 그대로 사용하므로 좌측과 동일 | `BedrockConverseModel` + `BedrockProvider`(boto3 클라이언트 주입 가능) | 기본 제공자. 기본 모델 ID는 Claude이므로 Nova는 model_id 지정 | Bedrock과 같은 계정, IAM으로 자연스럽게 결합 |
| 관측성 | LangSmith(상용) 또는 OpenTelemetry | LangSmith 또는 OpenTelemetry | Logfire 또는 OpenTelemetry | OpenTelemetry 내장 | Observability 서비스(CloudWatch 기반, CloudWatch 요금) |
| 테스트 더블 | 가짜 채팅 모델(langchain core) | 노드 단위 함수 테스트 | `TestModel`, `FunctionModel` | 모의 모델 제공자 | 로컬 스타터 툴킷으로 실행 |
| 배포 형태 | 아무 파이썬 런타임. Agent Server를 쓰면 LangSmith Deployment | 라이브러리는 어디서나. Agent Server 셀프호스트는 langgraph api 이미지 + PostgreSQL + Redis, k8s Helm 권장 | 아무 파이썬 런타임. AgentCore Runtime 포함 | AgentCore, Lambda, Fargate, EKS, Docker | Runtime 자체가 배포 대상 |
| 상용 컴포넌트 | LangSmith(선택) | LangSmith Deployment, Studio(선택). `langgraph dev` 로컬 개발은 무료 계정으로 가능 | Logfire(선택) | 없음 | 서비스 전체가 상용 |
| 비용 | 라이브러리 무료. LangSmith Developer $0(1좌석, 월 5k 트레이스), Plus $39/좌석(월 10k 트레이스, 소형 서버리스 배포 1개 포함), Enterprise 견적. 배포 종량 LCU $1.50, LSU $1.00 | 좌측과 동일 | 라이브러리 무료 | 라이브러리 무료 | Runtime vCPU 시간당 $0.0895 + GB 시간당 $0.00945, 초 단위(유휴와 I/O 대기 무료). Memory 단기 1k 이벤트당 $0.25, 장기 1k 레코드당 월 $0.75 + 1k 검색당 $0.50. Gateway 1k 호출당 $0.005. Harness 별도 요금 없음 |
| 리전(서울 기준) | 라이브러리라 무관 | 무관 | 무관 | 무관 | 서울 지원: Runtime microVM, Memory, Gateway, Identity, 내장 도구, Observability, Policy, Evaluations, Harness. 미지원: Runtime Instances, Web Search, payments, Agent Registry |
| VPC, PrivateLink | 무관 | 무관 | 무관 | 무관 | Runtime VPC 2025년 9월, Gateway와 Identity VPC egress 2026년 4월 지원 |
| 실행 시간 한도 | 런타임에 따름 | 런타임에 따름 | 런타임에 따름 | 런타임에 따름 | Runtime 세션 최대 8시간. 장기형은 Instances |
| 학습 곡선(정성 평가) | 낮음. 함수 하나로 시작 | 높음. 그래프 설계와 상태 관리 필요 | 중간. 타입과 Pydantic에 익숙하면 낮음 | 낮음에서 중간. 모델 주도 루프라 코드 적음 | 중간. IAM, 서비스 조합 이해 필요 |
| 커뮤니티, 성숙도(정성 평가) | 가장 큰 생태계, 1.0으로 API 안정화 | 넓은 채택, 1.x 안정 | 빠르게 성장, v2로 구조 재편 직후 | AWS 주도, 1년 남짓, 릴리스 빈번 | GA 1년 미만, 기능 추가 빠름 |
| 대표 적합 사례 | 도구 몇 개 붙은 단일 에이전트를 빠르게 | 커스텀 상태와 분기가 많은 오케스트레이션 | 출력 계약과 검증이 중요한 백엔드 통합 | AWS 네이티브 스택에서 멀티에이전트 | 프레임워크는 정했고 세션 격리, 메모리, 도구 게이트웨이, 관측성 인프라만 필요할 때 |
| 부적합 사례 | 그래프 수준의 세밀한 제어 | 단순 도구 호출 봇(과설계) | 그래프 중심 복잡 오케스트레이션 단독 | AWS 밖 환경 우선, 상용 컨트롤플레인 기대 | 프레임워크 대체 기대, 서울에서 Instances나 Registry 필요 |
| 알려진 주의점 | Nova 스트리밍 이슈(위), 레거시는 langchain classic | Agent Server 라이선스와 인프라 요구 | v1.100 이상에서 deprecation 정리 후 v2로 올리는 업그레이드 경로 | 저장소 개명으로 문서 링크 혼선 가능 | Bedrock Agents Classic은 유지보수 모드. 신규는 AgentCore로(상세는 스택 생태계 글) |

---

## 언제 무엇을 쓰나

단일 툴콜 에이전트를 빠르게 만들 때. LangChain 1.x `create_agent`가 가장 짧음. 모델, 도구, 시스템 프롬프트, 미들웨어만 넘기면 컴파일된 그래프가 나오고 `.invoke`로 끝. 요약, PII 마스킹, 재시도, 모델 폴백, 호출 상한 같은 운영 기능이 내장 미들웨어로 있어 초기 비용이 낮음. Bedrock에서 Nova를 쓸 계획이면 포럼에 보고된 스트리밍 이슈를 먼저 재현해 볼 것

커스텀 상태와 그래프 오케스트레이션이 필요할 때. LangGraph 직접 사용. 조건 분기, 병렬 브랜치, 서브그래프, 슈퍼스텝 체크포인트, `interrupt` 기반 HITL을 코드로 명시. `create_agent`로 만든 에이전트를 노드로 넣어 상위 그래프를 짜는 조합이 자연스러움. 셀프호스트 Agent Server가 필요해지는 시점에 라이선스와 Postgres, Redis 인프라를 감안

타입 계약과 검증이 중심일 때. Pydantic AI. `Agent[Deps, Output]`으로 입력 의존성과 출력 스키마를 타입으로 고정하고, 검증 실패 시 자동 재시도와 `ModelRetry`로 모델이 스스로 고치게 함. 내구 실행이 필요하면 Temporal, DBOS, Prefect capability를 붙이되 스트리밍 버퍼링과 직렬화 크기 제약을 확인. `TestModel`, `FunctionModel`로 LLM 없이 단위 테스트가 되는 점이 CI에서 큼

AWS 네이티브에 Bedrock 최적일 때. Strands Agents. Bedrock Converse가 기본 제공자이고 SessionManager가 S3와 AgentCore Memory를 바로 지원. Swarm, Graph, Workflow, A2A까지 멀티에이전트 패턴이 내장. OpenTelemetry가 기본이라 CloudWatch로 바로 연결. 배포는 AgentCore, Lambda, Fargate, EKS 어디든

실행 인프라만 필요할 때. Bedrock AgentCore. 프레임워크는 이미 정했고 세션 격리, 8시간 세션, 메모리, REST를 MCP 도구로 바꾸는 Gateway, Identity, 관측성이 필요하면 Runtime에 올림. 프레임워크 무관이므로 코드 변경 없이 올라감. 서울에서 Instances와 Agent Registry가 아직 없다는 점만 확인

섞어 쓰는 패턴

| 조합 | 형태 | 이유 |
|---|---|---|
| LangGraph 상위 그래프 + `create_agent` 워커 | 라우팅과 상태는 그래프가, 각 노드의 도구 호출 루프는 `create_agent`가 | 저수준 제어와 고수준 편의를 동시에 |
| Pydantic AI 앱 + AgentCore Runtime | 타입 계약은 앱이, 세션 격리와 메모리, 게이트웨이는 AgentCore가 | 프레임워크와 인프라 분리 |
| Strands + AgentCore Memory + Gateway | SessionManager를 AgentCore Memory로, 사내 REST를 Gateway로 MCP 도구화 | 같은 AWS 계정 안에서 IAM 하나로 |
| Pydantic AI + DBOS 또는 Temporal | 에이전트 실행을 내구 실행 엔진으로 감쌈 | 크래시 후 재개, 장시간 HITL 대기 |
| LangGraph + Temporal 플러그인 | 노드를 Activity로 실행 | 체크포인터 대신 엔진이 재개 감독 |
| 아무 프레임워크 + OpenTelemetry + 원하는 백엔드 | LangSmith, Logfire, CloudWatch 중 선택 | 프레임워크와 관측성 백엔드 결합 해제 |

---

## 흔한 오해

| 오해 | 실제 |
|---|---|
| LangGraph = LangChain + LangSmith | LangGraph는 독립 런타임 라이브러리. `langchain` 패키지에 의존하지 않고, LangSmith는 별도 상용 플랫폼 |
| LangGraph를 쓰려면 LangSmith가 필수 | 라이브러리는 MIT이고 어디서나 실행. LangSmith는 트레이싱과 배포를 원할 때만. `langgraph dev` 로컬 개발도 무료 계정으로 가능 |
| MIT니까 서버도 자유롭게 셀프호스트 | 라이브러리는 MIT지만 Agent Server 패키지 langgraph api는 Elastic License 2.0. 프로덕션 셀프호스트는 Enterprise 라이선스 키 필요 |
| AgentCore가 Strands나 LangGraph를 대체한다 | AgentCore는 실행 인프라. 루프와 오케스트레이션은 여전히 프레임워크 몫. 관리형 Harness는 설정형 에이전트이고 멀티에이전트는 위임 패턴만 |
| LangGraph Platform이라는 제품이 따로 있다 | 2025년 10월에 LangSmith Deployment로, LangGraph Studio는 LangSmith Studio로 개명 |

---

## 결론

- LangChain은 LangGraph 위의 고수준 API, LangGraph는 런타임, LangSmith는 상용 플랫폼. 셋을 층으로 보면 혼란이 사라짐
- Pydantic AI는 타입 계약, Strands는 AWS 네이티브 멀티에이전트, LangGraph는 세밀한 그래프 제어가 강점
- 다섯 개 중 하나를 고르는 문제가 아니라 프레임워크 하나 + AgentCore 인프라 사용 여부로 나눠 결정
- 라이선스는 라이브러리(MIT, Apache 2.0)와 서버 컴포넌트(Elastic License, 상용 서비스)를 분리해서 볼 것
- 서울 리전은 AgentCore 핵심 서비스는 지원하지만 Instances, Web Search, payments, Agent Registry는 아직 없음

## 출처

- Pydantic AI: [내구 실행 개요](https://pydantic.dev/docs/ai/integrations/durable_execution/overview/), [DBOS capability](https://pydantic.dev/docs/ai/capabilities/durable_execution/dbos/), [v2 발표](https://pydantic.dev/articles/pydantic-ai-v2), [PyPI](https://pypi.org/pypi/pydantic-ai/json)
- LangGraph: [PyPI langgraph](https://pypi.org/pypi/langgraph/json), [PyPI langgraph api](https://pypi.org/pypi/langgraph-api/json), [Standalone Server 배포](https://docs.langchain.com/langsmith/deploy-standalone-server), [제품명 변경 공지](https://changelog.langchain.com/announcements/product-naming-changes-langsmith-deployment-and-langsmith-studio), [라이선스 분석 글](http://rvernica.github.io/2026/03/langchain-license)
- LangChain: [PyPI](https://pypi.org/pypi/langchain/json), [v1 릴리스 노트](https://docs.langchain.com/oss/python/releases/langchain-v1), [Agents](https://docs.langchain.com/oss/python/langchain/agents), [Middleware](https://docs.langchain.com/oss/python/langchain/middleware), [Custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom), [1.0 블로그](https://www.langchain.com/blog/langchain-langgraph-1dot0), [Bedrock Nova 이슈 포럼](https://forum.langchain.com/t/langchain-v1-agentic-flow-on-bedrock-fails-for-non-claude-models-available-in-bedrock-llama4-nova-gpt-oss/2251)
- LangSmith: [요금](https://www.langchain.com/pricing), [OpenTelemetry 트레이싱](https://docs.langchain.com/langsmith/trace-with-opentelemetry)
- Strands: [1.0 발표](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-1-0-production-ready-multi-agent-orchestration-made-simple/), [공식 사이트](https://strandsagents.com/), [GitHub](https://github.com/strands-agents/harness-sdk), [Interrupts](https://strandsagents.com/docs/user-guide/concepts/interrupts/), [최신 릴리스](https://api.github.com/repos/strands-agents/harness-sdk/releases/latest)
- AgentCore: [리전](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html), [릴리스 노트](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html), [요금](https://aws.amazon.com/bedrock/agentcore/pricing/), [GA 공지](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available)
