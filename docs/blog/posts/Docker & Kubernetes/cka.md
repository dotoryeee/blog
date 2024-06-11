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


2. securityContext는 pod레벨과 container레벨 모두 적용 가능(스코프가 작은 container레벨의 context UID가 우선순위에 있다)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-pod
spec:
  securityContext:
    runAsUser: 1001
  containers:
  -  image: ubuntu #1002
     name: web
     command: ["sleep", "5000"]
     securityContext:
      runAsUser: 1002
  -  image: busybox #1001
     name: ubuntu
     command: ["sleep", "5000"]
  -  image: busybox #1001+NET_ADMIN+SYS_TIME
     name: buxybox
     command: ["sleep", "5000"]
     securityContext:
      capabilities:
        add: ["NET_ADMIN", "SYS_TIME"]
```

3. netpol 예시
```yaml
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: netpol-example
  namespace: default
spec:
  podSelector:
    matchLabels:
      name: source-pod-name
  policyTypes:
  - Egress
  - Ingress
  ingress:
    - {}
  egress:
  - to:
    - podSelector:
        matchLabels:
          name: internal-db-pod
    ports:
    - protocol: TCP
      port: 3306
  - to:
    - podSelector:
        matchLabels:
          name: internal-was-pod
    ports:
    - protocol: TCP
      port: 8080
  - ports:
    - port: 53
      protocol: UDP #destination을 정하지 않았기 때문에 53포트는 아웃바운드 트래픽은 제한되지 않음
    - port: 53
      protocol: TCP
```

4. hostPath volume 마운트 example
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp
  namespace: default
spec:
  containers:
    image: busybox
    name: event-simulator
    volumeMounts:
    - mountPath: /log
      name: log-volume
  volumes:
  - name: log-volume
    hostPath:
      path: /var/log/webapp
      type: DirectoryOrCreate
```

5. PVC/PV example
```yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: claim-log-1
spec:
  accessModes:
    - ReadWriteMany #PV와 동일해야 함
  volumeMode: Filesystem
  resources:
    requests:
      storage: 50Mi
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-log
spec:
  storageClassName: manual
  capacity:
    storage: 100Mi
  persistentVolumeReclaimPolicy: Retain
  accessModes:
    - ReadWriteMany #PVC와 동일해야 함
  hostPath:
    path: "/pv/log"

---
#Pod에서
  volumes:
  - name: log-volume
    persistentVolumeClaim:
        claimName: claim-log-1
```

6. Kubernetes Cluster 업그레이드 순서
    1. controlplane노드 kubeadm 업그레이드(apt, yum)
    2. controlplane노드 kubeadm apply upgrade
    3. controlplane노드 kubelet 업그레이드
    4. worker노트 kubeadm 업그레이드
    5. worker노드 kubeadm apply upgrade
    6. worker노드 kubelet 업그레이드

7. 