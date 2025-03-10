---
draft: false
date: 2025-03-11
authors:
  - dotoryeee
categories:
  - Cloud
  - Kubernetes
---
# Private EKS Cluster 트러블슈팅 내역[Draft]

<!-- more -->

- coredns configMap 수정하여 cluster내 hosts 수정하는 방법


- OCSP 에러 발생 시
```sh
curl -v https://test.test.com --ssl-no-revoke
```
curl의 k 옵션과 전혀 다른 옵션임에 유의할 것

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
