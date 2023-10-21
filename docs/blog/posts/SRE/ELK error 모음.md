---
draft: false
date: 1993-09-17
authors:
  - dotoryeee
categories:
  - ElasticSearch
---
# ELK error 모음

## 1
### 증상
- Error message<br>
  **Elastic Kibana did not load properly. Check the server output for more information**
- 인프라 구성
    Kibana 접근을 위해 Nginx를 reverse proxy로 사용하는 구조

### 해결방법
Nginx 설정파일에서 proxy_buffer 부분을 수정합니다

- AS-IS
    ```s
    proxy_buffer_size 128k;
	proxy_buffers 4 256k; (AWS에서 제공하는 ES-Proxy용 nginx 템플릿 기본값)
	proxy_busy_buffers_size 256k;
    ```
- TO-BE
    ```s
    proxy_buffer_size 128k;
	proxy_buffers 8 1024k;
	proxy_busy_buffers_size 1024k;
    ```
<!-- more -->
## 2
### 증상
- Filebeat가 삭제된 로그 파일을 계속 핸들링하고있어 시스템에서 로그가 삭제되었지만 (ls 명령어 사용지 파일이 삭제되어 보이지 않는 상태) lsof 명령으로 확인했을 때 filebeat에서 계속 파일을 물고있어 시스템 용량 확보가 불가능함

### 해결방법
filebeat의 버그로 6.8.4 / 7.4.1 이후로 업그레이드 해야합니다

### 원인
filebeat에서 close_timeout이 기본적으로 5minutes인데, 5분이 지나도 파일이 닫히지 않아 검색해보니 github issue로 등록된 것을 확인했습니다 [issue #13907](http://github.com/elastic/beats/pulls?q=13907)<br>
해당 버그에 대응하는 filebeat 버전은 [6.8.4](https://www.elastic.co/guide/en/beats/libbeat/6.8/release-notes-6.8.4.html#_bugfixes_11) 또는 [7.4.1](https://www.elastic.co/guide/en/beats/libbeat/7.17/release-notes-7.4.1.html0) 입니다.