---
draft: false
date: 2026-08-17
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
description: "에이전트 개발에 쓰는 오픈소스 도구를 오케스트레이션·에이전트·메모리·모델 실행·수집·저장소·관측 9개 레이어로 묶어 성격과 로컬 실행 여부를 표로 비교"
---
# AI 에이전트 개발 도구 레이어별 비교

에이전트를 만들 때 쓰는 오픈소스 도구를 레이어로 묶어 표로 정리했다. 성격, 로컬 실행 여부, 셀프호스팅 여부를 축으로 잡았다.

<!-- more -->

## 오케스트레이션 프레임워크

| 프레임워크 | 성격 | 주 언어 | 강점 영역 | 비고 |
|---|---|---|---|---|
| LangChain | 에이전트·LLM 앱 범용 프레임워크 | Python<br>JS·TS는 별도 라이브러리 | 모델·도구·벡터 저장소 통합량 | MIT. 1.x에서 에이전트 실행 기능 내장 |
| LlamaIndex | 데이터 프레임워크. 인덱싱·검색 중심 | Python | 데이터 커넥터와 인덱스 구성 | MIT. 2026-08 기준 v0.14 |
| Haystack | 파이프라인 그래프 오케스트레이션 | Python | 검색·라우팅·생성 단계를 명시적으로 조립 | Apache-2.0. 2026-07 기준 v3.0 |
| Semantic Kernel | 모델 중립 에이전트 오케스트레이션 SDK | C#, Python, Java 3종 공식 SDK | 엔터프라이즈 관측·보안 | MIT. Python SDK는 2026-08 기준 v1.44 |

---

## 도구 연결 표준과 SDK

| 프로토콜 | 해결하는 연결 | 참여자 | 전송 | 비고 |
|---|---|---|---|---|
| MCP(Model Context Protocol) | 앱 ↔ 도구·데이터 | 호스트, 클라이언트, 서버 | stdio<br>Streamable HTTP | 데이터 계층은 JSON-RPC 2.0 |
| A2A(Agent2Agent) | 에이전트 ↔ 에이전트 | 클라이언트, 서버(원격 에이전트) | JSON-RPC, gRPC, HTTP+JSON 바인딩<br>스트리밍은 SSE | Apache-2.0. 2026-05 기준 v1.0 |
| AG-UI(Agent-User Interaction Protocol) | 에이전트 ↔ 프런트엔드 | 에이전트 백엔드, 사용자 화면 애플리케이션 | 전송 비종속. SSE·WebSocket·웹훅 | MIT. 이벤트 기반 계층 |

| SDK | 대상 프로토콜 | 성격 | PyPI | 비고 |
|---|---|---|---|---|
| FastMCP | MCP | MCP 서버·클라이언트 구축 프레임워크 | `fastmcp` | Apache-2.0. 1.0이 공식 SDK로 흡수, 이후 독립 유지보수. 2026-08 기준 v3.4 |
| MCP Python SDK | MCP | 공식 Python 구현 | `mcp` | MIT. v2.0에서 FastMCP 클래스가 MCPServer로 개명 |

---

## 에이전트 프레임워크

| 프레임워크 | 성격 | 제어 방식 | 모델 결합 | 로컬 모델 | 비고 |
|---|---|---|---|---|---|
| LangGraph | 라이브러리 | 상태와 노드, 엣지로 짜는 그래프 | 프로바이더 중립 | ✅ | MIT. 2026-08 기준 v1.2 |
| PydanticAI | 라이브러리 | 타입 검증이 붙은 에이전트 루프 | 프로바이더 중립 | ✅ | MIT. 그래프가 필요하면 Pydantic Graph |
| smolagents | 라이브러리 | 파이썬 코드를 써서 실행하는 코드 에이전트 | 프로바이더 중립 | ✅ | Apache-2.0. 샌드박스 실행 지원 |
| nanobot | 런타임(실행형) | 설정 파일 기반 도구 호출 루프 | 프로바이더 중립 | ✅ | MIT. WebUI·터미널로 실행하고 OpenAI 호환 API 노출 |
| OpenAI Agents SDK | 라이브러리 | 내장 루프에 handoffs와 guardrails | 프로바이더 중립 | ✅ | MIT. 로컬은 OpenAI 호환 base_url과 LiteLLM 어댑터 경유 |
| Google ADK | 라이브러리 | 그래프 기반 Workflow와 에이전트 위임 | 프로바이더 중립. Gemini에 최적화 | ✅ | Apache-2.0. 2026-08 기준 v2.7 |
| CrewAI | 라이브러리 | 역할 기반 Crew와 이벤트 기반 Flow | 프로바이더 중립 | ✅ | MIT. 2026-08 기준 v1.15 |
| Strands Agents | 라이브러리 | 모델이 주도하는 에이전트 루프 | 프로바이더 중립. 기본값은 Amazon Bedrock | ✅ | Apache-2.0. Python과 TypeScript |
| Claude Agent SDK | 라이브러리. Claude Code CLI 번들 | 모델 주도 루프에 도구·훅·권한 | Claude 모델 전용 | ❌ | MIT. Bedrock, Google Cloud, Microsoft Foundry 경유 호출 |

---

## 에이전트 메모리

| 도구 | 저장 방식 | 형태 | 셀프호스팅 | 비고 |
|---|---|---|---|---|
| Mem0 | 벡터 | 라이브러리<br>저장소 `server/`의 Docker Compose 스택 | ✅ | Apache-2.0. 그래프 기억은 OSS에서 제거되어 관리형 Platform 전용 |
| Letta | 읽기·쓰기 가능한 메모리 블록 + 시맨틱 검색 아카이브 | 서버와 SDK | ✅ | Apache-2.0. Docker 이미지는 비유지보수로 문서에 명시 |
| Graphiti | 그래프. 임베딩·BM25·그래프 순회 병용 검색 | 라이브러리<br>FastAPI 서버 별도 제공 | ✅ | Apache-2.0. 2026-07 기준 v0.29 |
| Cognee | 그래프 + 벡터 | 라이브러리<br>API 서버 별도 제공 | ✅ | Apache-2.0. 2026-08 기준 v1.5 |
| LangMem | 벡터. 저장은 LangGraph BaseStore에 위임 | 라이브러리 | ✅ | MIT. 0.0.x 초기 단계 |

---

## 프롬프트 최적화

| 도구 | 최적화 대상 | 방식 | 비고 |
|---|---|---|---|
| DSPy | 프롬프트, few-shot 예시, LM 가중치 | 데이터 검사와 실행 trace 시뮬레이션으로 예시를 만들고 instruction을 제안·개선 | MIT. 옵티마이저는 BootstrapFewShot, MIPROv2, GEPA 등 |
| GEPA | 프롬프트, 코드, 에이전트 구성을 포함한 텍스트 파라미터 | LLM 반성 기반 Pareto 진화 탐색 | MIT. DSPy 내장 옵티마이저이자 독립 라이브러리 |

---

## 모델 실행

| 런타임 | 실행 형태 | 모델 포맷 | OpenAI 호환 API | 하드웨어 |
|---|---|---|---|---|
| Ollama | CLI와 HTTP 서버 | GGUF, Safetensors import<br>Modelfile로 정의 | 포트 11434 기준 `/v1/chat/completions`, `/v1/responses` | CPU·GPU·Apple Silicon |
| llama.cpp | 서버 바이너리 | GGUF | `/v1/chat/completions`, `/v1/responses`, `/v1/embeddings` | CPU·GPU·Apple Silicon |
| vLLM | 파이썬 서버 | Hugging Face Hub에서 내려받아 사용 | `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings` | NVIDIA CUDA 중심<br>Apple Silicon은 실험적 CPU 백엔드 |
| SGLang | 파이썬 서버 | Hugging Face 모델 경로 지정 | OpenAI API 전면 구현 | NVIDIA·AMD GPU, Intel Xeon CPU, TPU, NPU |
| MLX-LM | 파이썬 서버 | MLX 호환 모델 | `/v1/chat/completions`, `/v1/models` | Apple Silicon 전용. macOS 14 이상 |
| LM Studio | GUI 앱, CLI, 헤드리스 | GGUF와 MLX | 포트 1234 기준 `/v1/chat/completions` 등 | macOS는 Apple Silicon만 |

| 프로바이더 | 공식 Python SDK | 주 API | OpenAI 호환 엔드포인트 | 로컬 대체 |
|---|---|---|---|---|
| OpenAI | `openai` | Responses API | 해당 없음 | SDK가 base_url 지정을 지원해 로컬 서버로 돌릴 수 있음 |
| Anthropic | `anthropic` | Messages API `/v1/messages` | 있음. 테스트·비교 용도 | SDK가 base_url 지정을 지원. 로컬 모델 사용은 문서화되지 않음 |
| Google Gemini | `google-genai` | Gemini API | 있음 | 커스텀 base_url은 API 게이트웨이 용도로 문서화 |
| Upstage | 없음. OpenAI SDK에 base_url 지정 | `/v1/chat/completions`, `/v1/embeddings` | 있음 | OpenAI SDK를 그대로 쓰므로 base_url만 로컬 서버로 바꾸면 됨 |

---

## 문서 수집과 구조화 출력

| 도구 | 입력 | 출력 | 실행 위치 | 라이선스 |
|---|---|---|---|---|
| Crawl4AI | 웹 페이지 URL<br>raw HTML, 로컬 파일 | 마크다운 | 로컬 | Apache-2.0 |
| Firecrawl | URL<br>웹에 올라온 PDF·DOCX | 마크다운, 구조화 JSON | 셀프호스팅 가능<br>일부 기능은 클라우드 전용 | AGPL-3.0 |
| Docling | PDF, DOCX, PPTX, XLSX, HTML, EPUB, 오디오 | DoclingDocument 객체. 마크다운·HTML·JSON 내보내기 | 로컬 | MIT |
| Unstructured | PDF, HTML, Word 문서와 이미지 | 자체 정규 JSON 스키마 | 로컬 | Apache-2.0 |

| 도구 | 보장 방식 | 적용 지점 | 로컬 모델 | 비고 |
|---|---|---|---|---|
| Instructor | 프로바이더 클라이언트를 감싸 응답 모델을 붙이고 Pydantic 검증 실패 시 자동 재시도 | 클라이언트 | ✅ | MIT. 2026-06 기준 v1.15 |
| Outlines | 정규식·문법·JSON Schema 기반 제약 디코딩 | 추론 엔진 | ✅ | Apache-2.0. 백엔드는 Transformers, llama.cpp, vLLM, Ollama |
| BAML | 전용 DSL을 컴파일해 타입 있는 클라이언트를 만들고 출력 텍스트를 스키마에 맞춰 보정 파싱 | 컴파일러·파서 | ✅ | Apache-2.0. 디코딩 자체는 제약하지 않음 |
| OpenAI Structured Outputs | 프로바이더가 JSON Schema를 강제 | 프로바이더 | ❌ | Responses는 `text.format`, Chat Completions는 `response_format` |

---

## 검색 저장소

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
| Microsoft GraphRAG | 자체 Parquet 인덱스 산출물과 설정한 벡터 저장소 | LLM으로 엔티티·관계·클레임을 추출한 뒤 Leiden 계층 클러스터링과 커뮤니티 요약 | 텍스트 | MIT. 2026-07 기준 v3.1 |
| LightRAG | 기본은 파일로 영속화되는 인메모리 저장소<br>프로덕션은 PostgreSQL, Milvus·Qdrant, Neo4j·Memgraph 교체 | 청크별 엔티티·관계 추출. 그래프와 벡터 이중 계층 | 텍스트 | MIT. 2026-08 기준 v1.5 |
| RAG-Anything | LightRAG를 따름 | LightRAG의 구축 흐름을 그대로 사용 | 문서 내 이미지·표·수식<br>파서 기본값은 MinerU | MIT. LightRAG 위에 얹은 멀티모달 확장 |

---

## 관측과 평가

| 도구 | 수집 방식 | 셀프호스팅 | 프롬프트 관리 | 평가 기능 |
|---|---|---|---|---|
| Langfuse | 자체 SDK와 OpenTelemetry 둘 다 | ✅ | ✅ | ✅ |
| Arize Phoenix | OpenTelemetry. OpenInference 시맨틱 규약 | ✅ | ✅ | ✅ |
| Opik | 자체 SDK 데코레이터와 OpenTelemetry 둘 다 | ✅ | ✅ | ✅ |
| OpenLLMetry | OpenTelemetry 계측 전용 | 자체 백엔드 없이 기존 관측 스택으로 내보냄 | 관리형 Traceloop 플랫폼 기능 | 해당 없음(계측 SDK) |

| 도구 | 평가 대상 | 지표 방식 | 실행 형태 | 비고 |
|---|---|---|---|---|
| Ragas | LLM 앱 전반. RAG와 에이전트 포함 | 둘 다 | 파이썬 라이브러리 | Apache-2.0. 2026-01 이후 릴리스 없음 |
| DeepEval | LLM 앱 전체 흐름과 에이전트 궤적 | 둘 다. 로컬에서 도는 NLP 모델도 사용 | 파이썬 프레임워크와 CLI. pytest 방식 | Apache-2.0. 2026-07 기준 v4.1 |
| promptfoo | 프롬프트·모델 비교와 레드티밍 | 둘 다. 결정적 assertion과 LLM 루브릭 | CLI와 YAML 설정 중심 | MIT. npm 배포 |
| TruLens | LLM 앱과 에이전트. RAG Triad 축 | LLM 판정 중심. 채점 근거 설명 동반 | 파이썬 패키지와 대시보드 | MIT. 2026-08 기준 v2.13 |

---

## 요약

| 레이어 | 로컬 무료 조합 | 사유 |
|---|---|---|
| 에이전트 | PydanticAI | MIT, 프로바이더 중립 |
| 도구 연결 | FastMCP | Apache-2.0, 로컬 실행 |
| 메모리 | Mem0 | Docker Compose 셀프호스팅 스택 동봉 |
| 프롬프트 최적화 | DSPy | MIT, GEPA 내장 |
| 모델 실행 | Ollama | OpenAI 호환 엔드포인트 → 상용 API 코드 그대로 재사용 |
| 수집 | Docling | MIT, 전 과정 로컬 실행 |
| 구조화 출력 | Instructor | 클라이언트 계층이라 로컬 모델에도 그대로 적용 |
| 벡터 저장소 | ChromaDB | 서버 없이 영속 클라이언트로 시작 가능 |
| 관측 | Langfuse | 코어 MIT, 로컬 Docker Compose |
| 평가 | Ragas | Apache-2.0, 로컬 실행 |
