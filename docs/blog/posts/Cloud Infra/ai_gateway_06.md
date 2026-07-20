---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - Cloud
  - AI
  - Security
hide:
  - toc
---
# AI Gateway 가드레일 정리

<!-- more -->

가드레일(Guardrail)이란 게이트웨이 계층에서 LLM 입출력을 검사하고 정책 위반 시 차단·마스킹하는 콘텐츠 통제 계층

---

## 위협 모델 정리

게이트웨이가 막아야 할 대상은 앱이 아니라 프롬프트·응답에 실린 콘텐츠

|위협|설명|게이트웨이 대응|
|----|----|--------------|
|프롬프트 인젝션(Prompt Injection)|사용자 입력에 지시문을 섞어 시스템 프롬프트를 무력화|pre-call 입력 검사, 패턴·인젝션 분류기|
|탈옥(Jailbreak)|역할극·인코딩으로 안전 정책을 우회|입력 검사 + 전용 탈옥 분류기(Prompt Shields류)|
|PII 유출 (입력)|사용자가 개인정보를 프롬프트에 그대로 포함|pre-call 입력 마스킹·차단|
|PII 유출 (출력)|모델 응답에 개인정보·학습 데이터가 노출|post-call 출력 마스킹·차단|
|유해 콘텐츠|혐오·폭력·성적 응답 생성|콘텐츠 모더레이션 분류로 차단|
|시스템 프롬프트 유출|추출 공격으로 내부 지침·규칙이 노출|출력 검사로 지침 문자열 차단|
|과금 남용|가상 키 유출로 토큰을 과소비|가상 키·rate limit·예산 한도로 별도 통제|

- 입력·출력은 서로 다른 위협 → 한쪽 훅만으로는 절반만 방어
- 인젝션·탈옥·유출은 경계가 겹침 → 단일 분류기보다 다층 배치가 현실적

---

## 가드레일 동작 위치

LiteLLM은 요청 파이프라인의 위치별로 훅을 걸 수 있음

- pre-call: LLM 호출 전 입력을 검사해 프로바이더 도달 전에 차단·마스킹으로 개입
- post-call: 응답 수신 후 입력과 출력을 함께 검사해 유출·유해 응답을 최종 차단
- during-call: LLM 호출과 병렬로 입력만 검사, 추가 지연을 줄이는 용도(블로킹 아님)
- logging-only: 요청 흐름은 그대로 두고 로그에만 마스킹 적용

탐지 후 처리 방식은 세 가지로 갈림

|모드|동작|적합|
|----|----|----|
|차단(Block)|정책 위반 시 요청·응답 자체를 4xx로 거부|인젝션·금칙 주제|
|마스킹(Mask)|탐지 구간만 placeholder로 치환하고 통과|PII 처리|
|로깅(Logging)|흐름 변경 없이 탐지 사실만 기록|정책 튜닝·관측|

---

## 구현 방식 비교

정확도와 비용은 대체로 같은 방향으로 올라감

|방식|동작|장점|단점·비용|
|----|----|----|--------|
|정규식·휴리스틱|고정 패턴·키워드 매칭|빠름, 무료, 외부 의존성 없음|문맥을 못 봐 오탐·미탐이 큼|
|PII 탐지 엔진 (Presidio)|NER·정규식·체크섬 조합, 신뢰도 점수 산출|MIT 오픈소스, 셀프호스팅, 다국어 지원|별도 서비스 운영 부담, 완전 탐지 보장 없음|
|LLM 판정 (LLM Judge)|별도 LLM이 입출력을 정책 기준으로 평가|문맥 이해, 자연어로 유연한 정책 표현|검사 호출마다 토큰 비용·지연 가산|
|벤더 관리형|Bedrock Guardrails·Azure AI Content Safety·Lakera 등 관리형 API|운영 부담 없음, 정책 세트·분류기 완비|텍스트 단위 종량 과금, 외부 전송 발생|

- Presidio는 무료 OSS로, Analyzer가 엔티티 위치·유형·신뢰도를 반환하고 Anonymizer가 치환
- Bedrock Guardrails는 정책별 종량 과금 → 콘텐츠 필터·민감정보 필터는 유료, 단어·정규식 기반 필터는 무료
- Azure AI Content Safety는 혐오·성적·폭력·자해 4개 범주 + 인젝션 탐지(Prompt Shields), 텍스트 레코드 단위 과금
- 벤더 가드레일 대부분은 유료 관리형 → 오픈소스 코어와 경계 확인 필요

---

## LiteLLM 설정 예시

게이트웨이의 litellm_config.yaml에 guardrails 블록을 추가하는 형태. 설정 형태는 다음과 같음(공식 문서 기준)

```yaml title="litellm_config.yaml"
guardrails:
  - guardrail_name: "pii-input-mask"       # 입력 PII 처리
    litellm_params:
      guardrail: presidio                  # Presidio 엔진 연동(별도 컨테이너 기동)
      mode: "pre_call"                      # LLM 호출 전 입력 검사
      presidio_score_thresholds:
        ALL: 0.7                            # 신뢰도 0.7 미만 탐지는 무시
      pii_entities_config:
        EMAIL_ADDRESS: "MASK"               # 이메일은 마스킹 후 통과
        CREDIT_CARD: "BLOCK"                # 카드번호는 요청 자체를 차단

  - guardrail_name: "pii-output-check"      # 출력 검사
    litellm_params:
      guardrail: presidio
      mode: "post_call"                     # 응답 수신 후 입력+출력 검사
      default_on: true                      # 모든 요청에 자동 적용
```

- mode는 배열도 허용 → `mode: [pre_call, post_call]`로 입출력 동시 검사
- guardrail 값을 aporia·bedrock·lakera 등으로 바꾸면 벤더 가드레일로 교체됨
- MASK는 `<CREDIT_CARD>` 형태 placeholder로 치환, BLOCK은 요청을 거부

---

## 운영 주의

- 오탐↔미탐 트레이드오프: 신뢰도 임계값을 낮추면 오탐↑, 높이면 미탐↑ → 도메인별 튜닝 필요
- 지연 추가: pre-call·post-call은 요청 경로에 직렬로 붙어 응답 지연↑, during-call 병렬화로 완화
- 가드레일 자체 비용: LLM 판정·벤더 가드레일은 검사 호출이 곧 과금이라 원 호출 비용에 가산됨
- 감사 로그: 차단·마스킹 이벤트를 별도 로그로 남겨 정책 튜닝과 규정 준수 근거로 활용
- 단일 가드레일로는 완전 차단이 불가능해 입출력 양방향에 서로 다른 방식을 겹쳐 배치하는 편이 현실적

---

### 참고
- LiteLLM Guardrails Quick Start: https://docs.litellm.ai/docs/proxy/guardrails/quick_start
- Microsoft Presidio 공식 문서: https://microsoft.github.io/presidio/
- Amazon Bedrock Guardrails 문서: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-how.html

---

## 결론
- 가드레일은 위협을 pre-call·post-call 훅에서 차단·마스킹·로깅으로 처리하는 정책 계층
- 구현은 정규식 → Presidio → LLM 판정 → 벤더 관리형 순으로 정확도와 비용이 함께 상승
- 가드레일 자체가 지연·비용·오탐을 유발 → 임계값 튜닝과 감사 로그가 운영의 핵심
- 입력 검사는 "안으로 못 들어오게", 출력 검사는 "밖으로 못 나가게" 막는 양방향 문
