---
draft: false
date: 2025-09-04
authors:
  - dotoryeee
categories:
  - Kubernetes
---
# Kubernetes CNI 비교

|CNI|오버레이/암호화 옵션|데이터플레인/서비스 처리|kube-proxy 대체|
|----|----------------|---------------------|---------------|
|Amazon VPC CNI|오버레이 없음(언더레이 VPC 네이티브). Prefix Delegation, SG for Pods 등. 암호화는 VPC 계층(VPN/PrivateLink/WireGuard 외부)로 처리. |리눅스 기본 스택(Netfilter 경로 사용 가능). 네트워크 폴리시 네이티브 지원 추가됨. 서비스 처리는 기본 kube-proxy에 의존. |기본은 미대체(별도 eBPF LB 없음). kube-proxy 사용 권장. |
|Calico|오버레이 off(BGP 라우팅) 또는 on(VXLAN/IPIP). eBPF 모드에서는 IPIP 미지원, VXLAN 또는 비오버레이 권장. WireGuard로 암호화 가능. |표준 리눅스 데이터플레인(iptables 또는 nftables) 또는 eBPF 데이터플레인 선택. 정책/서비스를 해당 데이터플레인으로 집행. |eBPF 모드에서 kube-proxy-free 가능(서비스 LB/NAT을 eBPF로). 표준 모드에선 kube-proxy 사용. |
|Cilium|오버레이 on(VXLAN/Geneve) 또는 네이티브 라우팅 모드. BGP 등 유연한 라우팅 통합. |eBPF 기반 데이터플레인. L3/L4 LB, 정책, 관측 기능을 eBPF로 처리. 소켓 레벨 LB, XDP 가속 등. |완전 대체 가능(kube-proxy-free). eBPF 해시테이블로 대규모 스케일 지원. |
|Flannel|주로 VXLAN 오버레이(단순/경량). 다른 백엔드도 있으나 VXLAN 권장. 암호화는 기본 제공 X(외부 조합). |단순 오버레이(데이터플레인 특화 기능 적음). 정책 집행은 별도 엔진(예: Calico policy-only) 필요. 서비스는 kube-proxy. |미대체. kube-proxy 필요. |
|Antrea (OVS)|오버레이 on(VXLAN/Geneve). 선택적 IPsec 암호화 제공. |Open vSwitch(OVS) 데이터플레인. 에이전트가 OVS 브리지/플로우 설치로 포워딩·정책 집행. |기본적으로 kube-proxy 사용. 일부 기능으로 서비스 가속 있으나 일반적으로 대체 아님. |
|Weave Net|메쉬 오버레이(“fast datapath”로 커널 OVS datapath 활용, fallback “sleeve”). 암호화 선택 가능(구성에 따라). |커널 OVS datapath 활용한 빠른 경로와 캡슐화 경로 혼용. 정책은 별도 또는 Weave 자체 기능 범위. |일반적으로 kube-proxy 사용. 대체 아님. |

<!-- more -->
