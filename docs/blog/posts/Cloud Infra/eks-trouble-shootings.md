---
draft: false
date: 2025-03-11
authors:
  - dotoryeee
categories:
  - Kubernetes
tags:
  - EKS
  - CoreDNS
  - TLS
  - Troubleshooting
description: "Private EKS 클러스터에서 마주친 CoreDNS hosts 수정·OCSP·PKIX·self-signed 인증서 오류 대응을 모은 트러블슈팅 기록"
---
# Private EKS Cluster 트러블슈팅 내역[Draft]

<!-- more -->

- coredns configMap 수정하여 cluster내 hosts 수정하는 방법


- OCSP 에러 발생 시
```sh
curl -v https://test.test.com --ssl-no-revoke
```
--ssl-no-revoke는 Windows(Schannel) 전용 옵션이라 리눅스(OpenSSL)에선 무효하므로, OCSP responder로의 아웃바운드 경로를 열거나 폐기 검사를 수행하는 클라이언트에서 검사를 비활성화할 것

- PKIX path building failed(JAVA Spring)
JAVA IDE의 TrustStore에 SSL 등록해야 함

- openssl verify return code: 19
self-signed 인증서이므로 시스템에 신뢰할 수 인증서로 등록해야함

---
출처:

1. https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/enable-iam-roles-for-service-accounts.html
2. https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/lbc-manifest.html
3. https://stackoverflow.com/questions/76624577/argocd-ingress-kubernetes-too-many-redirects-even-with-insecure-nginx
4. https://husheart.tistory.com/187
5. https://argo-cd.readthedocs.io/en/release-2.5/operator-manual/rbac/
6. https://huntedhappy.tistory.com/entry/DK-Argocd-cli-%EC%84%A4%EC%B9%98-%EB%B0%8F-User-%EC%B6%94%EA%B0%80
7. https://changbaebang.github.io/2021-08-07-redis-cli/
8. https://velog.io/@broccolism/nginx-%EC%82%BD%EC%A7%88%ED%95%98%EA%B8%B0-%EB%94%B1-%EC%A2%8B%EC%9D%80-%EC%84%A4%EC%A0%95
