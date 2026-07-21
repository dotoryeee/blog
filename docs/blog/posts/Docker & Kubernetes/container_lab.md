---
draft: false
date: 2026-07-20
authors:
  - dotoryeee
categories:
  - Docker
tags:
  - Container
  - Namespace
  - cgroup
  - overlayfs
  - veth
description: "docker 없이 unshare·cgroup·chroot·overlayfs·veth만으로 컨테이너를 손수 조립하고 20M 메모리 제한 OOM까지 실측한 기록"
hide:
  - toc
---

# docker 없이 컨테이너 만들어보기

<!-- more -->

## 목표

---

- docker 명령 없이 리눅스 커널 기능만으로 컨테이너를 손으로 조립한다
- namespace 로 프로세스가 보는 세계를 격리하고, cgroup 으로 메모리를 제한하고, chroot 와 overlayfs 로 루트 파일시스템을 직접 만든다
- 메모리 제한을 넘긴 프로세스가 커널 OOM 킬러에 죽는 것까지 실측한다
- 마지막에 여기서 손으로 한 일이 runc 가 컨테이너를 띄울 때 하는 일과 같음을 확인한다

!!! tip
    💡 전 과정을 macOS Docker Desktop 의 리눅스 VM 커널 위에서 돌려 클라우드 비용이 들지 않는다

## 실습 환경

---

컨테이너는 별도 게스트 커널 없이 호스트 커널을 그대로 쓴다. macOS 의 Docker Desktop 은 리눅스 VM 을 하나 띄우고 그 안에서 컨테이너를 돌리므로, 그 VM 커널이 여기서의 진짜 "호스트 커널"이다. 먼저 커널 버전을 본다.

```s
docker run --rm alpine uname -srm
Linux 6.12.76-linuxkit aarch64
```

이 커널을 호스트로 삼아, privileged 로 띄운 ubuntu:24.04 컨테이너 안에서 unshare, cgroup, overlayfs 를 직접 만진다. privileged 가 필요한 이유는 mount, cgroup 쓰기, veth 생성 같은 특권 연산을 써야 하기 때문이다. hostname 은 dotoryeee-host 로 지정해 뒤의 UTS 격리 대비를 분명히 한다.

```s
docker run -it --rm --privileged --hostname dotoryeee-host --name ctr-lab ubuntu:24.04 bash
```

컨테이너에 들어오면 실습에 쓸 도구를 설치한다. unshare 와 chroot 는 util-linux 로 이미 들어 있고, iproute2(ip), iputils-ping, procps(ps), curl 만 더 깐다.

```s
apt-get update && apt-get install -y iproute2 iputils-ping procps curl
unshare --version
unshare from util-linux 2.39.3
```

자원 제한 실습에 쓸 cgroup 계층이 v2 인지 확인한다. cgroup2fs 로 나오면 단일 통합 계층이다.

```s
stat -fc %T /sys/fs/cgroup
cgroup2fs
```

## namespace 손수 만들기

---

namespace 는 프로세스가 보는 자원의 범위를 종류별로 잘라 준다. unshare 는 새 namespace 를 만들고 그 안에서 명령을 실행하는 도구다. hostname 을 담는 UTS 부터 만져본다.

1. UTS namespace 를 새로 만들고 그 안에서만 hostname 을 dotoryeee-container 로 바꾼다. namespace 를 빠져나오면 호스트 hostname 은 그대로다.

    ```s
    hostname
    dotoryeee-host

    unshare --uts sh -c 'hostname dotoryeee-container; echo " ns 내부: $(hostname)"'
     ns 내부: dotoryeee-container

    hostname
    dotoryeee-host
    ```

    ns 안에서 바꾼 hostname 이 밖으로 새지 않는다. 컨테이너마다 hostname 을 따로 갖는 것이 이 격리다.

2. PID namespace 를 만든다. --fork 로 unshare 가 자식을 하나 포크해 그 자식이 새 PID 공간의 첫 프로세스가 되고, --mount-proc 로 새 /proc 을 물려 ps 가 ns 안의 프로세스만 본다.

    ```s
    unshare --pid --fork --mount-proc bash -c 'echo "ns-init PID = $$"; sleep 60 & ps -ef; :'
    ns-init PID = 1
    UID          PID    PPID  C STIME TTY          TIME CMD
    root           1       0  0 13:58 ?        00:00:00 bash -c echo ...
    root           2       1  0 13:58 ?        00:00:00 sleep 60
    root           3       1  0 13:58 ?        00:00:00 ps -ef
    ```

    bash 가 PID 1 이 됐고 ps 에는 세 프로세스만 보인다. 호스트의 수많은 프로세스는 새 /proc 뷰에서 사라진다. 컨테이너 안에서 프로세스가 1번부터 시작하는 이유가 이것이다.

3. mount namespace 를 만들어 그 안에서 tmpfs 를 마운트한다. 마운트도, 그 위에 만든 파일도 호스트에서는 보이지 않는다.

    ```s
    mkdir -p /tmp/ns-mnt
    unshare --mount bash -c '
      mount -t tmpfs none /tmp/ns-mnt
      touch /tmp/ns-mnt/only-in-ns
      echo " ns 내부 mount:"; grep ns-mnt /proc/mounts
      echo " ns 내부 파일:"; ls /tmp/ns-mnt'
     ns 내부 mount:
    none /tmp/ns-mnt tmpfs rw,relatime 0 0
     ns 내부 파일:
    only-in-ns
    ```

    같은 경로를 호스트에서 보면 마운트도 파일도 없다.

    ```s
    grep -c ns-mnt /proc/mounts
    0
    ls -A /tmp/ns-mnt
    ```

## alpine rootfs 로 루트 바꾸기

---

namespace 로 프로세스는 격리했지만 파일시스템은 아직 호스트(ubuntu)를 그대로 본다. 컨테이너는 이미지를 풀어 만든 별도 rootfs 를 루트로 쓴다. alpine 의 mini rootfs 를 받아 chroot 로 그 안에 들어가 본다.

```s
cd /root
url=https://dl-cdn.alpinelinux.org/alpine/v3.21/releases/aarch64
curl -sO $url/alpine-minirootfs-3.21.7-aarch64.tar.gz
mkdir -p alpine-rootfs
tar -xzf alpine-minirootfs-3.21.7-aarch64.tar.gz -C alpine-rootfs
du -sh alpine-rootfs
8.5M	alpine-rootfs
```

3.7MB 짜리 tar 하나가 풀리면 bin, etc, usr 를 갖춘 최소 리눅스 루트가 된다. chroot 로 진입하면 그 안에서 본 루트가 alpine 으로 바뀐다.

```s
grep PRETTY_NAME /etc/os-release
PRETTY_NAME="Ubuntu 24.04.4 LTS"

chroot /root/alpine-rootfs /bin/sh -c '
  echo " chroot 안 os:"; grep PRETTY_NAME /etc/os-release
  echo " /bin/sh 실체:"; ls -l /bin/sh'
 chroot 안 os:
PRETTY_NAME="Alpine Linux v3.21"
 /bin/sh 실체:
lrwxrwxrwx    1 root     root            12 Apr 15 05:40 /bin/sh -> /bin/busybox
```

호스트는 Ubuntu 24.04 인데 chroot 안은 Alpine 3.21 이고, 셸도 alpine 의 busybox 다. 같은 커널 위에서 완전히 다른 배포판 루트로 프로세스를 돌린 것이다.

chroot 는 루트 디렉터리 경로만 바꿀 뿐 마운트 네임스페이스를 건드리지 않아 탈옥 여지가 있다. 실제 런타임은 마운트 루트 자체를 갈아끼우는 pivot_root 를 쓰는데, 둘의 차이는 chroot, pivot_root, switch_root 비교 글에서 다뤘다.

이제 앞의 namespace 와 이 rootfs 를 한 줄로 붙이면 컨테이너 골격이 나온다. UTS, PID, mount 를 한꺼번에 만들고, hostname 을 바꾸고, alpine 으로 chroot 한 뒤 그 안에서 /proc 을 새로 마운트한다. init.sh 는 alpine rootfs 안에 미리 넣어 둔 스크립트다.

```s title="alpine-rootfs/init.sh"
#!/bin/sh
mount -t proc proc /proc
echo " hostname : $(hostname)"
echo " os       : $(grep PRETTY_NAME /etc/os-release | cut -d= -f2)"
echo " 프로세스 트리:"
ps -ef
```

```s
unshare --uts --pid --mount --fork bash -c \
  'hostname dotoryeee-container; exec chroot /root/alpine-rootfs /bin/sh /init.sh'
 hostname : dotoryeee-container
 os       : "Alpine Linux v3.21"
 프로세스 트리:
PID   USER     TIME  COMMAND
    1 root      0:00 /bin/sh /init.sh
    9 root      0:00 ps -ef
```

hostname 은 dotoryeee-container, 루트는 alpine, 셸은 PID 1, 프로세스 트리에는 ns 안의 두 프로세스만 보인다. docker run 없이 만든 컨테이너다. 여기에 자원 제한과 이미지 레이어, 네트워크를 얹으면 실제 런타임이 하는 일에 가까워진다.

## cgroup v2 로 메모리 제한과 OOM

---

namespace 는 "무엇을 보는가"를 격리하지, "얼마나 쓰는가"는 막지 못한다. 메모리 상한은 cgroup 이 건다. cgroup v2 에서 자식 그룹이 memory 컨트롤러를 쓰려면 부모의 subtree_control 에 memory 를 위임해야 하는데, 프로세스가 직접 들어 있는 cgroup 은 자식으로 컨트롤러를 위임하지 못한다(no internal processes 규칙). 컨테이너 안 /sys/fs/cgroup 은 cgroup namespace 때문에 루트처럼 보여도 실제로는 위임된 비루트 서브트리라 이 규칙이 그대로 걸린다. 그래서 먼저 그 프로세스를 leaf 로 옮긴 뒤 위임한다.

```s
cd /sys/fs/cgroup
mkdir -p init
for pid in $(cat cgroup.procs); do echo $pid > init/cgroup.procs 2>/dev/null; done
echo "+memory +pids" > cgroup.subtree_control
cat cgroup.subtree_control
memory pids
```

이제 dotoryeee 그룹을 만들고 메모리 상한을 20M 로, 스왑은 0 으로 잠근다. 스왑을 막아야 상한을 넘긴 순간 바로 OOM 이 발동한다.

```s
mkdir -p /sys/fs/cgroup/dotoryeee
echo 20M > /sys/fs/cgroup/dotoryeee/memory.max
echo 0   > /sys/fs/cgroup/dotoryeee/memory.swap.max
cat /sys/fs/cgroup/dotoryeee/memory.max
20971520
```

이 그룹 안에서 메모리를 끝없이 먹는 프로세스를 돌린다. 셸이 자기 PID 를 cgroup.procs 에 써 넣어 스스로 그룹에 들어간 뒤, tail /dev/zero 로 무한한 0 을 한 줄로 쌓아 메모리를 늘린다.

```s
bash -c '
  echo $$ > /sys/fs/cgroup/dotoryeee/cgroup.procs
  echo " hog PID = $$ (dotoryeee 그룹에 등록)"
  exec tail /dev/zero'
 hog PID = 2783 (dotoryeee 그룹에 등록)
bash: line 9:  2783 Killed  bash -c ...
```

프로세스가 Killed 됐다. 종료 코드와 그룹의 이벤트 카운터를 본다. oom_kill 이 1 로 올랐고 최대 사용량은 정확히 상한인 20M 에서 멈췄다.

```s
echo "종료 코드 = $?"
종료 코드 = 137
cat /sys/fs/cgroup/dotoryeee/memory.events
low 0
high 0
max 39
oom 1
oom_kill 1
oom_group_kill 0
cat /sys/fs/cgroup/dotoryeee/memory.peak
20971520
```

종료 코드 137 은 128+9, 즉 SIGKILL 이다. 커널 로그(dmesg)에는 어느 memcg 가 넘쳐 어떤 프로세스를 죽였는지가 그대로 남는다.

```s
dmesg | grep -iE 'oom|killed process' | tail -3
tail invoked oom-killer: gfp_mask=0xcc0(GFP_KERNEL), order=0, oom_score_adj=0
... oom_memcg=/docker/22945.../dotoryeee,task_memcg=/docker/22945.../dotoryeee,task=tail...
Memory cgroup out of memory: Killed process 77559 (tail) total-vm:22500kB, anon-rss:20224kB...
```

oom_memcg 가 우리가 만든 dotoryeee 그룹이고, RSS 가 20MB 근처에서 죽었다. 여기서 죽은 프로세스의 PID 는 77559 인데, 컨테이너 안에서 본 PID(2783)와 다르다. dmesg 는 VM 커널의 전역 PID 로 찍고, 컨테이너는 자기 PID namespace 의 번호로 보기 때문이다. docker run 의 memory 옵션이 하는 일이 바로 이 memory.max 쓰기다.

## overlayfs 로 copy-on-write

---

이미지는 읽기 전용 레이어를 쌓아 만든다. 컨테이너가 그 위에 쓰기 레이어를 얹어 하나의 루트로 보게 해 주는 것이 overlayfs 다. lowerdir(읽기 전용), upperdir(쓰기), merged(병합 뷰)를 직접 마운트해 동작을 본다.

먼저 그냥 마운트하면 실패한다. Docker 컨테이너의 루트 자체가 이미 overlay2 라 그 위에 다시 overlay 를 얹지 못한다.

```s
mkdir -p /root/ovl/{lower,upper,work,merged}
mount -t overlay overlay -o lowerdir=/root/ovl/lower,upperdir=/root/ovl/upper,workdir=/root/ovl/work /root/ovl/merged
mount: /root/ovl/merged: wrong fs type, bad option, bad superblock ...
dmesg | grep -i overlay | tail -1
overlay: filesystem on /root/ovl/upper not supported as upperdir
```

upperdir 를 overlay 가 아닌 파일시스템에 두면 된다. tmpfs 를 하나 깔고 그 위에서 다시 마운트한다.

```s
mkdir -p /mnt/ovl && mount -t tmpfs tmpfs /mnt/ovl
cd /mnt/ovl && mkdir -p lower upper work merged
echo "이미지 레이어의 원본 설정" > lower/app.conf
echo "readme (lower 전용)"      > lower/readme.txt
mount -t overlay overlay -o lowerdir=/mnt/ovl/lower,upperdir=/mnt/ovl/upper,workdir=/mnt/ovl/work /mnt/ovl/merged
ls merged
app.conf
readme.txt
```

merged 에는 lower 의 파일이 그대로 보인다. upper 는 아직 비어 있다. 이 상태에서 merged 쪽에서 lower 파일을 수정하면, 원본 lower 는 건드리지 않고 변경분이 upper 로 복사된다. 이것이 copy-on-write 다.

```s
echo "컨테이너가 추가한 줄" >> merged/app.conf
echo "컨테이너 신규 파일"   > merged/newfile.txt

echo "--- upper (변경분만 저장) ---"; ls upper
--- upper (변경분만 저장) ---
app.conf
newfile.txt

echo "--- lower (원본 불변) ---"; cat lower/app.conf
--- lower (원본 불변) ---
이미지 레이어의 원본 설정

echo "--- merged (병합 결과) ---"; cat merged/app.conf
--- merged (병합 결과) ---
이미지 레이어의 원본 설정
컨테이너가 추가한 줄
```

lower 의 app.conf 는 원본 한 줄 그대로인데, upper 에는 수정된 app.conf 와 새로 만든 newfile.txt 가 생겼다. 컨테이너를 지우면 upper(쓰기 레이어)만 사라지고 lower(이미지 레이어)는 남는 이유가 이 구조다.

## network namespace 와 veth

---

network namespace 는 네트워크 장치, 라우팅 테이블, 포트 공간을 통째로 격리한다. 빈 netns 두 개를 만들고 veth pair(가상 랜선의 양 끝)로 이어 서로 통신시킨다.

```s
ip netns add ctr-lab-ns1
ip netns add ctr-lab-ns2
ip link add veth1 type veth peer name veth2
ip link set veth1 netns ctr-lab-ns1
ip link set veth2 netns ctr-lab-ns2
ip netns exec ctr-lab-ns1 ip addr add 10.10.0.1/24 dev veth1
ip netns exec ctr-lab-ns2 ip addr add 10.10.0.2/24 dev veth2
ip netns exec ctr-lab-ns1 ip link set veth1 up
ip netns exec ctr-lab-ns2 ip link set veth2 up
```

veth 한쪽씩을 각 netns 에 넣고 IP 를 부여했다. ns1 에서 ns2 로 ping 을 쏜다.

```s
ip netns exec ctr-lab-ns1 ping -c 3 10.10.0.2
PING 10.10.0.2 (10.10.0.2) 56(84) bytes of data.
64 bytes from 10.10.0.2: icmp_seq=1 ttl=64 time=0.017 ms
64 bytes from 10.10.0.2: icmp_seq=2 ttl=64 time=0.016 ms
64 bytes from 10.10.0.2: icmp_seq=3 ttl=64 time=0.016 ms

--- 10.10.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2042ms
```

두 격리된 네트워크가 veth 로 이어져 통신한다. 이 veth 도 10.10.0.x 라우트도 호스트에는 전혀 없다.

```s
ip -br addr show | grep -c veth
0
ip route | grep -c 10.10.0
0
```

컨테이너 하나에 veth 한쪽을 넣고 반대쪽을 브리지에 붙이면 docker0 네트워크가 된다. 여기서는 브리지 대신 netns 를 하나 더 둬 pair 를 직접 이어 본 것이다.

## runc 가 하는 일

---

여기까지 손으로 한 일을 한 줄로 요약하면, unshare 로 namespace 를 만들고, chroot 로 루트를 갈고, cgroup 에 memory.max 를 쓰고, overlayfs 로 레이어를 겹치고, veth 로 netns 를 이었다. 이 순서가 그대로 저수준 런타임 runc 가 컨테이너를 띄울 때 하는 일이다.

- runc 는 OCI runtime-spec 의 config.json 을 읽어 namespace 조합, cgroup 한도, rootfs 경로, 마운트, 네트워크를 세팅한 뒤 컨테이너 프로세스를 exec 한다
- 실무에서는 pivot_root 로 루트를 더 안전하게 갈고, user namespace 로 컨테이너 root 를 호스트 비특권 UID 에 매핑해 격리를 강화한다
- 이 조각들이 어떤 계층(docker CLI, dockerd, containerd, shim, runc)을 거쳐 조립되는지는 [컨테이너 내부 구조 정리](container_internals.md) 글에서 다뤘다

컨테이너는 마법이 아니라 커널 기능 몇 개의 조합이다. namespace 로 격리하고 cgroup 으로 제한한 프로세스, 그 한 문장을 손으로 만들어 확인했다.
