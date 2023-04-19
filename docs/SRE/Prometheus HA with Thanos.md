# Prometheus with Thanos

```yaml title="docker-compose.yaml"
version: "3.8"

services:
  prometheus1:
    image: prom/prometheus:v2.28.1
    container_name: prometheus1
    volumes:
      - ./prometheus1-data:/prometheus
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert.rules:/etc/prometheus/alert.rules
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--web.console.libraries=/etc/prometheus/console_libraries"
      - "--web.console.templates=/etc/prometheus/consoles"
      - "--web.enable-lifecycle" # /-/reload endpoint를 사용하기 위한 옵션
      - "--web.enable-admin-api" # /api/v1/admin endpoint를 사용하기 위한 옵션
    ports:
      - "9090:9090"
    networks:
      - thanos

  prometheus2:
    image: prom/prometheus:v2.28.1
    container_name: prometheus2
    volumes:
      - ./prometheus2-data:/prometheus
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert.rules:/etc/prometheus/alert.rules
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--web.console.libraries=/etc/prometheus/console_libraries"
      - "--web.console.templates=/etc/prometheus/consoles"
      - "--web.enable-lifecycle"
      - "--web.enable-admin-api"
    ports:
      - "9091:9090"
    networks:
      - thanos

  thanos-store: # Prometheus 인스턴스의 데이터를 수집하여 AWS S3에 저장합니다
    image: thanosio/thanos:v0.22.1
    container_name: thanos-store
    command:
      - "store"
      - "--tsdb.path=/tsdb"
      - "--objstore.config-file=/etc/thanos/storage.yaml"
      - "--grpc-address=0.0.0.0:10901"
    volumes:
      - ./thanos-data:/tsdb
      - ./storage.yaml:/etc/thanos/storage.yaml
    environment:
      - "AWS_ACCESS_KEY_ID=<aws-access-key>"
      - "AWS_SECRET_ACCESS_KEY=<aws-secret-key>"
      - "AWS_REGION=<aws-region>"
    ports:
      - "10901:10901"
    networks:
      - thanos

  thanos-query: #저장된 데이터를 쿼리하여 검색합니다
    image: thanosio/thanos:v0.22.1
    container_name: thanos-query
    command:
      - "query"
      - "--store=thanos-store:10901"
      - "--http-address=0.0.0.0:10902"
    volumes:
      - ./query-data:/query
    ports:
      - "10902:10902"
    networks:
      - thanos

  thanos-compact: #데이터를 압축하고 정리하여 저장소를 최적화합니다. thanos-compact는 Thanos에서의 데이터 보존을 위한 백그라운드 컴팩션을 수행합니다.
    image: thanosio/thanos:v0.22.1
    container_name: thanos-compact
    command:
      - "compact"
      - "--data-dir=/tsdb"
      - "--http-address=0.0.0.0:10903"
      - "--wait=2h" #wait 옵션의 기본값은 5m이지만 경우에도 일부 블록들이 충분히 생성되기 전에 컴팩션을 수행하게 될 수 있으므로 2h로 조정
    volumes:
      - ./thanos-data:/tsdb
    ports:
      - "10903:10903"
    networks:
      - thanos

  thanos-receive: #Prometheus 또는 다른 Thanos Receive 컨테이너에서 메트릭을 수집하고 Thanos Store로 전송합니다
    image: thanosio/thanos:v0.22.1
    container_name: thanos-receive
    command:
      - "receive"
      - "--tsdb.path=/tsdb"
      - "--objstore.bucket=<s3-bucket-name>"
      - "--objstore.config-file=/etc/thanos/storage.yaml"
    volumes:
      - ./thanos-data:/tsdb
      - ./storage.yaml:/etc/thanos/storage.yaml
    environment:
      - "AWS_ACCESS_KEY_ID=<aws-access-key>"
      - "AWS_SECRET_ACCESS_KEY=<aws-secret-key>"
      - "AWS_REGION=<aws-region>"
    ports:
      - "19291:19291"
    networks:
      - thanos

```
