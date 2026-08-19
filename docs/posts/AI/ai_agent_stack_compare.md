---
draft: false
date: 2026-08-19
authors:
  - dotoryeee
categories:
  - AI
tags:
  - AI Agent
  - LangGraph
  - PydanticAI
  - Mem0
  - Langfuse
  - Bedrock
description: "에이전트 개발에 쓰는 오픈소스 도구를 오케스트레이션·에이전트·메모리·모델 실행·수집·저장소·안전 필터·모니터링 10개 레이어로 묶어 성격과 로컬 실행 여부를 표로 비교. Amazon Bedrock 관리형 서비스와의 대응도 정리"
---
# AI 에이전트 개발 스택 OSS 생태계와 AWS Bedrock 비교

에이전트를 만들 때 쓰는 오픈소스 도구를 레이어로 묶어 표로 정리했다. 빠른 이해를 위해 목적별로 묶어봤다. 마지막에는 같은 레이어를 AWS Bedrock으로 채우면 어떻게 되는지 대응시켰다.

<!-- more -->

## 오케스트레이션 프레임워크

LLM 호출과 검색, 도구 실행을 파이프라인으로 조립하는 상위 프레임워크다.

| 프레임워크 | 성격 | 주 언어 | 강점 영역 | 비고 |
|---|---|---|---|---|
| LangChain | 에이전트·LLM 앱 범용 프레임워크 | Python<br>JS·TS는 별도 라이브러리 | 모델·도구·벡터 저장소 통합량 | MIT. 최근 메이저부터 에이전트 실행 기능 내장 |
| LlamaIndex | 데이터 프레임워크. 인덱싱·검색 중심 | Python | 데이터 커넥터와 인덱스 구성 | MIT |
| Haystack | 파이프라인 그래프 오케스트레이션 | Python | 검색·라우팅·생성 단계를 명시적으로 조립 | Apache-2.0 |
| Semantic Kernel | 모델 중립 에이전트 오케스트레이션 SDK | C#, Python, Java 3종 공식 SDK | 엔터프라이즈 관측·보안 | MIT |

---

## 도구 연결 표준과 SDK

에이전트가 외부 도구, 다른 에이전트, 화면과 대화하는 방식을 정한 약속이다.

| 프로토콜 | 해결하는 연결 | 참여자 | 전송 | 비고 |
|---|---|---|---|---|
| MCP(Model Context Protocol) | 앱 ↔ 도구·데이터 | 호스트, 클라이언트, 서버 | stdio<br>Streamable HTTP | 데이터 계층은 JSON-RPC 2.0 |
| A2A(Agent2Agent) | 에이전트 ↔ 에이전트 | 클라이언트, 서버(원격 에이전트) | JSON-RPC, gRPC, HTTP+JSON 바인딩<br>스트리밍은 SSE | Apache-2.0 |
| AG-UI(Agent-User Interaction Protocol) | 에이전트 ↔ 프론트엔드 | 에이전트 백엔드, 사용자 화면 애플리케이션 | 전송 비종속. SSE·WebSocket·웹훅 | MIT. 이벤트 기반 계층 |

| SDK | 대상 프로토콜 | 성격 | PyPI | 비고 |
|---|---|---|---|---|
| FastMCP | MCP | MCP 서버·클라이언트 구축 프레임워크 | `fastmcp` | Apache-2.0. 초기 버전이 공식 SDK로 흡수된 뒤 독립 유지보수 |
| MCP Python SDK | MCP | 공식 Python 구현 | `mcp` | MIT. 최근 메이저 개편에서 FastMCP 클래스가 MCPServer로 개명 |

---

## 에이전트 프레임워크

오케스트레이션보다 아래에서 에이전트 하나가 어떻게 돌아가는지를 책임진다.

| 프레임워크 | 성격 | 제어 방식 | 모델 결합 | 로컬 모델 | 비고 |
|---|---|---|---|---|---|
| LangGraph | 라이브러리 | 상태와 노드, 엣지로 짜는 그래프 | 프로바이더 중립 | 가능 | MIT |
| PydanticAI | 라이브러리 | 타입 검증이 붙은 에이전트 루프 | 프로바이더 중립 | 가능 | MIT. 그래프가 필요하면 Pydantic Graph |
| smolagents | 라이브러리 | 파이썬 코드를 써서 실행하는 코드 에이전트 | 프로바이더 중립 | 가능 | Apache-2.0. 샌드박스 실행 지원 |
| nanobot | 런타임(실행형) | 설정 파일 기반 도구 호출 루프 | 프로바이더 중립 | 가능 | MIT. WebUI·터미널로 실행하고 OpenAI 호환 API 노출 |
| OpenAI Agents SDK | 라이브러리 | 내장 루프에 handoffs와 guardrails | 프로바이더 중립 | 가능 | MIT. 로컬은 OpenAI 호환 base_url과 LiteLLM 어댑터 경유 |
| Google ADK | 라이브러리 | 그래프 기반 Workflow와 에이전트 위임 | 프로바이더 중립. Gemini에 최적화 | 가능 | Apache-2.0 |
| CrewAI | 라이브러리 | 역할 기반 Crew와 이벤트 기반 Flow | 프로바이더 중립 | 가능 | MIT |
| Strands Agents | 라이브러리 | 모델이 주도하는 에이전트 루프 | 프로바이더 중립. 기본값은 Amazon Bedrock | 가능 | Apache-2.0. Python과 TypeScript |
| Claude Agent SDK | 라이브러리. Claude Code CLI 번들 | 모델 주도 루프에 도구·훅·권한 | Claude 모델 전용 | 불가 | MIT. Bedrock, Google Cloud, Microsoft Foundry 경유 호출 |

---

## 에이전트 메모리

에이전트가 이전 대화와 사실을 저장하고 다시 꺼내 쓰는 계층이다.

| 도구 | 저장 방식 | 형태 | 셀프호스팅 | 비고 |
|---|---|---|---|---|
| Mem0 | 벡터 | 라이브러리<br>저장소 `server/`의 Docker Compose 스택 | 가능 | Apache-2.0. 그래프 기억은 OSS에서 제거되어 관리형 Platform 전용 |
| Letta | 읽기·쓰기 가능한 메모리 블록 + 시맨틱 검색 아카이브 | 서버와 SDK | 가능 | Apache-2.0. Docker 이미지는 비유지보수로 문서에 명시 |
| Graphiti | 그래프. 임베딩·BM25·그래프 순회 병용 검색 | 라이브러리<br>FastAPI 서버 별도 제공 | 가능 | Apache-2.0 |
| Cognee | 그래프 + 벡터 | 라이브러리<br>API 서버 별도 제공 | 가능 | Apache-2.0 |

---

## 프롬프트 최적화

사람이 손으로 프롬프트를 고치는 대신 데이터로 프롬프트를 자동 개선하는 도구다.

| 도구 | 최적화 대상 | 방식 | 비고 |
|---|---|---|---|
| DSPy | 프롬프트, few-shot 예시, LM 가중치 | 데이터 검사와 실행 trace 시뮬레이션으로 예시를 만들고 instruction을 제안·개선 | MIT. 옵티마이저는 BootstrapFewShot, MIPROv2, GEPA 등 |
| GEPA | 프롬프트, 코드, 에이전트 구성을 포함한 텍스트 파라미터 | LLM 반성 기반 Pareto 진화 탐색 | MIT. DSPy 내장 옵티마이저이자 독립 라이브러리 |

---

## 모델 실행

오픈 웨이트 모델을 로컬이나 서버에서 직접 띄우는 런타임이다.

| 런타임 | 실행 형태 | 모델 포맷 | OpenAI 호환 API | 하드웨어 |
|---|---|---|---|---|
| Ollama | CLI와 HTTP 서버 | GGUF, Safetensors import<br>Modelfile로 정의 | 포트 11434 기준 `/v1/chat/completions`, `/v1/responses` | CPU·GPU·Apple Silicon |
| llama.cpp | 서버 바이너리 | GGUF | `/v1/chat/completions`, `/v1/responses`, `/v1/embeddings` | CPU·GPU·Apple Silicon |
| vLLM | 파이썬 서버 | Hugging Face Hub에서 내려받아 사용 | `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings` | NVIDIA CUDA 중심<br>Apple Silicon은 실험적 CPU 백엔드 |
| SGLang | 파이썬 서버 | Hugging Face 모델 경로 지정 | OpenAI API 전면 구현 | NVIDIA·AMD GPU, Intel Xeon CPU, TPU, NPU |
| MLX-LM | 파이썬 서버 | MLX 호환 모델 | `/v1/chat/completions`, `/v1/models` | Apple Silicon 전용. macOS 14 이상 |
| LM Studio | GUI 앱, CLI, 헤드리스 | GGUF와 MLX | 포트 1234 기준 `/v1/chat/completions` 등 | macOS는 Apple Silicon만 |

---

## 문서 수집과 구조화 출력

웹 페이지와 문서는 모델이 읽기 좋은 형태로 바꾸고 모델 응답은 미리 정한 스키마대로 나오게 강제하는 도구다.

| 도구 | 입력 | 출력 | 실행 위치 | 라이선스 |
|---|---|---|---|---|
| Crawl4AI | 웹 페이지 URL<br>raw HTML, 로컬 파일 | 마크다운 | 로컬 | Apache-2.0 |
| Firecrawl | URL<br>웹에 올라온 PDF·DOCX | 마크다운, 구조화 JSON | 셀프호스팅 가능<br>일부 기능은 클라우드 전용 | AGPL-3.0 |
| Docling | PDF, DOCX, PPTX, XLSX, HTML, EPUB, 오디오 | DoclingDocument 객체. 마크다운·HTML·JSON 내보내기 | 로컬 | MIT |
| Unstructured | PDF, HTML, Word 문서와 이미지 | 자체 정규 JSON 스키마 | 로컬 | Apache-2.0 |

| 도구 | 보장 방식 | 적용 지점 | 로컬 모델 | 비고 |
|---|---|---|---|---|
| Instructor | 프로바이더 클라이언트를 감싸 응답 모델을 붙이고 Pydantic 검증 실패 시 자동 재시도 | 클라이언트 | 가능 | MIT |
| Outlines | 정규식·문법·JSON Schema 기반 제약 디코딩 | 추론 엔진 | 가능 | Apache-2.0. 백엔드는 Transformers, llama.cpp, vLLM, Ollama |
| BAML | 전용 DSL을 컴파일해 타입 있는 클라이언트를 만들고 출력 텍스트를 스키마에 맞춰 보정 파싱 | 컴파일러·파서 | 가능 | Apache-2.0. 디코딩 자체는 제약하지 않음 |
| OpenAI Structured Outputs | 프로바이더가 JSON Schema를 강제 | 프로바이더 | 불가 | Responses는 `text.format`, Chat Completions는 `response_format` |

---

## 검색 저장소

문서를 벡터나 그래프로 저장해 두고 질문과 가까운 조각을 찾아 주는 계층이다.

| 제품 | 구현 언어 | 배포 형태 | 로컬 실행 | 라이선스 |
|---|---|---|---|---|
| ChromaDB | Rust | 임베디드·서버 | 영속 클라이언트 또는 Docker 이미지 | Apache-2.0 |
| Qdrant | Rust | 서버 | Docker 이미지. 클라이언트 인메모리 모드는 개발·테스트용 | Apache-2.0 |
| Weaviate | Go | 서버<br>임베디드 모드 별도 | Docker | BSD-3-Clause |
| Milvus | Go | 임베디드(Lite), 단일 노드, 분산 | Lite는 파이썬 라이브러리, 단일 노드는 Docker 이미지 한 개 | Apache-2.0 |
| pgvector | C | PostgreSQL 확장 | 소스 빌드, Docker 이미지, 패키지 관리자 | PostgreSQL License |
| LanceDB | Rust | 임베디드 | 서버 없이 프로세스 안에서 실행 | Apache-2.0 |

| 도구 | 저장소 요구 | 그래프 구축 | 입력 범위 | 비고 |
|---|---|---|---|---|
| neo4j-graphrag | 실행 중인 Neo4j 인스턴스 | KG 구축 파이프라인 제공 | 텍스트 | Apache-2.0. KG 구축에 APOC core 필요 |
| Microsoft GraphRAG | 자체 Parquet 인덱스 산출물과 설정한 벡터 저장소 | LLM으로 엔티티·관계·클레임을 추출한 뒤 Leiden 계층 클러스터링과 커뮤니티 요약 | 텍스트 | MIT |
| LightRAG | 기본은 파일로 영속화되는 인메모리 저장소<br>프로덕션은 PostgreSQL, Milvus·Qdrant, Neo4j·Memgraph 교체 | 청크별 엔티티·관계 추출. 그래프와 벡터 이중 계층 | 텍스트 | MIT |
| RAG-Anything | LightRAG를 따름 | LightRAG의 구축 흐름을 그대로 사용 | 문서 내 이미지·표·수식<br>파서 기본값은 MinerU | MIT. LightRAG 위에 얹은 멀티모달 확장 |

---

## 안전 필터

모델 앞뒤에서 유해 콘텐츠, 금지 주제, 민감정보, 프롬프트 인젝션을 걸러내는 계층이다.

| 도구 | 성격 | 적용 지점 | 로컬 실행 | 비고 |
|---|---|---|---|---|
| NeMo Guardrails | 프레임워크. Colang 스크립트로 입력, 출력, 대화 흐름 레일 정의 | 앱 코드에 내장 | 가능 | Apache-2.0. NVIDIA |
| Guardrails AI | 프레임워크. Hub에서 validator를 골라 입력과 출력 검증 | 앱 코드에 내장 | 가능 | Apache-2.0. Pydantic 출력 검증 |
| LLM Guard | 스캐너 모음. 프롬프트 인젝션, PII, 독성, 금지 주제 등 입력과 출력 스캐너 | 앱 코드 또는 API 서버 | 가능 | MIT. Protect AI. 2026-07 저장소 archive 처리로 유지보수 종료 |
| Presidio | PII 탐지와 익명화 엔진 | 앱 코드 또는 서버 | 가능 | MIT. Microsoft가 만들었고 2026년 커뮤니티 조직 Data Privacy Stack으로 이관. LLM 이전부터 쓰던 도구라 star는 가장 많지만 PII 전용 |
| Llama Guard | 안전성 분류 모델. 입력과 출력을 유해 범주로 분류 | 별도 모델 추론 | 가능 | Llama 라이선스. Meta. Prompt Guard는 인젝션 전용 소형 분류기 |

---

## 모니터링과 평가

에이전트가 실제로 어떻게 움직였는지 기록하고 그 결과가 좋았는지 점수를 매기는 계층이다.

| 도구 | 수집 방식 | 셀프호스팅 | 프롬프트 관리 | 평가 기능 |
|---|---|---|---|---|
| Langfuse | 자체 SDK와 OpenTelemetry 둘 다 | 가능 | 있음 | 있음 |
| Arize Phoenix | OpenTelemetry. OpenInference 시맨틱 규약 | 가능 | 있음 | 있음 |
| Opik | 자체 SDK 데코레이터와 OpenTelemetry 둘 다 | 가능 | 있음 | 있음 |
| OpenLLMetry | OpenTelemetry 계측 전용 | 자체 백엔드 없이 기존 관측 스택으로 내보냄 | 관리형 Traceloop 플랫폼 기능 | 해당 없음(계측 SDK) |

| 도구 | 평가 대상 | 지표 방식 | 실행 형태 | 비고 |
|---|---|---|---|---|
| Ragas | LLM 앱 전반. RAG와 에이전트 포함 | 둘 다 | 파이썬 라이브러리 | Apache-2.0. 2026-01 이후 릴리스 없음 |
| DeepEval | LLM 앱 전체 흐름과 에이전트 궤적 | 둘 다. 로컬에서 도는 NLP 모델도 사용 | 파이썬 프레임워크와 CLI. pytest 방식 | Apache-2.0 |
| promptfoo | 프롬프트·모델 비교와 레드티밍 | 둘 다. 결정적 assertion과 LLM 루브릭 | CLI와 YAML 설정 중심 | MIT. npm 배포 |
| TruLens | LLM 앱과 에이전트. RAG Triad 축 | LLM 판정 중심. 채점 근거 설명 동반 | 파이썬 패키지와 대시보드 | MIT |

---

## 업계 사실상 표준(de facto)

| 레이어 | GitHub star 최다(2026-08) | 차순위 |
|---|---|---|
| 오케스트레이션 프레임워크 | LangChain | LlamaIndex |
| 도구 연결 | MCP. SDK는 FastMCP | MCP Python SDK |
| 에이전트 프레임워크 | CrewAI | nanobot, LangGraph |
| 에이전트 메모리 | Mem0 | Cognee, Graphiti |
| 프롬프트 최적화 | DSPy | GEPA |
| 로컬 런타임 | Ollama | llama.cpp |
| 문서 수집·파싱 | Firecrawl | Crawl4AI |
| 구조화 출력 | Outlines | Instructor |
| 벡터 DB | Milvus | Qdrant |
| 그래프·멀티모달 RAG | LightRAG | Microsoft GraphRAG |
| 안전 필터 | Guardrails AI | NeMo Guardrails |
| 모니터링 | Langfuse | Opik |
| 평가 | promptfoo | DeepEval |

---

## Amazon Bedrock과 OSS 대응

위 레이어를 AWS 관리형 서비스로 채우면 어떤 그림이 되는지 Bedrock 기준으로 대응시켰다. 관리형은 인프라 운영을 맡아 주는 대신 손댈 수 있는 범위가 정해져 있고 OSS는 그 반대다.

| 레이어 | Bedrock | 이 글의 OSS 대응 |
|---|---|---|
| 모델 실행 | Bedrock 파운데이션 모델 호출 | vLLM, Ollama, llama.cpp, SGLang |
| RAG 파이프라인 | Bedrock Knowledge Bases | LangChain, LlamaIndex + Qdrant, Milvus, ChromaDB |
| 에이전트 | Bedrock AgentCore | LangGraph, CrewAI, Strands Agents |
| 안전 필터 | Bedrock Guardrails | NeMo Guardrails, Guardrails AI |
| 평가 | Bedrock Evaluations, AgentCore Evaluations | Ragas, DeepEval, promptfoo |

### 파운데이션 모델 호출 vs vLLM, Ollama, SGLang

Claude, Llama, Mistral, Amazon Nova, OpenAI 모델 등을 하나의 API로 호출하는 서빙 계층이다.

| 구분 | Bedrock 파운데이션 모델 | OSS 런타임 |
|---|---|---|
| 방식 | 온디맨드 토큰 과금, Provisioned Throughput, 배치 추론, Priority와 Flex 서비스 티어, 리전 간 추론 라우팅. Custom Model Import로 Llama, Mistral, Qwen 등 지원 아키텍처의 오픈 웨이트 모델을 직접 올릴 수 있음 | EC2나 온프레미스 GPU에 가중치를 올려 직접 서빙 |
| 장점 | GPU 운영 없음, Claude 같은 독점 모델 즉시 사용, 쿼터 안에서 수요에 따라 자동 확장, OpenAI와 Anthropic 호환 API로 기존 SDK를 그대로 사용 | 토큰당 API 비용 없음, 데이터가 밖으로 나가지 않는 폐쇄망 운영, 양자화와 KV 캐시, 배칭 파라미터를 직접 조정 |
| 단점 | 호출량이 늘면 비용이 선형으로 증가, 서빙 엔진 내부 파라미터 조정 불가 | GPU 확보 난이도와 고정 인프라 비용, 장애 대응과 스케일링을 직접 담당 |
| 맞는 경우 | 트래픽 변동이 크거나 최신 모델을 빠르게 붙여야 할 때 | 요청량이 일정하게 높고 데이터 외부 전송이 불가할 때 |

### Knowledge Bases vs LangChain, LlamaIndex + 벡터 DB

문서 수집, 청킹, 임베딩, 벡터 저장, 검색까지 이어지는 RAG 파이프라인 계층이다. Knowledge Bases는 두 가지 형태로 나뉜다. Managed는 임베딩과 리랭킹, 저장소까지 AWS가 맡고 S3, SharePoint, Confluence, Google Drive, OneDrive, 웹 크롤러 커넥터와 문서 단위 권한 필터, 다단계 검색을 제공한다. Customer-managed는 벡터 저장소를 OpenSearch Serverless와 관리형 클러스터, Aurora pgvector, Neptune Analytics(그래프 RAG), Pinecone, MongoDB Atlas, Redis, S3 Vectors 중에서 고르고 청킹과 파싱을 직접 설정한다.

| 구분 | Bedrock Knowledge Bases | OSS 조합 |
|---|---|---|
| 방식 | 콘솔이나 API로 데이터 소스와 저장소를 지정하면 인제스천부터 검색 API까지 자동 구축 | 파서, 청킹, 임베딩, 벡터 DB, 리랭커를 코드로 조립 |
| 장점 | 파이프라인 운영 공수가 거의 없음, 청킹은 고정 크기와 계층, 시맨틱 세 가지에 Lambda 커스텀 변환까지 제공, 그래프 RAG와 멀티모달 파싱(Bedrock Data Automation)도 지원 | 청킹 전략, 리트리버 알고리즘, 리랭킹 로직을 어디까지든 바꿀 수 있음, 저장소와 파서 선택에 제한 없음 |
| 단점 | 청킹과 저장소는 제공 목록 안에서 선택, 리트리버 자체를 갈아끼울 수 없음, 관리형 저장소 최소 비용 발생 | 인제스천 파이프라인, 임베딩 캐싱, 벡터 DB 인프라를 직접 운영 |
| 맞는 경우 | 사내 규정이나 FAQ 챗봇을 가장 빠르게 세울 때 | 수식과 표가 많은 도메인 문서를 정밀하게 검색하거나 검색 방식 자체를 실험할 때 |

### AgentCore vs LangGraph, CrewAI, Strands Agents

에이전트 실행 계층이다. 2023년에 나온 Bedrock Agents는 2026년 7월 30일부터 Bedrock Agents Classic이라는 이름으로 유지보수 모드에 들어갔다. 직전 12개월간 사용 이력이 없는 계정은 새 에이전트를 만들 수 없고 모델 카탈로그도 그날 기준으로 고정됐다. 기존 에이전트는 계속 동작하지만 신규 기능은 없다. AWS가 안내하는 후속은 AgentCore다.

AgentCore는 하나의 에이전트 프레임워크가 아니라 Runtime, Gateway(도구를 MCP로 노출), Memory, Identity, Observability, Code Interpreter, Browser, Policy, Evaluations에 결제(Payments), 자동 최적화(Optimization), 카탈로그(Registry)까지 조합하는 인프라 묶음이다. 그 위에서 Strands, LangGraph, CrewAI, LlamaIndex, Google ADK, OpenAI Agents SDK, Claude Agent SDK 등 어떤 프레임워크로 짠 에이전트든 돌릴 수 있고 설정만으로 시작하는 managed harness도 따로 있다. 모델도 Bedrock 카탈로그 외에 OpenAI, Gemini, OpenAI 호환 엔드포인트를 붙일 수 있다.

| 구분 | Bedrock AgentCore | OSS 프레임워크 단독 |
|---|---|---|
| 방식 | 에이전트 코드는 프레임워크로 짜고 실행, 메모리, 인증, 관측은 AgentCore가 담당. harness를 쓰면 모델과 도구, 지시문만 선언 | 프레임워크로 루프를 짜고 상태 저장소, 세션, 재시도, 관측을 직접 구성 |
| 장점 | 컨테이너 런타임과 세션 격리, IAM 기반 권한, 도구를 MCP로 통일, 추적이 기본 내장 | 실행 환경 제약 없음, 어디서든 같은 코드로 실행 |
| 단점 | AWS 종속, harness 경로는 단계별 프롬프트 오버라이드나 라우팅형 다중 에이전트가 제한적 | 운영 계층을 전부 직접 만들어야 함 |
| 맞는 경우 | 이미 AWS 위에 있고 에이전트 운영 인프라를 직접 만들 인력이 없을 때 | 멀티 클라우드나 온프레미스, 로컬 모델을 섞어야 할 때 |

에이전트 로직 자체는 두 쪽 다 LangGraph나 CrewAI로 짜는 경우가 많다. 그래서 이 항목은 프레임워크끼리의 비교라기보다 그 프레임워크를 어디서 어떻게 돌리느냐의 비교다.

### Guardrails vs NeMo Guardrails, Guardrails AI

입력과 출력에서 유해 콘텐츠, 금지 주제, 민감정보, 근거 없는 답변을 걸러내는 계층이다.

| 구분 | Bedrock Guardrails | OSS |
|---|---|---|
| 방식 | 콘텐츠 필터(증오, 모욕, 성적, 폭력, 위법, 프롬프트 공격), 자연어로 정의하는 금지 주제, 단어 필터, PII와 정규식 기반 민감정보 필터, 컨텍스트 근거 검사, 논리 규칙 기반 Automated Reasoning 검사. 모델 호출에 붙이거나 ApplyGuardrail API로 단독 호출 | NeMo Guardrails는 Colang 스크립트로 대화 흐름을 정의, Guardrails AI는 Hub의 validator와 Pydantic 검증을 코드에 내장 |
| 장점 | 정책을 콘솔에서 버전 관리하고 애플리케이션 코드와 분리, ApplyGuardrail로 Bedrock 밖 모델에도 적용 가능 | 대화 주제 이탈 통제와 도메인별 검증 룰을 원하는 대로 프로그래밍 |
| 단점 | 정책 종류가 정해진 범위 안, 정책마다 지연과 텍스트 단위 과금이 추가 | 룰 엔진과 임베딩 모델을 앱 서버에서 돌려야 해 리소스를 씀 |
| 맞는 경우 | PII 마스킹, 유해 콘텐츠 차단 같은 표준 컴플라이언스 | 특정 경쟁사 언급 금지, 주제 이탈 시 안내 문구 같은 세밀한 대화 흐름 통제 |

### Evaluations vs Ragas, DeepEval, promptfoo

프롬프트나 파이프라인이 바뀌었을 때 품질이 어떻게 달라졌는지 재는 계층이다. Bedrock 쪽은 둘로 나뉜다. Bedrock Evaluations는 모델 평가(내장 지표, LLM 판정, 사람 평가)와 RAG 평가(Knowledge Bases 또는 외부 RAG 대상, 검색 관련성과 커버리지, 정확성, 완전성, 충실도)를 맡고 2026년 3월 GA된 AgentCore Evaluations는 세션, 트레이스, 도구 호출 단위로 에이전트 궤적을 평가한다.

| 구분 | Bedrock Evaluations, AgentCore Evaluations | OSS |
|---|---|---|
| 방식 | Bedrock Evaluations는 데이터셋을 S3에 올리고 평가 작업을 만들면 결과를 콘솔과 S3로 받음. AgentCore Evaluations는 CloudWatch에 쌓인 세션 트레이스를 Evaluate API나 CLI로 평가하고 결과를 CloudWatch 대시보드로 봄 | 코드에서 지표를 정의하고 테스트처럼 실행. DeepEval은 pytest, promptfoo는 CLI와 YAML |
| 장점 | S3에 둔 데이터셋과 바로 연동, 팀원 간 사람 평가 작업 분배, 에이전트 궤적 평가가 관측 데이터와 붙어 있음 | 커스텀 지표 자유, GitHub Actions 같은 CI 파이프라인에 PR 단위 회귀 테스트로 붙이기 쉬움 |
| 단점 | Bedrock Evaluations는 비동기 배치 작업이라 CI에 끼우려면 폴링과 결과 파싱을 직접 감싸야 함. AgentCore Evaluations는 동기 API가 있지만 평가 전에 트레이스를 CloudWatch에서 꺼내는 단계가 필요 | 판정용 LLM 호출 비용과 테스트 환경을 직접 관리 |
| 맞는 경우 | 비즈니스 조직과 함께 여러 모델과 프롬프트를 정성 비교할 때 | 코드나 프롬프트가 바뀔 때마다 RAG 성능 하락을 자동 검증할 때 |

### 선택 기준

Bedrock 쪽이 맞는 경우다.

- 인프라 인력이 적고 개발 속도와 IAM, VPC, PII 마스킹 같은 컴플라이언스가 우선일 때
- 검색, 함수 실행, 안전 검사로 끝나는 표준 업무 흐름이고 이미 AWS 위에 있을 때

OSS 쪽이 맞는 경우다.

- 자기 수정 루프, 상태 롤백, 다단계 검증처럼 실행 흐름을 세밀하게 통제해야 할 때
- AWS 외 클라우드, 온프레미스, 로컬 모델을 섞어야 해서 종속을 피해야 할 때

두 쪽을 섞는 것도 흔하다. 에이전트는 LangGraph로 짜고 AgentCore에서 돌리거나 모델은 vLLM으로 직접 서빙하면서 Guardrails만 ApplyGuardrail로 붙이는 식이다.
