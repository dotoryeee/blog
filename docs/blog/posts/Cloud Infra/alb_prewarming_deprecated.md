---
draft: false
date: 2025-03-19
authors:
  - dotoryeee
categories:
  - Cloud
description: "2025년 종료되는 ALB Pre-Warming을 대체하는 LCU-R 예약 방식과 값 추산법, 두 방식의 비용·설정 차이를 표로 비교"
---
# AWS ALB Pre-Warming 지원 종료

<!-- more -->

## 요약
AWS는 2025년 4월 30일부로 ALB Pre-Warming 요청을 더 이상 지원하지 않으며, 기존에 설정된 Pre-Warming은 2025년 6월 30일까지만 유지

## 대안
1. Pre-Warming을 대체하는 새로운 방식으로 LCU-R 사용(2024.11 출시)
2. LCU-R은 사용자가 직접 ALB 용량을 예약할 수 있는 셀프 서비스
3. LCU-R은 ALB뿐만 아니라 Network Load Balancer(NLB)에서도 사용 가능
4. 별도 기간 제한 없이 종료·취소 시까지 유지되며 감축은 하루 2회로 제한

## LCU-R 값 추산 가이드
1. Pre-Warming 요청한 이력이 있다면 AWS Support에 문의하여 과거에 적용된 설정 값 확인 가능
2. CloudWatch의 LCU 메트릭(PeakLCUs)을 활용하여 ALB의 최대 트래픽 대응에 필요한 LCU 추정
3. Max(PeakLCUs) * (samplecount / PERIOD(metric) * 60)

출처: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/capacity-unit-reservation.html

## 비교표
| 특성 | ALB Pre-Warming | LCU-R(Load Balancer Capacity Unit Reservation) |
|------|----------------|----------------------------------------------|
| 요청 방식 | AWS Support 티켓 제출 | 셀프 서비스(콘솔, CLI, SDK) |
| 설정 주체 | AWS 지원팀 | 고객 직접 설정 |
| 최소 요청 기간 | 일반적으로 며칠 전 | 수 분 내 반영(최대 수 시간) |
| 최대 유지 기간 | 케이스별 상이 | 제한 없음(취소 시까지 유지) |
| 비용 청구 방식 | 별도 비용 없음 | 예약한 LCU 수에 따라 비용 청구 |
| 용량 단위 | 대략적인 트래픽 예상치 | 정확한 LCU 수치 |
| 최소 예약 단위 | 명시적 제한 없음 | 최소 100 LCU |
| 최대 예약 단위 | 명시적 제한 없음 | 기본 1,500 LCU (조정 가능) |
| 계정 한도 | 명시적 제한 없음 | 리전별 12,000 LCU (조정 가능) |
| 투명성 | 내부 처리 과정 불투명 | 명확한 수치와 비용 |
| 모니터링 | 제한적 | CloudWatch 메트릭을 통한 상세 모니터링 |
| 종료 일정 | 2025년 4월 30일 요청 종료, 2025년 6월 30일 서비스 종료 | 현재 활성화 |