---
draft: true
date: 1993-09-17
authors:
  - dotoryeee
categories:
  - SRE
  - Grafana
  - Loki
---
# LogQL 모음 for Loki

!!! warning
    테스트 및 확인 추가 필요

1. 단일 레이블로 로그 검색:
    ```s
    {app="my-app"}
    ```
2. 여러 레이블로 로그 검색:
    ```s
    {app="my-app", environment="production"}
    ```
<!-- more -->
3. 문자열이 포함된 로그 검색:
    ```s
    {app="my-app"} |~ "error"
    ```
4. 문자열이 제외된 로그 검색:
    ```s
    {app="my-app"} !~ "debug"
    ```
5. 로그 메시지에서 특정 키워드를 포함하는 경우 카운트:
    ```s
    count_over_time({app="my-app"} |~ "error" [5m])
    ```
6. 로그에서 추출한 메트릭 사용하기:
    ```s
    {app="my-app"} | json | duration > 5
    ```
7. 인스턴스별 로그 메시지 에러 비율 계산:
    ```s
    sum(rate({app="my-app"} |~ "error" [5m])) by (instance)
    ```
8. 레이블별로 에러 카운트:
    ```s
    sum(count_over_time({app="my-app"} |~ "error" [1h])) by (job)
    ```
9. 시간 범위를 지정하여 로그 검색:
    ```s
    {app="my-app"} |~ "error" | logfmt | latency > 300ms and latency < 500ms
    ```
10. logfmt 파서를 사용하여 로그에서 메트릭 추출:
    ```s
    {app="my-app"} | logfmt | status=500
    ```
11. JSON 파서를 사용하여 로그에서 메트릭 추출:
    ```s
    {app="my-app"} | json | level="error" | latency > 250
    ```
12. 문자열과 여러 조건을 사용하여 로그 필터링:
    ```s
    {app="my-app"} |~ "error" |~ "timeout" |~ "network"
    ```
13. 파이프를 사용하여 로그 필터링 및 메트릭 추출:
    ```s
    {app="my-app"} |~ "error" | latency > 200ms
    ```
14. 파서와 조건을 결합하여 로그 필터링:
    ```s
    {app="my-app"} | json | method="POST" | response_code >= 400
    ```
15. 시간 범위에 대한 에러 로그 카운트 비율:
    ```s
    sum(rate({app="my-app"} |~ "error" [10m])) / sum(rate({app="my-app"} [10m]))
    ```
16. 로그 라인의 길이가 일정 길이를 초과하는 경우 필터링:
    ```s
    {app="my-app"} | length > 1000
    ```
17. 로그 필드에 기반한 값 분포를 측정하는 히스토그램 생성:
    ```s
    histogram_quantile(0.9, sum by (le) (rate({app="my-app"} | json | histogram_duration_seconds_bucket [5m])))
    ```
18. 사용자 정의 파서를 사용하여 로그 메시지를 구문 분석하고 필터링:
    ```s
    {app="my-app"} | pattern "level: %{LOGLEVEL:level} msg: %{GREEDYDATA:msg}" | level="error"
    ```
19. 로그에서 추출된 메트릭을 기반으로 시간 범위에 대한 평균 계산:
    ```s
    avg(rate({app="my-app"} | json | duration_seconds [5m]))
    ```
20. 로그에서 추출한 메트릭을 기반으로 시간 범위에 대한 최대값 계산:
    ```s
    max(rate({app="my-app"} | json | duration_seconds [5m]))
    ```
21. 로그의 에러 및 워닝 메시지를 포함하는 요청 비율 계산:
    ```s
    (sum(rate({app="my-app"} |~ "(error|warning)" [5m])) by (instance)) / (sum(rate({app="my-app"} [5m])) by (instance))
    ```
22. JSON 파서를 사용하여 로그 필드를 기반으로 시간 범위에 대한 평균, 최소 및 최대값 계산:
    ```s
    avg(rate({app="my-app"} | json | duration_seconds [5m])), min(rate({app="my-app"} | json | duration_seconds [5m])), max(rat```e({app="my-app"} | json | duration_seconds [5m]))
    ```
23. 두 개의 로그 필드를 조합하여 시간 범위에 대한 평균 계산:
    ```s
    avg(rate({app="my-app"} | logfmt | total_duration_seconds = duration_seconds + network_latency_seconds [5m]))
    ```
24. 로그에서 특정 키워드를 포함하는 라인의 비율을 계산하고, 특정 태그를 기준으로 그룹화:
    ```s
    sum(rate({app="my-app"} |~ "error" [5m])) by (tag) / sum(rate({app="my-app"} [5m])) by (tag)
    ```
25. 로그 라인의 요청 수와 요청 크기의 합계를 계산하여, 시간 범위에 대한 평균 요청 크기를 계산:
    ```s
    sum(rate({app="my-app"} | json | bytes [5m])) / sum(rate({app="my-app"} [5m]))
    ```
26. 로그 라인에서 사용자 정의 정규식을 사용하여 클라이언트 IP 주소 추출 및 해당 IP 주소별 에러 카운트 계산:
    ```s
    count_over_time({app="my-app"} | pattern "client_ip: %{IPV4:client_ip} .* (error|warning)" [5m]) by (client_ip)
    ```
27. 로그에서 특정 레이블과 필드 값을 기반으로 요청 비율을 계산하고 이를 기반으로 90번째 백분위수 계산:
    ```s
    histogram_quantile(0.9, sum by (le) (rate({app="my-app", environment="production"} | json | response_time_bucket [5m])))
    ```
