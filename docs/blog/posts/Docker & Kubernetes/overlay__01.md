---
draft: false
date: 2025-09-10
authors:
  - dotoryeee
categories:
  - Kubernetes
---
# Overlay 비교

## Network Overlay MTU & Encryption (IPIP, VXLAN, Geneve)

Kubernetes CNI 설정 시 오버레이 프로토콜별 암호화 지원 및 추가 오버헤드 영향 정리


## 비교표 (IPv4 기준)

| 프로토콜 | 기본 오버헤드(캡슐화) | 권장 MTU 산식 예(언더레이 1500) | 암호화 지원/방식 | 암호화 추가 오버헤드(예) | 암호화 적용 후 MTU 예시 | 자원/특이점 |
|---|---|---|---|---|---|---|
| IP-in-IP | 약 20B | 1500 − 20 = 1480 | 자체 암호화 없음, 필요 시 IPsec(ESP) 등 적용 | IPsec ESP 전형치 30~40B대(+NAT-T/패딩 가변) | 1500 − (20 + ~36) ≈ 1444 (프로파일별 상이) | 소프트웨어 암복호화 시 CPU 부하↑, NIC 오프로드 시 경감 |
| VXLAN | 약 50B (IPv6는 ~70B) | 1500 − 50 = 1450 | 자체 암호화 없음, 언더레이에 IPsec/WG 추가 가능 | WG 60B, IPsec ~36B 등 합산 | VXLAN+WG: 1500 − (50 + 60) = 1390 | UDP 캡슐화, VTEP/오프로드 유무에 성능 민감 |
| Geneve | 대략 44–58B(+옵션 가변) | 1500 − (44~58) ≈ 1456~1442 | 자체 암호화 없음, 언더레이 암호화 | IPsec ~36B 등 합산 | 예: 1500 − (58 + 36) ≈ 1406 | 옵션(TLV)로 가변 헤더 → MTU 마진 넉넉히 확보 권장 |

### 검증 체크리스트
- ping -M do -s N으로 DF 기반 PMTU 탐색, 경로별 대형 페이로드 송신 테스트(gRPC/HTTP2 등)
- 특정 경로만 타임아웃/리트랜스 발생 시 MTU/DF/ICMP Block 여부 점검

## 예시 계산(언더레이 MTU 1500, IPv4)
- IPIP 단독: 1500 − 20 = 1480  
- VXLAN 단독: 1500 − 50 = 1450  
- Geneve(옵션 14B 가정, 총 58B): 1500 − 58 = 1442  
- VXLAN + WireGuard: 1500 − (50 + 60) = 1390  
- IPIP + IPsec(ESP ~36B): 1500 − (20 + 36) ≈ 1444

### 참고
- MTU 계산 원칙: 유효 MTU = 언더레이 MTU − (캡슐화/암호화 헤더 오버헤드 합). 일반적으로 IPv4 기준 대략 IP-in-IP 20B, VXLAN 50B, Geneve 44–58B(옵션에 따라 가변)로 본다
- 암호화 적용 시: VXLAN/Geneve/IPIP에 암호화를 더할 경우 IPsec(ESP) 등 추가 오버헤드가 더해져 MTU를 더 낮춰야 한다
- IPv6는 기본 헤더가 더 커서 동일 캡슐화에서도 오버헤드가 증가(일반적으로 +20B)한다
- 중첩 터널(예: VXLAN 위 WireGuard)을 쓰면 오버헤드를 합산한다. 예: 1500 언더레이에서 VXLAN(50)+WG(60)=110 → 권장 MTU ≈ 1390
- VXLAN 오버헤드(IPv4) ~50B, IPv6 ~70B
- Geneve 헤더는 옵션에 따라 가변(안정적 MTU를 위해 보수적으로 산정)
- IPsec ESP 오버헤드는 암호화/인증 알고리즘, NAT-T, 패딩에 따라 변동. 실무에서는 1400 근처 권장값을 사용하는 사례가 많음

<!-- more -->
