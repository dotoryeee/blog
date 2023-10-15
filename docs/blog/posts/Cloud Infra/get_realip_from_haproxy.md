---
draft: true
date: 2021-05-01
authors:
  - dotoryeee
categories:
  - NHNcloud
  - LoadBalancer
---
# Layer7 LB 사용시 real IP 가져오기

1. Load balancer에서 HTTP protocol기반 routing을 사용하면 기본적으로 Client IP를 확인할 수 없다.
2. 현재 생성된 Load balancer의 Private IP가 10.0.1.48이다
    ![image1](./get_realip_from_haproxy/Screenshot%202023-05-27%20at%2010.06.26%20PM.png)
3. Client web browser -> Load Balancer -> Nginx instance로 접속하면 nginx의 access log에 client의 IP가 아닌 Load balancer의 IP가 기록된다
    ![image2](./get_realip_from_haproxy/Screenshot%202023-05-27%20at%2010.11.07%20PM.png)
<!-- more -->
4. X-Forwarded-For 헤더의 값을 로깅하도록 설정한다
    ```s
    set_real_ip_from 10.0.0.0/8;
    real_ip_header X-Forwarded-For;

    log_format main '$http_x_forwarded_for  – $remote_user [$time_local]'
        '”$request” $status $body_bytes_sent “$http_referer”'
        '”$http_user_agent”';
    ```
    ![image3](./get_realip_from_haproxy/Screenshot%202023-05-27%20at%2010.11.53%20PM.png)
5. Nginx access log에 client의 IP가 잘 저장된다
    ![image4](./get_realip_from_haproxy/Screenshot%202023-05-27%20at%2010.10.45%20PM.png)
6. 그 외에 nginx에서 conf업데이트 시 sudo systemctl restart nginx 사용하지 말고, nginx -s reload옵션을 이용하자. conf 문법에 오류가 있을경우 conf를 적용하지 않아 nginx가 종료되지 않는다. conf에 문법 오류가 있을 때 sudo systemctl restart nginx를 사용하면 nginx가 종료되어버린다.