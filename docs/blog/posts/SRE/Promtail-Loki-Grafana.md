---
draft: true
date: 2021-05-01
authors:
  - dotoryeee
categories:
  - SRE
  - Promtail
  - Loki
  - Grafana
---
# Promtail-Loki-Grafana

1. install promtail
    ```bash
    #!/bin/bash

    # Install Promtail
    curl -LO https://github.com/grafana/loki/releases/download/v2.3.0/promtail-linux-amd64.zip
    sudo apt-get update && sudo apt-get install -y unzip
    unzip promtail-linux-amd64.zip
    sudo mv promtail-linux-amd64 /usr/local/bin/promtail
    sudo chmod a+x /usr/local/bin/promtail

    # Create a Promtail user
    sudo useradd --no-create-home --shell /usr/sbin/nologin promtail

    # Create a configuration directory for Promtail
    sudo mkdir -p /etc/promtail

    # Change ownership of the configuration directory to Promtail user
    sudo chown promtail:promtail /etc/promtail
    ```
<!-- more -->
2. promtail 설정
    ```s title="/etc/promtail/promtail.yml"
    #!/bin/bash

    cat <<EOF | sudo tee /etc/promtail/promtail.yml
    server:
    http_listen_port: 9080
    grpc_listen_port: 0

    positions:
    filename: /tmp/positions.yaml

    clients:
    - url: http://LOKI_HOST:LOKI_PORT/loki/api/v1/push

    scrape_configs:
    - job_name: system
    static_configs:
    - targets:
        - localhost
        labels:
        job: varlogs
        __path__: /var/log/**log
    EOF

    sudo chown promtail:promtail /etc/promtail/promtail.yml
    ```

    ```s
    sudo systemctl restart promtail
    ```

3. S3에 데이터 저장을 위한 Loki config 생성
    ```yaml title="loki-config/config.yaml"
    auth_enabled: false # Loki자체 인증 사용 여부

    server:
        http_listen_port: 3100

    ingester: #Loki 인제스터 구성(로그 업로드, 라벨링, 저장)
        lifecycler: # 인제스터에서 사용되는 수명주기 관리자
            address: 0.0.0.0 #address는 인제스터 수명주기 관리자의 IP 주소
            ring: 
                kvstore:
                  store: inmemory
                replication_factor: 2
            final_sleep: 0s # chunk_retain_period가 10m으로 설정하고 final_sleep을 5m으로 설정하면 chunk는 15분만 유지됌
        chunk_idle_period: 5m #데이터 청크가 저장되어 있는 상태로 유지되는 최대 기간
        chunk_retain_period: 10m #데이터 청크가 유지되는 기간. chunk_idle_period가 chunk_retain_period보다 작은 경우 chunk가 적절한 시간 내에 compacting이나 ingesting이 되지 않을 수 있으므로 데이터 손실이 발생할 수 있다. chunk_idle_period >= chunk_retain_period
        max_transfer_retries: 0 #데이터 전송에 실패한 경우 재시도 횟수
        trace:
            store: inmemory # 인제스터에서 발생한 추적 데이터를 저장하는 곳
        wal:
            enabled: true
            compressions: none # none, snappy, gzip, lz4 
            flush_after: 512mb # WAL 파일이 일정 크기가 될 때마다 디스크로 플러시
            encoding: snappy
            segment_size: 512mb

    schema_config:
        configs:
            - from: 2023-04-19 #스키마 설정이 적용되는 시작 날짜
            store: aws
            object_store: s3
            schema: v11
            index:
                prefix: loki_index_
                period: 24h

    storage_config:
        aws:
            s3: 
            access_key_id: ${AWS_ACCESS_KEY_ID}
            secret_access_key: ${AWS_SECRET_ACCESS_KEY}
            bucketnames:
            - <bucket-name>
            region: ap-northeast-2
            s3forcepathstyle: true
            max_concurrent_requests: 100
            s3partsize: 128MB
            s3maxmultipartcopy: 10000

    compactor: #컴팩터는 오래된 로그를 압축
        working_directory: /tmp/loki/compactor
        shared_store: aws
        compaction:
            schedule: '0 * * * *'
            retention_enabled: true
            retention: 48h

    limits_config:
        ingestion_rate_mb: 5
        ingestion_burst_size_mb: 10
        staleness_delta: 1m

    chunk_store_config:
        max_look_back_period: 0s

    table_manager:
        retention_deletes_enabled: false
        retention_period: 0s

    ruler: # Loki에서 Alertmanager와 통합하기 위한 설정
        alertmanagers:
        - static_configs:
            - targets: # Alertmanager 서버의 엔드포인트
                - alertmanager:9093
        ring:
            kvstore: # Loki 인스턴스에서 Alertmanager와 연결할 때 사용하는 DB로 인메모리DB 사용
                store: inmemory # inmemory, consul, etcd
            replication_factor: 1
        enable_api: true
    ```

4. Deploy Loki and Grafana
    ```yaml title="docker-compose.yaml"
    version: "3.8"

    services:
    loki:
        image: grafana/loki:2.3.0
        command: -config.file=/etc/loki-config/config.yaml
        volumes:
        - ./loki-config:/etc/loki/
        ports:
        - "3100:3100"
        deploy:
        replicas: 2
        placement:
            constraints:
            - node.role == worker
        restart_policy:
            condition: any

    grafana:
        image: grafana/grafana:latest
        volumes:
        - grafana-data:/var/lib/grafana
        - ./grafana/provisioning:/etc/grafana/provisioning
        ports:
        - "3000:3000"
        depends_on:
        - loki
        deploy:
        placement:
            constraints:
            - node.role == manager # node.role이 manager인 노드에만 해당 서비스가 배포
        restart_policy:
            condition: any # any로 설정되어 있으므로 어떤 상황에서든 재시작을 시도

    volumes:
        grafana-data:
    ```

