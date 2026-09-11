# LLM Gateway 워크샵 실습 2편 기획

작성일 2026-09-11. 상태: 게시 완료. Opus 4중 팩트체크(사실 오류 5건, 근거 없는 관측 서술 8건 수정)와 Opus 4중 국문 교정(151건 반영)을 거쳐 draft false로 전환. 사용자가 고른 제목은 "금융망에서 AI 사용하기(Keycloak SSO+LiteLLM)"와 "금융망에서 AI 사용하기(LiteLLM Guardrail+Bedrock Guardrail)", 부제는 "운영자 관점에서 알아보기"와 "개발자(AI 실사용자)와 감사 관점에서 알아보기". 작성일은 1편 2026-09-10, 2편 2026-09-11. 화면의 주소와 키는 워크샵 임시 계정 값이라 마스킹하지 않기로 함.

| 산출물 | 경로 |
|---|---|
| 1편 | `docs/posts/AI/finance_llm_gateway_sso.md`, 이미지 39장 `finance_llm_gateway_sso/` |
| 2편 | `docs/posts/AI/finance_llm_gateway_guardrail.md`, 이미지 36장 `finance_llm_gateway_guardrail/` |
| 크롭 도구 | `/tmp/llmproxy-catalog/imgtool.py` (ruler, crop, copy) |
| 드래프트 포함 빌드 설정 | `/tmp/mkdocs-draft.yml`, 출력 `/tmp/mkdocs-site` |

미해결: Module 5-2 예산 429와 키 폐기, 5-4 CloudWatch, 4-2 Cowork, 4-5 우회 재현은 미실습 또는 미캡처라 문서 서술만 있음. Usage의 실패 14건 원인은 오류 본문을 열어 보지 않아 미확인.

## 재료

| 항목 | 위치 | 비고 |
|---|---|---|
| 워크샵 오프라인 사본 | `~/downloads/llmproxy/claude-llmgateway-workshop/` | AWS Workshop Studio "AI Coding Assistant(Claude Code/Codex/OpenCode) 제공을 위한 LLM Gateway 구축" ko-KR 26페이지. 원문 마크다운은 `src/raw/content/` |
| 실습 스크린샷 | `~/downloads/llmproxy/images/Screenshot 2026-09-10 at *.png` 125장, `2026-09-11 at 17.28.51` 1장 | 9월 10일 10:50에서 16:42 사이 촬영 |
| 워크샵 다이어그램 사본 | `~/downloads/llmproxy/images/*.png` 10장 | AWS 저작물. 공개 블로그에는 mermaid로 다시 그려 쓰는 것을 권장 |
| 스크린샷 카탈로그 | `/tmp/llmproxy-catalog/batch-A.md` 부터 `batch-D.md` | 장별 모듈, 설명, 눈에 띄는 텍스트, 유용도. 임시 경로라 재부팅 시 사라짐 |
| 이벤트 | 시작 9/10 10:01, 72시간 | 9/13 10:01까지 계정 접근 가능. 미캡처 항목 추가 촬영 가능 |

## 기존 글과의 관계

| 기존 글 | 겹치는 부분 | 이번 글에서의 처리 |
|---|---|---|
| `Cloud Infra/ai_gateway.md` AI Gateway 정리 | 게이트웨이 개념, 솔루션 비교, 가드레일 위치 | 개념 설명은 링크로 대체. 이번 글은 실습 기록 |
| `Cloud Infra/ai_gateway_litellm.md` LiteLLM 구축과 운영 | Virtual Key, 예산, 라우팅, 캐시, Prometheus | Ollama 로컬 구성이었음. 이번은 Bedrock, PrivateLink, SSO 임시 키가 새 축 |
| `Cloud Infra/claude_apps_gateway.md` | 개발자에게 키를 주지 않는 Claude Code 게이트웨이 | Cognito 기반 Anthropic 공식 게이트웨이. 이번은 LiteLLM OSS와 Keycloak Device Grant. 비교 문단 1개로 연결 |
| `Cloud Infra/sso.md` | OAuth, OIDC, JWT 기초 | Device Authorization Grant 설명 시 링크 |

공통 태그는 기존 쌍과 묶이도록 `AI Gateway`를 유지하고, `LiteLLM`, `Bedrock`, `Keycloak`, `Claude Code`, `Codex`, `OpenCode`를 편별로 나눠 단다.

## 2편 분할 근거

| 분할안 | 1편 | 2편 | 판단 |
|---|---|---|---|
| A. 역할 기준 (권장) | Module 1, 2, 3. 운영자가 인프라를 확인하고 게이트웨이, 모델, 사용자, IdP, 브로커, 임시 키 발급을 만든다 | Module 4, 5와 프로덕션 로드맵. 개발자가 툴 3종을 붙이고, 우회 차단 계층을 읽고, 감사 로그와 Guardrails를 확인한다 | 스크린샷이 약 38장과 33장으로 균형. 1편은 첫 임시 키로 모델 호출 성공에서 끝나고 2편은 그 키로 툴을 연결하며 시작해 서사가 끊기지 않음 |
| B. 구축과 검증 기준 | Module 1에서 4 | Module 5와 로드맵 | 1편이 스크린샷 98장으로 과중 |
| C. 정리와 실습 기준 | 개념 정리 글 | 실습 글 1편에 전부 | 기존 `ai_gateway.md`와 개념이 겹치고 실습 글이 70장 이상으로 과중 |

A안으로 진행한다. 두 편 모두 `docs/posts/AI/`에 두고 categories는 `AI`, 이미지는 글 파일명과 같은 하위 폴더에 둔다.

| 편 | 파일명 안 | 이미지 폴더 |
|---|---|---|
| 1편 | `llm_gateway_bedrock_sso_key.md` | `llm_gateway_bedrock_sso_key/` |
| 2편 | `llm_gateway_ai_tools_audit.md` | `llm_gateway_ai_tools_audit/` |

## 작성 규칙

- 실습 글이므로 평서형 `~한다`. 존댓말 금지
- 본문 볼드 금지, em dash와 en dash 금지, 임의 번역 괄호 금지, "파헤치기" 금지
- 같은 층위의 개념은 먼저 표로 비교하고 그 뒤 세부로 내려간다. 흐름은 mermaid
- 워크샵 문서 페이지를 찍은 스크린샷은 참고용으로만 쓰고 게시하지 않는다
- 워크샵 다이어그램 PNG는 게시하지 않고 mermaid로 다시 그린다
- CLI 화면 스크린샷은 전체를 싣지 않고 필요한 부분만 줄 단위로 잘라 쓴다 (2026-09-11 사용자 지시). 터미널 한 장에 여러 명령이 섞여 있으면 섹션마다 해당 명령과 출력 줄만 잘라 별도 이미지로 만든다. 예: 13.14.09는 compose up 결과와 헬스체크 줄, 13.21.14는 실패 curl 두 줄과 성공 응답 줄, 14.59.43은 200과 401 줄
- 게시 전 grep으로 `**`, `—`, `–` 0건 확인

## 1편 목차와 스크린샷 배정

시각은 `Screenshot 2026-09-10 at HH.MM.SS.png`의 HH.MM.SS.

| 순서 | 섹션 | 내용 | 스크린샷 | 마스킹 |
|---|---|---|---|---|
| 1 | 이 글에서 만드는 것 | 워크샵 정보 표, 실습 아키텍처 mermaid, 기존 글 링크, 2편 예고 | 10.50.09 이벤트 대시보드 | 계정 정보 |
| 2 | 통제 다섯 가지와 담당 층 | 인증, 상한, 기록, 정책, 킬 스위치가 각각 어느 모듈과 컴포넌트에 놓이는지 표. 운영자와 개발자 페르소나의 자격증명 표 | 없음 | |
| 3 | 네트워크 경로 확인 | VPC 엔드포인트 3개 표 (서비스명, 서브넷, 허용 액션). 접근 제어 3계층 표 (IAM, 엔드포인트 정책, 게이트웨이 모델 목록). 프라이빗 DNS 실측: 로컬 Mac에서는 공인 IP 8개, EC2 안에서는 사설 IP 2개로 풀림 | 11.02.32 엔드포인트 목록, 11.02.37 bedrock-runtime 정책, 11.08.27 로컬 nslookup, 11.08.35 EC2 nslookup | 계정 ID |
| 4 | LiteLLM 기동 | `/opt/workshop` 파일 표, compose 항목 표, nginx 설정 핵심 (`/auth/`는 8080, `/`는 4000, `proxy_buffering off`), 기동 후 첫 헬스체크 실패와 12초 뒤 성공 | 13.14.09 compose up과 헬스체크, 13.14.11 nginx conf, 13.14.03 Swagger, 13.14.05 로그인 화면 | 13.14.09의 DATABASE_URL, MASTER_KEY, SALT_KEY |
| 5 | 모델 등록과 API 포맷 3종 검증 | 등록 모델 8개 표 (Public Model Name, 실제 대상, 라우트 접두어, Provider). 포맷 3종과 툴 대응 표. GATEWAY_URL 미설정으로 실패한 curl 트러블슈팅. gpt-oss-120b가 추론 토큰으로 max_output_tokens 64를 소진해 status incomplete로 끝난 관찰. 스트리밍 SSE 통과. Mantle 경로 등록. 별칭 3개가 필요한 이유. 자격증명 없이 SigV4로 호출되는 구조 | 13.19.19 Add Model, 13.22.28 Test Connect 성공, 13.21.14 messages 포맷, 13.22.41 chat.completions, 13.23.05 스트리밍, 13.23.45 responses 포맷, 13.24.11 Mantle, 13.28.21 모델 8개 UI, 13.28.24 모델 8개 API | 13.21.14와 13.22.41의 Master Key |
| 6 | 사용자와 예산 | Invite User 입력 표, 기본 예산 5달러가 자동 적용된 뒤 2달러로 덮어쓰기, developer002는 0.000001달러, API로 이메일과 UUID 확인. 팀 키에는 개인 예산이 적용되지 않는다는 참고 | 13.35.11 Invite User, 13.36.14 Edit Settings, 13.37.08 사용자 3명, 13.37.36 user/list API | |
| 7 | Keycloak 구성 확인 | realm, 클라이언트, 사용자 표. public 클라이언트에 시크릿도 redirect URI도 없는 이유. 이메일이 IdP와 게이트웨이를 잇는 키라는 점 | 14.14.35 Manage realms | 임시 admin 경고 배너는 그대로 둬도 됨 |
| 8 | Key Vending Broker | LiteLLM JWT Auth가 Enterprise인 제약. 브로커 4단계 표 (서명·issuer·만료, azp, 이메일 조인, /key/generate). broker.env 4줄 표. 기동과 health. Keycloak 도메인으로 보낸 /auth/health는 401, 게이트웨이 도메인은 ok. 1단계 흐름 mermaid sequence | 14.35.35 브로커 기동, 14.35.49 health jq, 14.38.02 도메인별 health 비교 | |
| 9 | SSO 로그인과 임시 키 발급 | 스크립트 4종 표 (gateway-login, get-gateway-key, ensure-gateway-session, 래퍼). Device Grant 화면 4장. 헬퍼 연속 실행 시 같은 키. virtual-key.json 구조. Master Key 없이 첫 모델 호출. 운영자 화면에서 sso 별칭 키 확인. 키 수명 4시간과 1분 상세 화면 대조, 200 뒤 60초 후 401. 2단계 호출 경로 mermaid sequence | 14.39.52 gateway-login.sh 소스, 14.45.30 로그인 대기, 14.45.37 동의 화면, 14.45.42 Device Login Successful, 14.45.46 SSO complete, 14.46.02 키 발급, 14.46.59 virtual-key.json과 첫 호출, 14.47.47 Internal Users 1 Key, 14.48.25 Virtual Keys sso 별칭, 14.54.37 4시간 키 상세, 14.54.54 KEY_DURATION 60s, 14.55.29 1분 키 상세, 14.59.43 200 뒤 401 | 14.46.02, 14.46.59, 14.59.43의 sk- 키 |
| 10 | 정리 | 다섯 통제 중 1편에서 증거를 확보한 항목 표. 2편에서 다룰 것 | 없음 | |

제외: 13.15.08과 13.15.11은 비밀값만 추가된 중복. 14.35.56은 14.35.49와 동일 파일. 14.47.50은 14.47.47과 동일 화면. 14.53.01과 14.53.13은 JWT 전문 노출이라 소스 설명은 14.39.52로 대신함. 워크샵 문서 페이지 캡처 13.24.28, 13.25.32, 13.27.37, 13.28.45, 13.28.52, 13.37.47, 14.15.31, 14.15.41, 14.46.46, 14.54.25는 참고용.

## 2편 목차와 스크린샷 배정

| 순서 | 섹션 | 내용 | 스크린샷 | 마스킹 |
|---|---|---|---|---|
| 1 | 이 글에서 하는 것 | 1편 링크, 전제 (developer001 SSO 세션), 툴 3종 | 없음 | |
| 2 | 키 헬퍼 규약 한 줄과 툴 3종 비교 | 설정 파일, 헬퍼 지정 위치, 만료 처리, 엔드포인트, API 포맷을 한 표로. 헬퍼 하나에 연결 방식 셋 mermaid. 래퍼가 필요한 툴과 아닌 툴 | 없음 | |
| 3 | Claude Code 연결 | settings.json 항목 표와 없을 때 생기는 일. apiKeyHelper 추가 전후. 환경 변수가 헬퍼보다 우선하는 함정. 세션을 지우고 `claude`만 실행해 브라우저 로그인부터 시작까지. 래퍼 2줄과 ensure-gateway-session.sh 11줄. /status가 보고한 인증 방식과 base URL. Virtual Keys에 키 4개가 쌓인 화면 (1분 키 2개 Expired) | 15.24.44 settings.json, 15.26.22 apiKeyHelper 추가, 15.27.42 래퍼가 로그인 시작, 15.28.02 로그인 완료와 온보딩, 15.28.38 첫 대화, 15.29.08 래퍼 소스, 15.30.53 ensure 스크립트, 15.32.25 /status, 15.35.09 키 4개 | |
| 4 | OpenCode 연결 | opencode.json 구조 표. models.dev에 없는 별칭이라 tool_call, limit, cost를 직접 선언. `{env:}`는 변수가 없으면 빈 문자열이 되는 함정과 `{file:}` 교체 전후. TUI 상태줄의 (GW) 표시. 세션 화면의 토큰과 비용. 만료 시 재시작이 필요한 이유 | 15.39.06 설정과 로그인, 15.39.43 TUI 시작, 15.40.21 응답과 비용, 15.42.50 file 참조로 바뀐 설정 | |
| 5 | Codex 연결 | config.toml 항목 표. env_key와 auth 블록의 상호 배타. wire_api는 responses만. OPENAI_BASE_URL 무시. Model metadata 경고. 인증 실패가 Reconnecting으로 보이는 함정 | 15.45.15 config 전후, 15.45.27 TUI 시작, 15.49.02 응답 | 15.45.15의 sk- 키 |
| 6 | 우회는 어디서 막히나 | 시나리오 3개와 차단 층 표. IAM Deny와 NotResource 허용 목록 정책 해설 표. 3층 겹침 mermaid. Cowork 선택 실습은 미진행으로 한 줄 | 없음. 이벤트 만료 전 `codex exec -c model_provider=amazon-bedrock` 재현 캡처 권장 | |
| 7 | 지출과 프롬프트 로그 감사 | /spend/logs의 User-Agent 자동 분류. /user/info의 spend와 max_budget. Usage 대시보드 요약 (요청 47건 중 실패 14건). Logs 목록의 실패 행. Codex 요청 상세의 User-Agent codex-tui (워크샵 문서의 codex_exec와 다름, TUI로 실행했기 때문). OpenCode 요청 원문. 프롬프트 원문은 proxy_server_request 필드. psql 조회. 헬스체크 행은 proxy_server_request도 비어 있음. 툴별 "안녕" 한 번 비용 표 (Codex 7,751토큰, OpenCode 8,074토큰, Claude Code 약 34,000토큰. Claude Code 첫 요청 0.127달러와 다음 요청 0.013달러 차이는 캐시 쓰기와 읽기 단가 차이로 보이며 로그에서 재확인 필요) | 16.14.49 user/info, 16.17.12 Usage 요약, 16.17.16 Top Keys와 Provider, 16.17.30 Request Logs, 16.18.23 Codex 상세, 16.20.45 OpenCode 원문, 16.25.00 psql 결과, 16.25.37 proxy_server_request 빈 값 | 16.25.00의 DB 호스트와 ARN |
| 8 | 예산 발동과 키 폐기 | developer002 키 발급, 429 ExceededBudget, Delete Key 뒤 인증 실패. Block과 Delete와 Reset Spend 용도 표 | 미캡처. 이벤트 만료 전 촬영 권장. 불가하면 문서 서술만 | |
| 9 | PII 마스킹과 Guardrails | 두 계층 비교 표 (실행 위치, 정책 표현, 동작, 적용 범위, mode). pii_filter.py 정규식 2개. config 추가와 재생성, 기동 직후 헬스체크 실패 2회. Claude Code 응답에 [KR-RESIDENT-ID]와 [KR-MOBILE]. 로그에 저장된 것도 마스킹본. Bedrock 콘솔의 ws-guardrail. LiteLLM Guardrails 등록 전후. 400 Violated guardrail policy. Guardrail 삭제 뒤 같은 프롬프트에 모델 자체 거절이 정상 응답으로 돌아온 대조. pre_call 뒤 during_call 실행 순서 | 16.32.04 pii_filter.py, 16.33.49 config와 재기동, 16.34.17 마스킹 응답, 16.34.49 마스킹된 로그, 16.38.56 Bedrock Guardrail, 16.39.17 pii-mask만, 16.40.59 두 개 등록, 16.41.32 400 차단, 16.41.55 삭제 후 모델 거절 | 16.38.56과 16.40.37의 계정 ID |
| 10 | OTel과 CloudWatch | LiteLLM에 CloudWatch 네이티브 콜백이 없고 OTel과 ADOT를 거친다는 구조 표 | 미캡처. CloudWatch EC2 CPU 그래프 촬영 권장 | |
| 11 | 프로덕션 로드맵 | IdP 교체 시 바뀌는 값 1줄. 인증 구조 선택지 A, B, C 표. 완전 프라이빗망에서 바뀌는 절반과 안 바뀌는 절반. 수천 명 구간에서 Redis가 필수인 이유 | 없음. production-arch.png는 mermaid로 재작성 | |
| 12 | 정리 | 다섯 통제와 확인한 증거 표 | 없음 | |

제외: 15.27.38 과도기, 15.28.07은 15.28.02와 같은 순간, 16.13.34는 16.14.49에 포함, 16.18.49와 16.18.57은 같은 상세 스크롤, 16.40.40은 16.40.37 중복, 16.41.47 삭제 모달은 선택, 09-11 17.28.51은 16.41.55 재캡처. 문서 페이지 캡처 15.29.32, 15.40.30, 15.52.44, 15.52.50, 16.22.20, 16.23.01, 16.25.21, 16.42.12는 참고용.

## 마스킹이 필요한 스크린샷

| 종류 | 파일 |
|---|---|
| Master Key, DB 접속 문자열, SALT | 13.14.09, 13.21.14, 13.22.41 |
| Keycloak 비밀번호 평문 | 14.45.25 (미사용 예정) |
| 발급된 sk- 키 | 14.46.02, 14.46.12, 14.46.59, 14.59.43, 15.45.15 |
| JWT 전문 | 14.53.01, 14.53.13 (미사용 예정) |
| DB 호스트와 시크릿 ARN | 16.25.00 |
| AWS 계정 ID | 11.02.32, 11.02.37, 11.02.40, 11.02.41, 14.53.18, 16.38.56, 16.40.37, 16.40.40 |

## 이벤트 만료 전 추가 촬영 권장

| 항목 | 이유 |
|---|---|
| 5-2 예산 발동과 키 폐기 | 다섯 통제 중 킬 스위치의 유일한 실습 증거. 현재 0장 |
| 5-4 CloudWatch EC2 지표 | 2편 10절 화면 |
| 4-5 시나리오 1 재현 | `codex exec --skip-git-repo-check -c model_provider=amazon-bedrock "1 + 1은?"`의 AccessDenied |
| 2-2 CloudTrail InvokeModel | vpcEndpointId가 남는 레코드. 1편 3절 또는 2편 6절의 운영 증거 |
| Logs 실패 14건 원인 | 15:49에서 15:54 사이 claude-sonnet-5 3건, claude-sonnet-4-6 6건 실패. 상세를 열어 오류 본문 확인 |

## 제목 후보

1편

1. Bedrock 앞에 LLM Gateway 세우기: LiteLLM 구축부터 Keycloak SSO 임시 키 발급까지
2. 개발자에게 API 키를 주지 않는 LLM Gateway 구축기 1편: 인프라, LiteLLM, Key Vending Broker
3. AI 코딩 툴용 LLM Gateway 실습 1편: 게이트웨이 운영자가 하는 일
4. LiteLLM과 Keycloak으로 만드는 4시간짜리 API 키
5. PrivateLink 위의 LLM Gateway: Bedrock 모델 등록과 SSO 임시 Virtual Key 발급
6. 정적 API 키 없이 Bedrock 열어 주기: LLM Gateway와 Key Vending Broker 구축
7. 사내 AI 코딩 툴 도입 1편: LLM Gateway 구축과 SSO 임시 키 발급 실습
8. LiteLLM 무료 버전만으로 SSO 임시 키 발급 체계 만들기
9. Claude Code, Codex, OpenCode를 위한 LLM Gateway 구축 1편: 네트워크, 모델, 사용자, 인증
10. Master Key는 브로커까지만: LLM Gateway 운영자 관점의 구축 기록

2편

1. AI 코딩 툴 3종을 LLM Gateway에 붙이고 감사하기: Claude Code, OpenCode, Codex
2. 개발자에게 API 키를 주지 않는 LLM Gateway 구축기 2편: 툴 연결, 우회 차단, 감사와 Guardrails
3. 헬퍼 스크립트 하나로 Claude Code, Codex, OpenCode 연결하기
4. 게이트웨이를 지나지 않은 호출은 남지 않는다: AI 코딩 툴 연결과 우회 차단 3계층
5. 누가 어떤 툴로 무엇을 물었고 얼마를 썼는가: LLM Gateway 감사 로그와 Guardrails 실습
6. 사내 AI 코딩 툴 도입 2편: 툴 연결, 프롬프트 로그 감사, PII 마스킹과 Guardrails
7. 안녕 한 번에 얼마인가: 툴별 토큰 오버헤드와 LLM Gateway 감사 실습
8. Claude Code, Codex, OpenCode를 위한 LLM Gateway 구축 2편: 연결, 감사, 통제
9. LLM Gateway 운영 실습: 툴 연결부터 주민등록번호 마스킹과 Bedrock Guardrails 차단까지
10. 키 헬퍼 규약과 감사 가능성: AI 코딩 툴을 LLM Gateway로 통제한 기록

## 도입문 후보

1편

1. AWS 워크샵에서 Amazon Bedrock 앞에 LiteLLM 게이트웨이를 직접 올리고, Keycloak SSO 로그인만으로 4시간짜리 임시 API 키를 받는 구조까지 만들었다. 정적 키를 한 번도 배포하지 않는 것이 목표였고, 그 과정을 운영자 관점에서 기록한다.
2. 개발자들이 각자 API 키를 발급받아 AI 코딩 툴을 쓰기 시작하면 누가 무엇을 얼마나 쓰는지 아무도 답할 수 없게 된다. 이 글은 모든 모델 호출이 반드시 지나는 단일 진입점을 세우고, 그 진입점에 사람을 연결하는 인증 체계를 만든 실습 기록이다.
3. LLM Gateway 워크샵 실습을 두 편으로 나눠 정리한다. 1편은 VPC 엔드포인트 정책 확인부터 LiteLLM 기동, 모델 8개 등록, 사용자 예산 설정, Key Vending Broker 구성, SSO 임시 키 발급까지 운영자가 하는 일이다.
4. LiteLLM의 JWT 인증은 Enterprise 라이선스가 필요하다. 무료 버전만으로 같은 효과를 내기 위해 Keycloak 앞에 120줄짜리 FastAPI 브로커를 두고 4시간 만료 Virtual Key를 발급하는 구조를 직접 구성했다.
5. Claude Code, Codex, OpenCode가 각각 다른 API 포맷을 쓰는데도 게이트웨이 하나로 받을 수 있는지, 그 게이트웨이가 인터넷을 거치지 않고 Bedrock에 닿는지, 개발자에게 키를 배포하지 않고도 인증이 되는지 세 가지를 확인했다.
6. 이 글에서 만든 것은 세 가지다. PrivateLink로만 Bedrock에 닿는 LiteLLM 게이트웨이, 부르는 이름과 실제 대상을 분리한 모델 별칭 8개, 그리고 SSO 로그인 결과로 생성되어 4시간 뒤 사라지는 Virtual Key다.
7. Master Key는 브로커까지만 간다. 개발자 PC에 도달하는 것은 만료되는 임시 키뿐이다. 이 원칙 하나를 지키기 위해 네트워크, 게이트웨이, IdP, 브로커 네 층을 차례로 확인하고 구성한 기록이다.
8. 워크샵 계정에 준비된 것은 EC2, RDS, CloudFront, VPC 엔드포인트, Keycloak realm까지였다. 컨테이너를 시작하는 것부터가 실습이었고, 이 글은 그 시작부터 첫 임시 키로 모델을 호출하기까지를 스크린샷과 함께 남긴다.
9. 사내 AI 코딩 툴 도입 검토에서 막히는 지점은 게이트웨이 구축이 아니라 개발자에게 키를 어떻게 주느냐였다. 워크샵에서 그 답을 SSO 기반 임시 키 발급으로 구현해 보고, 키 수명을 1분으로 줄여 만료까지 직접 확인했다.
10. 기존에 정리한 AI Gateway 개념과 LiteLLM 실습에 이어, 이번에는 Amazon Bedrock과 사내 IdP를 전제로 한 구성을 다룬다. 다른 점은 자격증명이다. 모델 쪽은 인스턴스 역할의 SigV4, 개발자 쪽은 SSO 임시 키라 어디에도 저장된 비밀값이 없다.

2편

1. 1편에서 만든 게이트웨이와 임시 키에 Claude Code, OpenCode, Codex를 연결했다. 헬퍼 스크립트 하나를 세 툴의 설정 파일에 각각 다른 방식으로 지정하는 것이 전부였고, 그 뒤 로그에서 누가 어떤 툴로 무엇을 물었고 얼마를 썼는지 확인했다.
2. 게이트웨이를 세웠다고 통제가 끝나는 것은 아니다. 툴 설정 한 줄로 게이트웨이를 우회할 수 있고, 예산은 설정한 것과 발동하는 것이 다르며, 프롬프트 원문이 어느 필드에 남는지 알아야 감사에 답할 수 있다. 2편은 이 세 가지를 확인한 기록이다.
3. AI 코딩 툴 세 종은 API 포맷도 키를 읽는 방식도 다르다. Claude Code와 Codex는 명령을 실행해 키를 받고 OpenCode는 파일에서 읽는다. 같은 임시 키를 세 툴에 넣는 방법과 만료 시 각 툴이 어떻게 복구하는지 정리한다.
4. 안녕 한 마디를 보내는 데 Claude Code는 3만 토큰이 넘게 들고 Codex는 8천 토큰이 든다. 게이트웨이 로그를 열어 보면 툴별 오버헤드가 그대로 보인다. 이 글은 툴을 연결한 뒤 그 로그를 읽고, PII 마스킹과 Guardrails로 입력을 통제한 실습이다.
5. 감사 심사에서 나오는 질문은 늘 같다. 누가, 어떤 툴로, 무엇을 물었고, 얼마를 썼는가. 워크샵 후반부에서 이 네 가지를 게이트웨이 화면 하나와 SQL 쿼리 세 개로 답하는 방법을 확인했고, 주민등록번호가 모델에 닿기 전에 가려지는 것까지 봤다.
6. 2편은 개발자 역할로 시작한다. 툴 이름만 실행하면 브라우저 로그인이 열리고 키는 한 번도 보지 않은 채 Claude Code가 시작된다. 그 뒤 운영자로 돌아가 로그, 예산, Guardrails가 실제로 작동하는지 확인했다.
7. 게이트웨이를 지나지 않은 호출은 예산에도 로그에도 남지 않는다. 그래서 우회를 막는 것은 게이트웨이가 아니라 자격증명, IAM, 네트워크 세 계층의 몫이다. 툴 연결 실습에 이어 이 세 계층이 각각 무엇을 막는지 정책 파일로 확인했다.
8. 1편이 운영자가 준비하는 쪽이었다면 2편은 개발자가 쓰는 쪽과 감사팀이 보는 쪽이다. 툴 세 종 연결, 우회 차단 계층, 지출과 프롬프트 로그, 한국형 PII 마스킹, Bedrock Guardrails 차단, 프로덕션으로 갈 때 바꿀 것을 순서대로 다룬다.
9. LiteLLM Custom Guardrail로 주민등록번호를 가리고 Bedrock Guardrails로 폭력 프롬프트를 차단했다. 두 계층이 어떤 순서로 실행되는지, Guardrail을 지우면 모델 자체 거절과 어떻게 다르게 보이는지까지 Claude Code 화면으로 비교했다.
10. 워크샵 마지막 모듈은 만든 것이 실제로 작동하는지 증거를 모으는 시간이었다. 툴별 User-Agent가 자동으로 분류되는 로그, 마스킹된 채 저장된 프롬프트, 게이트웨이가 돌려준 400 차단 응답을 스크린샷으로 남기고 프로덕션 로드맵을 정리한다.

## 열린 결정

1. 분할안 A 확정 여부
2. 편별 제목 선택
3. 편별 도입문 선택
4. 이벤트 만료 전 5-2, 5-4, 4-5, CloudTrail 추가 촬영 여부
5. 워크샵 다이어그램을 mermaid로 재작성하는 방침 동의 여부
6. 스크린샷 마스킹 방식 (직접 크롭 또는 스크립트로 검은 박스)
