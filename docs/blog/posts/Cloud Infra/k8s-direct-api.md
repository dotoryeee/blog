---
draft: false
date: 2025-03-26
authors:
  - dotoryeee
categories:
  - Kubernetes
---
# Kubectl 없이 Kubernetes API Server 직접 호출하는 방법

<!-- more -->

1. Kubernetes 접속 정보 가져오기(api endpoint, name)
```sh hl_lines="6 7"
controlplane ~ ➜  k config view -o yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://controlplane:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: kubernetes-admin@kubernetes
kind: Config
preferences: {}
users:
- name: kubernetes-admin
  user:
    client-certificate-data: DATA+OMITTED
    client-key-data: DATA+OMITTED
```
2. 부트스트랩 토큰 secret 이름 확인
```sh
controlplane ~ ➜  kubectl get secrets -n kube-system | grep 'bootstrap-token-*'
bootstrap-token-cfs356   bootstrap.kubernetes.io/token   6      30m
```
3. 수집 대상 토큰 정보 확인
```sh hl_lines="6 7"
controlplane ~ ➜  k -n kube-system get secret bootstrap-token-cfs356 -o yaml
apiVersion: v1
data:
  auth-extra-groups: c3lzdGVtOmJvb3RzdHJhcHBlcnM6a3ViZWFkbTpkZWZhdWx0LW5vZGUtdG9rZW4=
  expiration: MjAyNS0wMy0yN1QwMDoxMTowNFo=
  token-id: Y2ZzMzU2
  token-secret: NnBvYmNjOTNmNGswMXhobg==
  usage-bootstrap-authentication: dHJ1ZQ==
  usage-bootstrap-signing: dHJ1ZQ==
kind: Secret
metadata:
  creationTimestamp: "2025-03-26T00:11:04Z"
  name: bootstrap-token-cfs356
  namespace: kube-system
  resourceVersion: "249"
  uid: cb9b0f6e-af44-40a9-b1d7-f44313678416
type: bootstrap.kubernetes.io/token
```
4. 토근 base64 디코딩
```sh
controlplane ~ ✖ echo Y2ZzMzU2 | base64 --decode
cfs356
controlplane ~ ➜  echo NnBvYmNjOTNmNGswMXhobg== | base64 --decode
6pobcc93f4k01xhn
```
5. kubectl 없이 API 직접 호출
    1. 토큰 없을때
    ```sh
    controlplane ~ ➜  curl --insecure https://controlplane:6443/api
    {
    "kind": "Status",
    "apiVersion": "v1",
    "metadata": {},
    "status": "Failure",
    "message": "forbidden: User \"system:anonymous\" cannot get path \"/api\"",
    "reason": "Forbidden",
    "details": {},
    "code": 403
    }
    ```
    2. 토큰 있을떄
    ```sh
    controlplane ~ ➜  curl --insecure https://controlplane:6443/api -H "Authorization: Bearer cfs356.6pobcc93f4k01xhn"
    {
    "kind": "APIVersions",
    "versions": [
        "v1"
    ],
    "serverAddressByClientCIDRs": [
        {
        "clientCIDR": "0.0.0.0/0",
        "serverAddress": "192.168.58.188:6443"
        }
    ]
    }
    ```
