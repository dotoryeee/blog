# KQL 모음 for kibana

1. 다중 필드로 로그 필터링:
    ```s
    app: "my-app" AND environment: "production"
    ```
2. 필드의 값이 특정 범위에 있는 로그 필터링:
    ```s
    app: "my-app" AND response_code >= 400 AND response_code <= 499
    ```
3. 여러 문자열을 포함하는 로그 필터링:
    ```s
    app: "my-app" AND (message: "error" OR message: "timeout" OR message: "warning")
    ```
4. 필드의 값이 특정 리스트에 포함되는 로그 필터링:
    ```s
    app: "my-app" AND method.keyword in ("GET", "POST", "PUT")
    ```
5. 문자열이 포함되지 않은 로그 필터링:
    ```s
    app: "my-app" AND NOT message: "debug"
    ```
6. 날짜 범위를 기반으로 로그 필터링:
    ```s
    app: "my-app" AND @timestamp >= "now-7d/d" AND @timestamp < "now/d"
    ```
7. 특정 레이블과 필드 값을 기반으로 로그 필터링:
    ```s
    app: "my-app" AND environment: "production" AND response_time_ms > 1000
    ```
8. 정규 표현식을 사용하여 로그 필터링:
    ```s
    app: "my-app" AND message: /error|timeout|warning/
    ```
9. 사용자 정의 스크립트를 사용하여 로그 필터링:
    ```s
    app: "my-app" AND doc['duration_seconds'].value + doc['network_latency_seconds'].value > 5
    ```
10. 필드의 값이 존재하는 로그만 필터링:
    ```s
    app: "my-app" AND _exists_:user_agent
    ```
11. 날짜 범위와 여러 조건을 결합하여 로그 필터링:
    ```s
    app: "my-app" AND environment: "production" AND (message: "error" OR message: "warning") AND @timestamp > "now-1h"
    ```
12. 문자열 검색과 범위 조건을 결합하여 로그 필터링:
    ```s
    app: "my-app" AND message: "error" AND (response_code >= 500 AND response_code <= 599) AND response_time_ms > 2000
    ```
13. 여러 필드의 값이 특정 리스트에 포함되는 로그 필터링:
    ```s
    app: "my-app" AND (status.keyword in ("running", "pending") OR method.keyword in ("GET", "POST", "PUT"))
    ```
14. 여러 문자열을 포함하고 특정 필드 값에 기반한 로그 필터링:
    ```s
    app: "my-app" AND (message: "error" OR message: "warning" OR message: "timeout") AND response_time_ms > 500
    ```
15. 날짜 범위를 사용하여 특정 문자열을 포함하는 로그 라인의 비율을 계산:
    ```s
    app: "my-app" AND message: "error" AND @timestamp > "now-1d/d" AND @timestamp < "now/d"
    ```
16. 사용자 정의 스크립트를 사용하여 여러 필드의 값의 합이 특정 임계값을 초과하는 로그 필터링:
    ```s
    app: "my-app" AND script('params.duration_seconds + params.network_latency_seconds > 5', params: ['duration_seconds': doc['duration_seconds'].value, 'network_latency_seconds': doc['network_latency_seconds'].value])
    ```
17. 정규 표현식을 사용하여 여러 필드의 값을 기반으로 로그 필터링:
    ```s
    app: "my-app" AND message: /(GET|POST|PUT) .* (error|warning)/
    ```
18. 특정 필드의 값을 기반으로 여러 레이블의 로그 필터링:
    ```s
    app: "my-app" AND environment: "production" AND response_time_ms: (>=1000 AND <=2000)
    ```
