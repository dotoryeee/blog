# Kibana load error

## 증상
- Error message<br>
  **Elastic Kibana did not load properly. Check the server output for more information**
- 인프라 구성
    Kibana 접근을 위해 Nginx를 reverse proxy로 사용하는 구조

## tl;dr
상세 내역을 기재하기 전 해결 방안부터 적겠습니다. Nginx 설정파일에서 proxy_buffer 부분을 수정합니다

- AS-IS
    ```s
    proxy_buffer_size 128k;
	proxy_buffers 4 256k;
	proxy_busy_buffers_size 256k;
    ```
- TO-BE
    ```s
    proxy_buffer_size 128k;
	proxy_buffers 8 1024k;
	proxy_busy_buffers_size 1024k;
    ```

## 원인

