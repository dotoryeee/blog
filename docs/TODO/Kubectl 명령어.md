# Kubectl 명령어 메모

!!! warning
    테스트 및 확인 추가 필요

1. kubernetes cluster event 생성 시간 순서로 정렬하여 호출
    ```s
    kubectl get events --sort-by=.metadata.creationTimestamp
    ```

2. 