---
draft: true
date: 2023-10-22
authors:
  - dotoryeee
categories:
  - study
  - Kubernetes
  - Database
  - Cloudnet@
---
# Database on Kubernetes study / Week 1
---
## 목표
1. Kubectl 명령의 흐름
2. CSI
3. PV/PVC
4. CNI
5. Sercice
6. ExternalDNS
7. CoreDNS
8. StatefulSet / HeadlessService
<!-- more -->

---
## 실습
1. Kubectl 명령의 흐름
    ![출처:https://devocean.sk.com/blog/techBoardDetail.do?ID=163578](./doik2/EKS-arch.png)<br>
    출처: https://devocean.sk.com/blog/techBoardDetail.do?ID=163578<br>
    AWS EKS cluter 구축 시 Contorl plane은 무조건 AWS에서 관리하는 VPC에 provisioning되며, worker node만 사용자의 VPC에 구성된다.<br>
    참고: Control plane의 앞단에는 무조건 ALB가 아닌 NLB가 배포된다.
    <br>
    클러스터 관리자가 Kubectl을 이용해 베포 명령 시 아래와 같은 순서로 명령어가 전달된다.<br>
    1. Kubectl은 kubeconfig에 저장된 인증 정보를 로드한다.
    2. Kubectl명령은 AWS에서 관리하는 NLB에 도달한다.
    3. NLB 뒷단에 배치된 Control plane의 API Server에 명령이 전달된다.
    4. API Server는 변경사항을 etcd에 기록합니다.
    5. controller manager는 변경사항을 감지하고 desired state를 유지하기 위해 각종 컨트롤러(Node, Replication, Endpoint, Service Account, Namespace 등)를 동작시킵니다.
    6. Scheduler는 새로운 pod가 위치할 적절한 노드를 예약합니다.
    7. Scheduler가 노드에 pod를 할당하면 kubelet이 감지하고 pod배포를 진행합니다.
    8. kubelet은 CRI -> container runtime을 이용해 pod배포를 진행합니다.
2. CSI
    
3. PV/PVC

4. CNI

5. Sercice

6. ExternalDNS

7. CoreDNS

8.  StatefulSet / HeadlessService



