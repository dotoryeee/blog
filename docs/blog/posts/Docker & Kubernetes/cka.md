---
draft: true
date: 2024-06-10
authors:
  - dotoryeee
categories:
  - study
  - kubernetes
  - cka
---
# CKA 시험 요약

## 시험 명령어 요약

<!-- more -->

1. ETCD 백업/복구
    - 백업

    각 파라미터에 필요한 값(etcd엔드포인트, 인증서 위치)는 `kubectl -n kube-system describe po etcd-controlplane` 명령에서 찾는다.
    ```sh
    ETCDCTL_API=3 etcdctl \
    --endpoints localhost:2379  \
    --cert=/etc/kubernetes/pki/etcd/server.crt  \
    --key=/etc/kubernetes/pki/etcd/server.key  \
    --cacert=/etc/kubernetes/pki/etcd/ca.crt \
    snapshot save /opt/etcd-snapshot.db
    ```

    - 복구
    기존 etcd데이터와 충돌을 방지하고 복구 테스트를 진행하기 위해 `--data-dir`파라미터를 부여한다
    !!! info ""
        etcd v3.6부터 etcdctl을 이용한 복구는 deprecate된다 -> etcdutl사용
    ```sh
    ETCDCTL_API=3 etcdctl --data-dir /var/somewhere/etcd-from-backup snapshot restore /opt/etcd-snapshot.db
    ```
    static pod로 실행중인 etcd pod를 수정한다
    ```sh
    $ cat /var/lib/kubelet/config.yaml | grep static
    staticPodPath: /etc/kubernetes/manifests
    $ vi /etc/kubernetes/manifests/etcd.yaml
    기존 79행을 80행처럼 변경
    78   - hostPath:
    79       #path: /var/lib/etcd
    80       path: /var/somewhere/etcd-from-backup
    81       type: DirectoryOrCreate
    1~2분 후 etcd pod의 재생성이 완료되면 아래와 같이 etcd-data 디렉터리가 변경된 것을 확인할 수 있다
    $ k -n kube-system describe po etcd-controlplane | grep somewhere -C3
        HostPathType:  DirectoryOrCreate
    etcd-data:
        Type:          HostPath (bare host directory volume)
        Path:          /var/somewhere/etcd-from-backup
        HostPathType:  DirectoryOrCreate
    QoS Class:         Burstable
    Node-Selectors:    <none>

    ```


    참고: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/


2. K8S Cluster Upgrade


3. static POD 관리


4. drain, cordon, uncordon
