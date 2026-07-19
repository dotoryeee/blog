---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - Cloud
  - AI
hide:
  - toc
---
# AI Gateway 솔루션 비교

<!-- more -->

셀프호스팅 운영 부담을 기준으로 대표 5개 AI Gateway 솔루션을 배포 형태·핵심 기능·라이선스 관점에서 비교

---

## 비교표

|솔루션|배포 형태 / 라이선스|라우팅·폴백|캐싱|가드레일|관측성|비고|
|------|------------------|---------|-----|-------|------|-----|
|LiteLLM|셀프호스팅(Docker·Helm). MIT 오픈소스, Enterprise 유료 티어(SSO·RBAC·감사 로그).|지원. 폴백 체인·num_retries·다중 키 로드밸런싱.|Exact·Semantic 모두 지원.|지원. hook 플러그인·외부 가드레일 연동.|지원. 토큰·비용 추적, 로그, Admin UI.|OpenAI 호환 단일 API, 140+ 프로바이더. k8s는 Helm 차트로 배포.|
|Kong AI Gateway|셀프호스팅(Kong Gateway 플러그인)·Konnect SaaS. Gateway는 Apache 2.0, 고급 AI 기능은 Enterprise 유료.|지원. AI Proxy Advanced의 다중 LB 알고리즘·재시도·폴백(고급은 Enterprise).|Semantic 캐시(Enterprise).|지원. AI Prompt Guard(OSS), PII 마스킹·시맨틱 가드레일(Enterprise).|지원. 토큰·지연·비용, OpenTelemetry.|기존 Kong 운영 조직에 적합. 기능별 플러그인 조합. KIC로 k8s 연동.|
|Portkey|셀프호스팅·관리형 SaaS. MIT 오픈소스(2026년 거버넌스·관측 기능까지 오픈소스화).|지원. 가중치 로드밸런싱·조건부 라우팅·폴백·자동 재시도.|Simple·Semantic 모두 지원.|지원. 40+ 가드레일 플러그인.|지원. 요청·비용·지연 대시보드.|1,600+ LLM. 가드레일 통합이 강점. Docker·k8s 셀프호스팅.|
|Cloudflare AI Gateway|완전 관리형(셀프호스팅 없음). 상용, 무료 티어 + 유료.|지원. Dynamic Routing·자동 폴백.|Exact 캐시.|지원. 콘텐츠 모더레이션·DLP.|지원. Analytics·로깅.|프로바이더 앞단 프록시. 인프라 운영 부담 없음. k8s 무관.|
|Envoy AI Gateway|셀프호스팅(Kubernetes). Apache 2.0 오픈소스.|지원. 통합 모델 카탈로그·자동 failover.|미지원(시맨틱 캐시 로드맵).|코어 미제공(상용 애드온으로 보강).|지원. OpenTelemetry·OpenInference 트레이싱.|Gateway API·Inference Extension 기반 k8s 네이티브. Envoy Gateway 확장.|

---

## 선택 가이드

|상황|추천|사유|
|----|----|----|
|빠른 셀프호스팅 시작|LiteLLM|Docker 한 방 기동, OpenAI 호환, MIT. 폴백·키 관리 즉시 사용.|
|기존 Kong 운영 조직|Kong AI Gateway|이미 쓰는 API 플랫폼에 AI 플러그인만 추가. 학습 곡선 최소.|
|가드레일·거버넌스 중심|Portkey|다수 가드레일 내장, 완전 오픈소스, 1,600+ LLM 커버.|
|운영 부담 최소 완전 관리형|Cloudflare AI Gateway|프로바이더 앞단에 얹기만 하면 됨. 서버·업그레이드 관리 불필요.|
|Kubernetes 네이티브|Envoy AI Gateway|Gateway API 표준 기반, Apache 2.0, 기존 Envoy 운영과 통합.|

---

### 참고
- Kong AI Gateway 공식 문서: https://developer.konghq.com/ai-gateway/
- Cloudflare AI Gateway Features: https://developers.cloudflare.com/ai-gateway/features/
- Envoy AI Gateway 공식 문서: https://aigateway.envoyproxy.io/docs/

---

## 결론
- 셀프호스팅 유연성 우선이면 LiteLLM·Portkey(오픈소스), 운영 부담 최소면 Cloudflare(관리형)
- Kubernetes 표준 위에 얹으려면 Envoy AI Gateway, 기존 API 플랫폼 재활용이면 Kong
- 시맨틱 캐시·가드레일 등 고급 기능은 오픈소스 코어와 유료 티어 경계를 배포 전 확인 필요
- 다음 편에서는 라우팅·폴백 전략 심화 예정
- 오픈소스는 "직접 굴리는 게이트웨이", 관리형은 "맡겨두는 게이트웨이"로 나눠 상황에 맞게 고르면 됌
