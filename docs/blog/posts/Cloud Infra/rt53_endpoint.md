---
draft: false
date: 2024-03-02
authors:
  - dotoryeee
categories:
  - AWS
  - Route53
---
# Route53 Endpoint for Private Hosted Zone

Route53 Private Hosted Zone(이하 PHZ) 생성 후 TGW로 연결된 타 VPC에서 쿼리 테스트 진행했습니다.<br>
온프레미스 또는 다른 클라우드에서 AWS Route53 PHZ의 DNS 쿼리를 사용하고자 할 때 동일한 구조로 이용 가능합니다.<br>
원래 Bind서버의 조건부 포워딩 정책에 Route53 PHZ 도메인을 부여해주는것이 주 목적이지만, 별도 DNS서버 없이 Route53 Inbound Endpoint가 DNS서버로써 동작할 수 있는지 테스트 하였습니다.

![](./rt53_endpoint/Screenshot%202024-03-02%20at%2009.56.49.png)

<!-- more -->
1. 현재 tgw-test.com을 ec2-03이 속한 우측 VPC에만 Route53 Private Hosted Zone으로 배포 후 www.tgw-test.com을 A record: 1.2.3.4로 설정한 상태.
    ![](./rt53_endpoint/Screenshot%202024-03-02%20at%2010.12.26.png)
2. ec2-02는 Public으로 배포된 제 3자의 www.tgw-test.com을 쿼리하는 모습
    ![](./rt53_endpoint/Screenshot%202024-03-02%20at%2010.16.40.png)
3. ec2-03는 Private으로 배포된 내 www.tgw-test.com을 쿼리하는 모습(1.2.3.4를 확인할 수 있다)
    ![](./rt53_endpoint/Screenshot%202024-03-02%20at%2010.17.39.png)
4. 우측 VPC Private Subnet에 Private Hosted Zone형태의 tgw-test.com도메인에 대한 Route53 Inbound Endpoint를 생성한다.
    ![](./rt53_endpoint/Screenshot%202024-03-02%20at%2010.18.45.png)
5. TGW생성 후 각 VPC에 Attachment 생성한 다음 TGW Route Table에 상호 VPC간 통신 가능하도록 라우팅이 잘 설정되었는지 확인한다.
    ![](./rt53_endpoint/Screenshot%202024-03-02%20at%2010.20.28.png)
6. ec2-02서버에서 타 VPC에 배포된 Route53 Inbound Endpoint에 53번 포트로 텔넷을 걸어 네트워크가 잘 통신되는것을 확인한다.
    ![](./rt53_endpoint/Screenshot%202024-03-02%20at%2010.23.20.png)
7. ec2-02서버의 /etc/resolv.conf를 수정해 바라볼 DNS 서버를 변경한다
    ![](./rt53_endpoint/Screenshot%202024-03-02%20at%2010.24.33.png)
8. 이제 다른 VPC의 Route53 Inbound endpoint를 메인 DNS로 이용해 www.tgw-test.com에 대한 레코드 값이 1.2.3.4로 표시되는 것을 확인할 수 있다
    ![](./rt53_endpoint/Screenshot%202024-03-02%20at%2010.24.56.png)