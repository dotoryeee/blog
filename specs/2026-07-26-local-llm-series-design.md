# 로컬 LLM 실습·정리 4편 시리즈 기획

작성일 2026-07-26. 게시 예정일 2026-07-27.

## 배경

블로그 104편 중 AI 카테고리는 14편이다. 이론 정리(C)가 gpu_01~08로 8편, 실습(A)이 3편(gpu_lora_lab, ai_gateway_litellm, mcp_server_lab), 나머지 3편은 게이트웨이·MCP 관련이다.

2026-07-19 이후 이 블로그의 지배적 패턴은 **"정리(C) + 실습(A)" 2편 세트를 공통 대표 태그로 묶는 것**이다. 지금까지 9쌍이 있다(OpenTelemetry, WireGuard·IPIP, eBPF, 컨테이너 내부구조, GitOps·ArgoCD, Service Mesh, 시크릿·Vault, MCP, AI Gateway).

이 구조에서 빈 자리가 두 개 확인됐다.

1. **gpu_07 LLM 추론 서빙 정리에 짝이 되는 실습이 없다.** prefill/decode 분리, KV cache 계산식, 필요 VRAM 어림, continuous batching, 양자화, 서빙 엔진 비교까지 이론이 전부 들어 있는데 실측 글이 없다. 특히 서빙 엔진 비교표에 llama.cpp를 "GGUF, Apple Silicon(Metal) 1급 지원 / 로컬·온디바이스·맥"이라고 **주장만** 적어두었다.
2. **MoE 추론 관점과 RAG 파이프라인 관점이 비어 있다.** MoE는 gpu_05에 Expert Parallelism 표 한 줄로만 등장하고 그마저 학습 관점이다. RAG는 gpu_08에 "파인튜닝 vs RAG 차이점" 섹션만 있다.

## 목표

Mac Studio M1 Max / 64GB 통합 메모리에서 로컬 LLM을 실측해 gpu_07의 이론을 검증하고, 로컬 모델로 RAG 파이프라인까지 세운다. 클라우드 비용 0 원칙(§11)을 유지한다.

## 검증된 사실

작성 시점에 HuggingFace API와 공식 저장소로 직접 확인한 값이다. 집필 시 이 표를 근거로 쓰되, 실행 시점에 달라질 수 있는 값은 실측으로 갱신한다.

### 모델 아키텍처

| 항목 | Qwen3.6-35B-A3B | Qwen3.6-27B |
|---|---|---|
| 구조 | MoE (qwen3_5_moe) | Dense (qwen3_5) |
| 총 레이어 | 40 | 64 |
| full attention 레이어 | 10 | 16 |
| linear attention 레이어 | 30 | 48 |
| full_attention_interval | 4 | 4 |
| attention heads | 16 | 24 |
| KV heads | 2 | 4 |
| head_dim | 256 | 256 |
| hidden_size | 2048 | 5120 |
| intermediate_size | moe 512, shared 512 | 17408 |
| 전문가 | 256개 중 토큰당 8개 | 없음 |
| max_position_embeddings | 262144 | 262144 |
| vocab_size | 248320 | 248320 |

두 모델 모두 **하이브리드 어텐션**이다. 4개 레이어 중 1개만 full attention이고 나머지는 linear attention이다. gpu_07의 KV cache 계산식은 모든 레이어가 KV를 저장한다고 가정하므로, 이 모델에 그대로 넣으면 약 4배 과대 추정이 나온다. 2편의 핵심 실측 항목이다.

### GGUF 파일 크기 (unsloth 배포판)

| 양자화 | 35B-A3B (MoE) | 27B (Dense) |
|---|---|---|
| Q4_K_M | 22.13GB (UD-Q4_K_M) | 16.82GB |
| Q6_K | 29.31GB (UD-Q6_K) | 22.52GB |
| Q8_0 | 36.90GB | 28.60GB |
| BF16 | 69.37GB (2분할) | 53.80GB (2분할) |

**파라미터도 파일도 MoE가 더 큰데 토큰당 활성 파라미터는 3B vs 27B로 9배 차이다.** 메모리는 비싸고 연산은 싼 역전 구조가 이 시리즈의 논지다.

BF16은 두 모델 다 64GB에 올라가지 않는다. 로컬에서 양자화가 선택이 아니라 전제인 이유의 증거로 쓴다.

### 도구

- llama.cpp: Homebrew formula 존재(stable 10050), 의존성 ggml·openssl@3
- `llama-server --metrics`: Prometheus 호환 `/metrics` 엔드포인트 제공(기본 비활성, env `LLAMA_ARG_ENDPOINT_METRICS`)
- `llama-server /slots`: 슬롯별 속도·처리 토큰·샘플링 파라미터 조회(기본 활성)
- Qdrant: Web UI 내장
- 임베딩 모델: `Qwen/Qwen3-Embedding-0.6B-GGUF`

## 4편 구성

전부 `docs/blog/posts/Cloud Infra/`에 두고 categories는 `AI`로 통일한다. 기존 AI 글 14편이 모두 이 폴더에 있다.

| 순서 | 파일 | 제목 | 유형 | 대표 태그 |
|---|---|---|---|---|
| 1 | `moe.md` | MoE 추론 정리 | (C) 개조식 | **MoE**, LLM, Qwen |
| 2 | `moe_lab.md` | llama.cpp로 MoE와 Dense 추론 성능 비교하기 | (A) 실습 | **MoE**, llama.cpp, Qwen |
| 3 | `rag.md` | RAG 정리 | (C) 개조식 | **RAG**, LLM, Embedding |
| 4 | `rag_lab.md` | 로컬 모델로 RAG 파이프라인 구축하기 | (A) 실습 | **RAG**, Qdrant, llama.cpp |

파일명은 블로그 관행(`정리=주제.md`, `실습=주제_lab.md`)을 따랐다. `otel.md`/`otel_lab.md`, `service_mesh.md`/`service_mesh_lab.md`와 같은 꼴이다. 볼드 표시한 대표 태그를 세트끼리 공유해 태그 페이지에서 묶이게 한다(§3).

정리 글을 먼저 배치한 이유가 하나 더 있다. 정리 글은 모델 다운로드가 필요 없어서, 1편을 쓰는 동안 2편용 모델(약 90GB)을 백그라운드로 받을 수 있다.

### frontmatter

네 편 공통 골격이다. 순서는 §3 고정 규칙을 지킨다.

```yaml
draft: false
date: 2026-07-27
authors:
  - dotoryeee
categories:
  - AI
tags:
  - <대표 태그>
  - <세부 2~4개>
description: "<50~120자, §12 규칙 준수>"
```

폭 넓은 표가 들어가는 편에는 `hide: [toc]`를 추가한다.

## 1편 — MoE 추론 정리 (moe.md)

(C) 개조식. 명사형 종결. 첫 섹션은 `## MoE란` + 불릿 아닌 정의 한 줄로 연다(§1).

목차:

1. `## MoE란` — 정의 한 줄
2. `## 총 파라미터와 활성 파라미터` — 35B와 3B가 각각 무엇을 뜻하는지
3. `## 게이팅과 라우팅` — top-k 선택, 로드 밸런싱
4. `## 전문가 구성` — 세분화 전문가(256개 중 8개), 공유 전문가
5. `## Dense와 비교` — 표
6. `## 메모리와 연산 트레이드오프` — 표
7. `## 로컬 추론에서의 MoE` — 대역폭 바운드 관점
8. `## 함정: 활성이 3B여도 전부 올려야 함`
9. `## 결론`

gpu_05(분산 학습 병렬화)가 MoE를 학습 관점 Expert Parallelism으로 다뤘으므로 각도가 겹치지 않게 쓴다. 필요하면 본문 자연 링크 1회로만 연결한다(§3).

## 2편 — MoE와 Dense 추론 성능 비교 실습 (moe_lab.md)

(A) 실습. 평서형 `~한다`(존댓말 금지, §1). 본문 프로즈·admonition에 인라인 백틱 금지.

### 스택

llama-server는 네이티브(brew), 관측 스택은 docker compose로 분리한다. Docker Desktop for Mac은 Metal 패스스루가 없어 컨테이너 안 llama.cpp가 GPU를 못 쓴다. `ai_gateway_litellm`이 이미 "네이티브 Ollama 설치 시 api_base를 host.docker.internal로 연결한다"는 같은 패턴을 썼다.

```
llama-server :8080  MoE 35B-A3B   (네이티브, Metal, --alias dotoryeee-moe)
llama-server :8081  Dense 27B     (네이티브, Metal, --alias dotoryeee-dense)
Prometheus   :9090  (docker) → host.docker.internal:8080,8081 /metrics
Grafana      :3000  (docker) → 대시보드 dotoryeee local llm
```

### 실측 항목

| # | 실측 | 기대 관찰 |
|---|---|---|
| 1 | 모델 로드 시 메모리 점유 | MoE 22.13GB vs Dense 16.82GB |
| 2 | prefill 속도(TTFT) | 프롬프트 길이별 |
| 3 | decode 속도(토큰/초) | 역전 지점. 활성 3B vs 27B |
| 4 | KV cache 실측 vs gpu_07 계산식 | 하이브리드 어텐션으로 약 4배 어긋남 |
| 5 | 컨텍스트 확장 4K→32K→128K | KV 증가 곡선 |
| 6 | 양자화 사다리 Q4_K_M→Q6_K→Q8_0 | Dense 기준 16.8→22.5→28.6GB |
| 7 | 동시 요청 `--parallel` | 처리량 vs 지연 트레이드오프 |

3번이 이 글의 논지다. 파일도 파라미터도 MoE가 큰데 디코드는 MoE가 빠르다는 것이 수치로 나오면 gpu_07의 "decode는 대역폭 바운드" 서술이 실측으로 증명된다.

양자화 사다리는 **Dense로만** 돌린다. MoE까지 3점을 받으면 다운로드가 127GB로 뛴다. Dense 3점(16.82+22.52+28.60) + MoE Q4_K_M(22.13)이면 약 90GB로 끝나고 디스크 여유 301GB 안에서 안전하다. MoE Q8_0(36.90GB)은 받지 않고 macOS GPU wired limit 계산으로만 다룬다.

### 스크린샷 계획 (11장 목표)

Grafana 6장, llama-server 내장 WebUI 3장, Prometheus 타깃 1장, macmon GPU 사용률 1장.

브랜딩(§10)은 `--alias dotoryeee-moe` / `dotoryeee-dense`, Prometheus job 이름 `dotoryeee-llm`, Grafana 대시보드 `dotoryeee local llm`으로 건다.

날짜 처리는 k6 글 전례를 따른다. Grafana 시간축은 §10 예외(날짜 없는 시간축이 논지의 증거)로 유지하되 연월일은 CSS 주입으로 가린다. 촬영 후 이미지를 Read로 열어 육안 확인한다.

## 3편 — RAG 정리 (rag.md)

(C) 개조식. 목차:

1. `## RAG란` — 정의 한 줄
2. `## 파이프라인 구성` — 수집→청킹→임베딩→저장→검색→리랭킹→생성
3. `## 청킹 전략` — 표
4. `## 임베딩 모델 선택` — 표
5. `## 벡터 검색 방식` — HNSW·IVF·Flat 표
6. `## 하이브리드 검색` — BM25 + 벡터
7. `## 리랭킹`
8. `## 함정`
9. `## 결론`

gpu_08에 "파인튜닝 vs RAG 차이점 정리" 섹션이 있으므로 그 각도(언제 무엇을 쓰나)는 피하고 파이프라인 구성 요소로 각을 잡는다. 본문 자연 링크 1회로만 연결한다(§3).

## 4편 — 로컬 모델로 RAG 파이프라인 구축하기 (rag_lab.md)

(A) 실습.

### 스택

```
Qdrant       :6333  (docker, Web UI 내장, 컬렉션 dotoryeee-docs)
llama-server :8082  Qwen3-Embedding-0.6B (네이티브, --embedding)
llama-server :8080  MoE 35B-A3B Q4_K_M (2편에서 받아둔 것을 그대로 재사용)
llama-server :8081  Dense 27B Q4_K_M (7번 항목 답변 속도 대조용)
Open WebUI   :8088  (docker)
```

### 실측 항목

1. 문서 수집·청킹 — 청크 크기별 개수
2. 임베딩 차원과 소요 시간
3. Qdrant 색인 상태
4. top-k별 검색 적중
5. 벡터 검색 vs 하이브리드 대조
6. RAG 미적용/적용 답변 대조
7. MoE와 Dense의 답변 생성 속도 차이

### 스크린샷 계획 (10장 목표)

Qdrant Web UI 4장(컬렉션 목록, 포인트 탐색, Visualize 탭, REST 콘솔), Open WebUI 4장(RAG 미적용/적용 답변 대조, 지식 관리), 검색 스코어 2장.

## 제작 파이프라인

각 편은 6단계를 순서대로 거친다(CLAUDE.md §11).

| 단계 | 작업 | 담당 |
|---|---|---|
| 1 | 기획안 작성 | Opus |
| 2 | 기획의 유효성·의미 검증 | Fable |
| 3 | 실습 수행·스크린샷 촬영 | Sonnet |
| 4 | 글 작성 | Opus |
| 5 | 올바른 정보만 담겼는지 검증 | Fable |
| 6 | git 푸시·블로그 게시 | Sonnet |

1편과 3편은 실측이 없는 정리 글이므로 3단계를 생략한다.

집필 에이전트에게 항상 명시할 것(§11): 편 번호·연재 언급 금지, 검증 못한 수치 기입 금지, 실측 불가 환경에서 터미널 출력 캡처 금지, 스크린샷 8~12장 목표와 촬영 후 육안 확인 의무.

## 타임라인

작업은 2026-07-27 01:00 이후에 시작하고 글 사이에 2시간 이상 간격을 둔다.

| 시각 | 작업 |
|---|---|
| 01:07 | 시작. llama.cpp 설치·Qwen3.6 지원 확인, 모델 다운로드 백그라운드 개시, 1편 파이프라인 |
| 03:13 | 2편 파이프라인 |
| 05:11 | 3편 파이프라인 |
| 07:09 | 4편 파이프라인 |

정각·30분을 피해 off-minute로 잡았다.

## 리스크와 대응

| 리스크 | 대응 |
|---|---|
| llama.cpp가 Qwen3.6(qwen3_5_moe)을 아직 지원하지 않을 수 있음 | 01:07 최우선으로 확인. brew 배포판이 안 되면 소스 빌드로 우회. 그래도 안 되면 2편·4편의 모델을 지원 확인된 것으로 교체하고 1편·3편은 그대로 진행 |
| 모델 다운로드 약 90GB가 오래 걸림 | 1편(정리, 모델 불필요) 집필과 겹쳐 백그라운드로 받음 |
| Q8_0 구간에서 macOS GPU wired limit에 걸릴 수 있음 | `iogpu.wired_limit_mb` 조정. 실습의 함정 섹션 소재로 활용 |
| 세션 종료 시 예약이 사라짐 | CronCreate는 세션 한정이다. 세션을 열어두고 `caffeinate`로 절전을 막을 것 |

## 범위 밖

- **멀티모달**: 두 모델 다 mmproj가 있어 vision이 되지만 4편에 담으면 밀도가 떨어진다
- **별도 양자화 정리글**: gpu_07에 양자화 개요 표(GGUF K-quant 포함)가 이미 있어 겹친다. 2편의 실측 섹션으로 흡수
- **vLLM·TensorRT-LLM 비교**: CUDA 전용이라 이 하드웨어에서 실측 불가. gpu_07의 표로 충분

## 게시 전 체크리스트

- frontmatter 순서와 `description` 유무(§3)
- categories 1개, controlled vocabulary 안에 있는지
- (C) 글 명사형 종결 / (A) 글 평서형 `~한다`, 존댓말 없음
- em-dash·en-dash 없음(§7), `### 참고` 섹션 없음(§7)
- AI 흔적 체크리스트(§12), 특히 `oaicite`·`citeturn`·`utm_source=` grep
- 스크린샷 날짜 미노출, dotoryeee 브랜딩 노출(§10)
- `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`로 빌드해 WARNING 없는지
- 배포 후 `curl -s https://dotoryeee.github.io/blog/ | grep -c 'site-verification'`가 2 이상인지(§13)
