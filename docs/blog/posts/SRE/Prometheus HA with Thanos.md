---
draft: true
date: 1993-09-17
authors:
  - dotoryeee
categories:
  - SRE
tags:
  - Prometheus
  - Thanos
  - HA
description: "docker-compose로 Prometheus 2대와 Thanos store·query·compact·receive를 올려 HA를 구성한 기록"
---
# Prometheus with Thanos
<!-- more -->
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

  thanos-store: # AWS S3에 저장된 과거 데이터 블록을 읽어 thanos-query에 제공합니다
    image: thanosio/thanos:v0.22.1
    container_name: thanos-store
    command:
      - "store"
      - "--data-dir=/tsdb"
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
      - "--objstore.config-file=/etc/thanos/storage.yaml"
      - "--http-address=0.0.0.0:10903"
      - "--wait" #컴팩션 완료 후 종료하지 않고 새 작업을 대기하는 boolean 플래그
      - "--wait-interval=2h" #wait-interval의 기본값은 5m이지만 일부 블록들이 충분히 생성되기 전에 컴팩션을 수행하게 될 수 있으므로 2h로 조정
    volumes:
      - ./thanos-data:/tsdb
      - ./storage.yaml:/etc/thanos/storage.yaml
    environment:
      - "AWS_ACCESS_KEY_ID=<aws-access-key>"
      - "AWS_SECRET_ACCESS_KEY=<aws-secret-key>"
      - "AWS_REGION=<aws-region>"
    ports:
      - "10903:10903"
    networks:
      - thanos

  thanos-receive: #Prometheus의 remote_write로 메트릭을 수집하여 AWS S3에 업로드합니다
    image: thanosio/thanos:v0.22.1
    container_name: thanos-receive
    command:
      - "receive"
      - "--tsdb.path=/tsdb"
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

!!! notice

    💡 위 구성은 Prometheus에 Sidecar가 없어 실시간 데이터 조회와 S3 업로드 주체가 빠져 있으므로 각 Prometheus에 Sidecar를 붙이거나 remote_write로 receive에 전송하고 thanos-query에 sidecar/receive endpoint를 등록해야 HA 쿼리가 성립합니다
