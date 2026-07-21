---
draft: false
date: 2026-07-19
authors:
  - dotoryeee
categories:
  - DevOps
description: "mkdocs gh-deploy 푸시는 됐는데 글이 404, GitHub Pages 빌드가 building에서 멈춘 원인을 gh api로 격리하고 재빌드로 푼 기록"
---

# GitHub Pages 배포 미반영 이슈 요약

<!-- more -->

## 증상

mkdocs gh-deploy로 새 포스트를 배포했고 gh-pages 브랜치 푸시도 성공했지만, 라이브 블로그 인덱스에 글이 노출되지 않고 포스트 URL은 404 응답

---

## 원인 파악 절차

|확인 지점|방법|결과|
|---|---|---|
|로컬 빌드|mkdocs build 후 site/blog/index.html 확인|정상 (글 포함)|
|gh-pages 브랜치|git ls-tree, git show로 배포 산출물 확인|정상 (페이지·인덱스 포함)|
|라이브 사이트|포스트 URL 직접 접근|404 (미반영)|
|Pages 빌드 상태|gh api로 builds/latest 조회|building에서 멈춤|

- 소스·빌드·푸시가 전부 정상인데 라이브만 미반영 → 브라우저/CDN 캐시가 아니라 GitHub Pages 빌드 단계 문제
- 빌드 이력 조회 결과 평소 22~26초에 끝나던 빌드가 15분 이상 building 상태로 스턱

---

## 조치

```s
# 최신 빌드 상태 확인
gh api repos/<owner>/<repo>/pages/builds/latest

# 빌드 이력 확인 (평소 소요 시간과 비교)
gh api "repos/<owner>/<repo>/pages/builds?per_page=5"

# 플랫폼 장애 여부 확인
curl -s https://www.githubstatus.com/api/v2/components.json

# 스턱된 빌드 재요청
gh api -X POST repos/<owner>/<repo>/pages/builds
```

- 플랫폼 상태는 operational → 개별 빌드 스턱으로 판정
- 재빌드 요청 후 21초 만에 built 완료, 라이브 정상 반영 확인

---

## 결론

- gh-pages 푸시 성공 ≠ 라이브 반영. 글이 안 보이면 캐시 탓하기 전에 Pages 빌드 상태부터 확인할 것
- 점검 순서는 로컬 빌드 → 브랜치 산출물 → Pages 빌드 상태 → CDN 캐시 순서로 안쪽에서 바깥쪽으로 격리
- "푸시 성공"이 아니라 "Pages 빌드 완료"가 배포의 끝이라고 이해하면 됌
