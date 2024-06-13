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

7. 현재 노드에서 K8S Cluster통신에 사용하는 NIC 찾기
```sh
controlplane ~ ➜  k get no -o wide
NAME           STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION   CONTAINER-RUNTIME
controlplane   Ready    control-plane   18m   v1.29.0   192.1.220.9    <none>        Ubuntu 22.04.4 LTS   5.4.0-1106-gcp   containerd://1.6.26
node01         Ready    <none>          17m   v1.29.0   192.1.220.12   <none>        Ubuntu 22.04.3 LTS   5.4.0-1106-gcp   containerd://1.6.26

# cluster에 공개된 Private IP는 192.1.220.9

controlplane ~ ➜  ip a | grep 192.1.220.9 -C3
    link/ether 72:b5:ab:b3:a9:61 brd ff:ff:ff:ff:ff:ff link-netns cni-1201966d-c959-fdea-787f-c45a7e9a0804
15489: eth0@if15490: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 qdisc noqueue state UP group default 
    link/ether 02:42:c0:01:dc:09 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 192.1.220.9/24 brd 192.1.220.255 scope global eth0
       valid_lft forever preferred_lft forever
15491: eth1@if15492: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:ac:19:00:13 brd ff:ff:ff:ff:ff:ff link-netnsid 1

# ip a 명령어를 이용해 192.1.220.9는 eth0 NIC이 사용중인것을 확인할 수 있고 MAC Addr이 02:42:c0:01:dc:09인것도 확인할 수 있다.
```
8. 노드의 기본 게이트웨이 조회
```sh
ip route show default
```
9. node01의 pod들이 pod간 통신을 시도할 때 10.244.192.0으로 통신한다
```sh
node01 ~ ➜  ip route show 
default via 172.25.0.1 dev eth1 
10.244.0.0/16 dev weave proto kernel scope link src 10.244.192.0 
172.25.0.0/24 dev eth1 proto kernel scope link src 172.25.0.43 
192.41.231.0/24 dev eth0 proto kernel scope link src 192.41.231.3 
```
10. CoreDNS config 
```sh
controlplane ~ ➜  k -n kube-system describe cm coredns 
# ConfigMap으로 저장된 coredns config data호출
Name:         coredns
Namespace:    kube-system
Labels:       <none>
Annotations:  <none>

Data
====
Corefile:
----
.:53 {
# 53포트 listen
    errors
    # 쿼리 처리 중 에러를 로깅한다
    health {
       lameduck 5s
       # coreDNS 종료 요청 시 5초 지연시키고, 그동안 새로운 요청은 받지 않음
    }
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        # 클러스터 내부 DNS 도메인 설정(cluster.local, in-addr.arpa, ip6.arpa)
        # in-addr.arpa: IP v4 역방향 조회를 위한 도메인, 192.0.2.1쿼리시 옥텟 역순 배치 방식에 따라 1.2.0.192.in-addr.arpa응답
        # ip6.arpa: IP v6 역방향 조회를 위한 도메인
       pods insecure
       # 보안이 적용되지 않은 pod이름 기반 DNS 활성화
       fallthrough in-addr.arpa ip6.arpa
       # in-addr.arpa, ip6.arpa에 대한 쿼리 처리 실패 시 다음 플러그인으로 전달 -> forward . /etc/resolv.conf으로 전달됌
       ttl 30
    }
    prometheus :9153
    forward . /etc/resolv.conf {
       max_concurrent 1000
    }
    cache 30
    loop
    # DNS 쿼리 루프 방지
    reload
    # coredns config변경 시 자동 리로드
    loadbalance
}
```
11.  클러스터 내에서 default 네임스페이스의 test라는 Pod가 payroll 네임스페이스의 web-svc라는 service를 호출할 때 사용할 수 있는 도메인 종류 4가지
     - FQDN (Fully Qualified Domain Name): web-svc.payroll.svc.cluster.local
     - 단축 이름(Shortened name): web-svc
     - 네임스페이스를 포함한 단축 이름: web-svc.payroll
     - 서비스 도메인 (svc 포함): web-svc.payroll.svc
12. kubernetes v1.29 설치
    1. 시스템이 부팅될 때 br_netfilter 커널 모듈을 자동으로 로드하도록 설정(브릿지 네트워크용)
    ```sh
    cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
    br_netfilter
    EOF
    ```
    2. IPv4, IPv6 패킷이 브릿지를 통과할 떄 iptables를 거치도록 설정
    ```sh
    cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
    net.bridge.bridge-nf-call-ip6tables = 1
    net.bridge.bridge-nf-call-iptables = 1
    EOF
    # sysctl 설정 리로드
    sudo sysctl --system
    ```
    3. k8s repo 등록
    ```sh
    sudo apt install -y apt-transport-https ca-certificates curl

    # gpg keyring 디렉터리 생성
    sudo mkdir -p -m 755 /etc/apt/keyrings

    # 시스템에 gpg키 등록
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

    # pkgs.k8s.io repository 등록
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

    # 시스템 apt repo 업데이트
    sudo apt update
    ```
    4. kubectl, kubeadm, kubelet 설치
    ```sh
    apt install -y kubelet=1.29.0-1.1 kubeadm=1.29.0-1.1 kubectl=1.29.0-1.1
    sudo apt-mark hold kubelet kubeadm kubectl
    ```
13. Master node 설치
    1.  eth0의 ip를 api 서버 ip로 adversite 설정 + pod 네트워크를 10.244.0.0/16로 설정
    ```sh
    IP_ADDR=$(ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    kubeadm init --apiserver-cert-extra-sans=controlplane --apiserver-advertise-address $IP_ADDR --pod-network-cidr=10.244.0.0/16
    ```
    2. init완료 후 cluster 접근 정보를 kubectl 디렉터리로 복사한다
    ```sh
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    ```
14. Worker node 설치
master node init후 발급되는 토큰을 이용해 cluster join을 진행한다.
```sh
kubeadm join 192.8.56.9:6443 --token w7u33y.4ij3jy55d9o3wqqa \
--discovery-token-ca-cert-hash sha256:da7c8753a36dd3ad1b117490941b6468eae862ef5b7078e0f30f5968e7e28b5f 
```
15.  Flannel 설치
    1.  flannel 다운로드 
    ```sh
    wget https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
    ```
    2. flannel 컨테이너에 eth0 인터페이스 사용하도록 파라미터 추가
    ```yaml
    containers:
      - args:
        - --ip-masq
        - --kube-subnet-mgr
        - --iface=eth0
        command:
        - /opt/bin/flanneld
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: EVENT_QUEUE_DEPTH
          value: "5000"
        image: docker.io/flannel/flannel:v0.25.4
        name: kube-flannel
    ```
