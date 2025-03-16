---
draft: false
date: 2025-03-16
authors:
  - dotoryeee
categories:
  - Cloud
hide:
  - toc
---
#  AWS 보안 서비스 요약

<!-- more -->


| <div style="width:8em">특성| <div style="width:20em">VPC Security Group| <div style="width:20em">Subnet NACL| <div style="width:20em">AWS Network Firewall| <div style="width:20em">AWS Firewall Manager| <div style="width:20em">AWS WAF| <div style="width:20em">AWS Shield|
|---|------------------|-----------|---------------------|-------------------|--------|----------|
|보호 레벨|인스턴스/리소스 레벨에서 작동하며 개별 EC2, RDS, Lambda 등 VPC 내 리소스에 직접 연결됨. 2024년 10월부터 여러 VPC에서도 사용 가능|서브넷 경계에서 작동하며 해당 서브넷으로 들어오고 나가는 모든 트래픽을 제어|VPC 레벨에서 작동하며 전체 VPC의 네트워크 트래픽을 검사 및 필터링하는 완전 관리형 서비스|다중 계정 및 리소스에 걸쳐 여러 보안 서비스를 중앙에서 관리하는 상위 레벨 서비스|CloudFront, ALB, API Gateway 등에 연결되어 웹 애플리케이션 트래픽을 보호하는 클라우드 네이티브 방화벽|인프라 레벨에서 DDoS 공격으로부터 AWS 리소스를 보호하는 관리형 서비스|
|상태 유지|상태 유지(Stateful) 방식으로 작동하여 허용된 인바운드 트래픽의 응답은 규칙과 상관없이 자동으로 허용됨|상태 비유지(Stateless) 방식으로 작동하여 인바운드와 아웃바운드 트래픽을 각각 별도로 평가하고 규칙 설정 필요|상태 유지 및 비유지 규칙을 모두 지원하며 트래픽 흐름 상태를 추적하거나 개별 패킷 기반 필터링 가능|직접적인 상태 유지 기능은 없으며 관리하는 각 서비스의 상태 유지 특성을 활용|웹 요청 및 응답의 상태를 추적하여 상태 유지 방식으로 작동|네트워크 흐름을 분석하여 상태 유지 방식으로 DDoS 공격 패턴 탐지 및 방어|
|주요 보호 대상|EC2 인스턴스, RDS 데이터베이스, Lambda 함수, ElastiCache, Redshift 등 VPC 내 모든 리소스. 이제 여러 VPC와 참여자 계정 간에도 공유 가능|서브넷 내의 모든 리소스에 대한 트래픽을 필터링하며 서브넷 경계의 첫 번째 방어선 역할|VPC 전체의 트래픽을 보호하며 특히 인터넷 게이트웨이, NAT 게이트웨이 등을 통과하는 트래픽 검사|AWS Organizations 내 여러 계정의 리소스와 다양한 보안 서비스를 통합 관리|CloudFront, Application Load Balancer, API Gateway, AppSync를 통한 웹 애플리케이션 트래픽|CloudFront, Route 53, Global Accelerator, Elastic IP 등 AWS 리소스에 대한 DDoS 공격|
|검사 수준|L3/L4(IP 주소, 포트, 프로토콜) 수준에서 트래픽 필터링, 애플리케이션 계층 검사 불가|L3/L4(IP 주소, 포트, 프로토콜) 수준에서 트래픽 필터링, 패킷 헤더만 검사|L3-L7 심층 패킷 검사 지원, 패킷 헤더뿐만 아니라 페이로드 내용까지 검사 가능|직접 검사하지 않고 관리하는 각 서비스의 검사 기능을 활용|L7(HTTP/HTTPS) 웹 트래픽 검사, 요청 헤더, 쿠키, URI, 쿼리 문자열 등 검사|L3/L4 네트워크/전송 계층(Standard), L7 애플리케이션 계층까지(Advanced) 보호|
|주요 기능|인스턴스 간 트래픽 제어, 소스/대상 IP 및 포트 기반 액세스 제어, 다른 보안 그룹 참조 가능. 이제 VPC 간 보안 그룹 공유 가능|서브넷 수준의 방화벽, 명시적 허용/거부 규칙, 임시 포트 범위 제어, 악성 IP 차단|상태 기반 필터링, 도메인 이름 필터링, 침입 방지, 프로토콜 분석, Suricata 호환 규칙. 자동 규칙 업데이트 및 트래픽 모니터링|중앙 집중식 정책 관리, 규정 준수 모니터링, 자동 교정, 다중 계정 보안 정책 적용, 계층적 보호 정책|SQL 인젝션/XSS 방어, 봇 제어, 속도 제한, 지역 차단, IP 평판 필터링, 커스텀/관리형 규칙|네트워크 흐름 모니터링, 자동 DDoS 완화, 트래픽 엔지니어링, 24/7 모니터링, 전용 DDoS 대응팀(Advanced)|
|규칙 유형|허용 규칙만 지원(명시적 거부 불가), 기본적으로 모든 트래픽 거부, 참조 기반 규칙 지원|허용 및 거부 규칙 모두 지원, 숫자 기반 우선순위(1-32766), 낮은 번호부터 평가, 기본적으로 모든 트래픽 거부|상태 유지/비유지 규칙, Suricata 호환 IPS/IDS 규칙, 도메인 필터링 규칙, 정규식 패턴 매칭|정책 기반 규칙, 자동 교정 규칙, 규정 준수 규칙, 리소스 태그 기반 정책|관리형 규칙 그룹(OWASP Top 10, 봇 제어 등), 속도 기반 규칙, IP 세트 기반 규칙, 지역 차단 규칙|정적 임계값 기반 규칙(Standard), 동적 임계값 및 커스텀 완화 규칙(Advanced)|
|비용|완전 무료로 제공, 추가 비용 없음|완전 무료로 제공, 추가 비용 없음|시간당 배포 비용 + 처리된 데이터 양에 따른 비용|정책당 월별 요금 + 관리하는 리소스 수에 따른 비용|규칙 수 + 검사된 웹 요청 수에 따른 비용|Standard는 무료, Advanced는 월별 구독 요금 + 데이터 전송량에 따른 비용|
|관리 복잡성|낮음 - 간단한 인바운드/아웃바운드 규칙 설정, AWS 콘솔, CLI, API를 통한 쉬운 관리|중간 - 규칙 번호와 우선순위 관리 필요, 인바운드/아웃바운드 규칙 별도 설정|높음 - 복잡한 규칙 세트 관리, Suricata 규칙 이해 필요, 네트워크 토폴로지 고려|중간 - 다중 계정 관리는 복잡하나 중앙 집중식 인터페이스로 단순화|중간 - 웹 공격 패턴 이해 필요, 다양한 규칙 유형 관리, 오탐 처리|낮음(Standard), 높음(Advanced) - 고급 기능 구성 및 DDoS 대응 계획 수립 필요|
|통합 서비스|EC2, RDS, Lambda, ElastiCache, Redshift, EFS, ELB 등 대부분의 VPC 리소스와 통합|VPC 서브넷에만 연결되며 다른 서비스와 직접적인 통합 없음|VPC, Transit Gateway, Route Tables, CloudWatch, CloudTrail과 통합|AWS Organizations, Security Hub, WAF, Shield, Network Firewall, Security Groups 등과 통합|CloudFront, ALB, API Gateway, AppSync, CloudWatch, Kinesis Firehose와 통합|CloudFront, Route 53, Global Accelerator, ELB, EC2, AWS WAF와 통합|
|배포 위치|리소스에 직접 연결, 리전 서비스. 이제 여러 VPC에 연결 가능|서브넷에 자동 연결, 리전 서비스|VPC 내 특정 서브넷에 엔드포인트 배포, 리전 서비스|글로벌 서비스, 모든 리전의 리소스 관리 가능|글로벌 서비스(CloudFront) 또는 리전 서비스(ALB, API Gateway)|글로벌 서비스, 모든 리전의 리소스 보호|
|로깅 및 모니터링|기본 로깅 없음, VPC 흐름 로그와 함께 사용 가능|기본 로깅 없음, VPC 흐름 로그와 함께 사용 가능|CloudWatch Logs로 상세 트래픽 로깅, S3 버킷으로 내보내기 가능|Security Hub와 통합된 규정 준수 대시보드, CloudWatch 이벤트 지원|CloudWatch Logs, Kinesis Firehose를 통한 실시간 로깅, 상세 트래픽 분석|CloudWatch 지표, Shield Advanced는 상세 공격 가시성 및 보고서 제공|
|자동화 지원|AWS CloudFormation, Terraform, AWS CDK 등을 통한 자동화 지원|AWS CloudFormation, Terraform, AWS CDK 등을 통한 자동화 지원|AWS CloudFormation, API를 통한 자동화, 타사 SIEM 통합|자동 교정 기능, 새 리소스에 자동 정책 적용, API 통합|AWS CloudFormation, API를 통한 자동화, 타사 보안 도구 통합|자동 DDoS 탐지 및 완화, 사전 예방적 참여(Advanced)|

