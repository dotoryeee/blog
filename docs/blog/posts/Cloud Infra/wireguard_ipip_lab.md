---
draft: false
date: 2026-07-20
authors:
  - dotoryeee
categories:
  - Network
tags:
  - WireGuard
  - IPIP
  - MTU
  - Tunnel
description: "Docker 컨테이너 두 대에 IPIP·WireGuard 터널을 직접 올려 tcpdump로 평문·암호문을 대조하고 iperf3 처리량과 MTU까지 실측한 기록"
---

# IPIP와 WireGuard 터널 직접 구성하고 비교하기

<!-- more -->

## 목표

---

- 리눅스 노드 두 대를 두고 IPIP 터널과 WireGuard 터널을 직접 구성해 올린다
- 같은 트래픽을 두 터널로 흘려보내고 언더레이를 tcpdump로 캡처해 캡슐화 결과를 눈으로 대조한다
- IPIP는 내부 페이로드가 평문으로 새고, WireGuard는 같은 페이로드가 암호문으로 바뀌는 것을 grep으로 확인한다
- iperf3로 터널 없음, IPIP, WireGuard 세 경로의 처리량을 재고 MTU를 실측한다

프로토콜 원리와 항목별 비교표는 WireGuard vs IPIP 차이점 정리 글에서 다루고, 이 글은 손으로 올려 값을 뽑는 데 집중한다.

## 실습 환경

---

macOS의 Docker Desktop은 linuxkit 리눅스 VM 위에서 컨테이너를 돌린다. 그 VM 커널이 ipip와 wireguard 모듈을 이미 제공하므로 노드 역할의 컨테이너 두 개를 같은 브리지 네트워크에 붙이면 물리 노드 두 대처럼 쓸 수 있다. NET_ADMIN과 privileged를 줘야 터널 인터페이스를 만들 수 있다.

```s
docker network create dotoryeee-tunnel-net

docker run -d --name dotoryeee-node1 --hostname node1 --network dotoryeee-tunnel-net \
  --cap-add NET_ADMIN --privileged ubuntu:24.04 sleep infinity
docker run -d --name dotoryeee-node2 --hostname node2 --network dotoryeee-tunnel-net \
  --cap-add NET_ADMIN --privileged ubuntu:24.04 sleep infinity

# 두 노드에 도구 설치
for n in dotoryeee-node1 dotoryeee-node2; do
  docker exec $n bash -c 'apt-get update -qq &&
    apt-get install -y -qq iproute2 wireguard-tools iperf3 tcpdump iputils-ping'
done
```

브리지가 각 컨테이너에 자동으로 준 언더레이 IP는 다음과 같다. 이 IP가 터널의 바깥 헤더에 실릴 전달용 주소다.

| 노드 | 언더레이 IP(eth0) | IPIP 터널 IP | WireGuard 터널 IP |
|---|---|---|---|
| dotoryeee-node1 | 172.21.0.2 | 10.100.0.1 | 10.200.0.1 |
| dotoryeee-node2 | 172.21.0.3 | 10.100.0.2 | 10.200.0.2 |

커널과 도구 버전은 아래와 같다. modprobe나 lsmod는 이미지에 없지만 /sys/module 아래에 ipip와 wireguard가 이미 올라와 있어 별도 적재 없이 바로 진행할 수 있다.

```s
docker exec dotoryeee-node1 bash -c 'uname -sr; ip -V; wg --version'
Linux 6.12.76-linuxkit
ip utility, iproute2-6.1.0, libbpf 1.3.0
wireguard-tools v1.0.20210914 - https://git.zx2c4.com/wireguard-tools/
```

## IPIP 터널 구성

---

1. 두 노드에 각각 ipip 모드 터널을 만든다. local과 remote는 물리 인터페이스 IP이고, 방향만 서로 뒤집어 대칭으로 잡는다

    ```s
    # node1
    ip tunnel add ipip0 mode ipip local 172.21.0.2 remote 172.21.0.3
    ip addr add 10.100.0.1/30 dev ipip0
    ip link set ipip0 up

    # node2 (local/remote 반전)
    ip tunnel add ipip0 mode ipip local 172.21.0.3 remote 172.21.0.2
    ip addr add 10.100.0.2/30 dev ipip0
    ip link set ipip0 up
    ```

2. 키도 핸드셰이크도 없다. 인터페이스가 올라온 순간 바로 터널 내부 대역으로 통신된다. node1에서 반대편 터널 IP로 ping을 쏴본다

    ```s
    docker exec dotoryeee-node1 ping -c 3 10.100.0.2
    PING 10.100.0.2 (10.100.0.2) 56(84) bytes of data.
    64 bytes from 10.100.0.2: icmp_seq=1 ttl=64 time=0.082 ms
    64 bytes from 10.100.0.2: icmp_seq=2 ttl=64 time=0.195 ms
    64 bytes from 10.100.0.2: icmp_seq=3 ttl=64 time=0.527 ms

    --- 10.100.0.2 ping statistics ---
    3 packets transmitted, 3 received, 0% packet loss, time 2077ms
    ```

인터페이스를 자세히 보면 MTU가 1480으로 잡혀 있다. 언더레이 1500에서 바깥 IPv4 헤더 20바이트만큼 줄어든 값이다.

```s
docker exec dotoryeee-node1 ip -d addr show ipip0
12: ipip0@NONE: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1480 qdisc noqueue state UNKNOWN
    link/ipip 172.21.0.2 peer 172.21.0.3 ...
    ipip ipip remote 172.21.0.3 local 172.21.0.2 ttl inherit ...
    inet 10.100.0.1/30 scope global ipip0
```

## WireGuard 터널 구성

---

1. 각 노드에서 개인키와 공개키 쌍을 만든다. wg genkey로 개인키를 뽑고 그걸 wg pubkey에 넘겨 공개키를 얻는다

    ```s
    # node1
    umask 077; wg genkey | tee /tmp/priv1 | wg pubkey > /tmp/pub1
    # node2
    umask 077; wg genkey | tee /tmp/priv2 | wg pubkey > /tmp/pub2
    ```

2. 인터페이스를 만들고 개인키, 리슨 포트, 피어를 설정한다. 피어 블록에는 상대 공개키, 허용 대역(AllowedIPs), 최초 접속용 엔드포인트를 넣는다. node1의 최종 설정은 이렇게 굳는다

    ```s
    docker exec dotoryeee-node1 wg showconf wg0
    [Interface]
    ListenPort = 51820
    PrivateKey = (개인키)

    [Peer]
    PublicKey = uIy0M6/XqRY9aOE2+APDKgv3628xp/gAvmrbbwU2nHs=
    AllowedIPs = 10.200.0.2/32
    Endpoint = 172.21.0.3:51820
    ```

3. node1에서 반대편 터널 IP로 ping을 쏘면 첫 패킷을 계기로 핸드셰이크가 성립하고 곧바로 응답이 돌아온다

    ```s
    docker exec dotoryeee-node1 ping -c 3 10.200.0.2
    64 bytes from 10.200.0.2: icmp_seq=1 ttl=64 time=0.589 ms
    64 bytes from 10.200.0.2: icmp_seq=2 ttl=64 time=1.41 ms
    64 bytes from 10.200.0.2: icmp_seq=3 ttl=64 time=0.580 ms
    ```

4. wg show로 세션 상태를 확인한다. latest handshake에 시각이 찍혀 있으면 세션키가 확립된 것이다

    ```s
    docker exec dotoryeee-node1 wg show
    interface: wg0
      public key: SHupqA8rhRCxSHm6gSRRaI5D5cXLvlI5qQ8cWhkMLjE=
      private key: (hidden)
      listening port: 51820

    peer: uIy0M6/XqRY9aOE2+APDKgv3628xp/gAvmrbbwU2nHs=
      endpoint: 172.21.0.3:51820
      allowed ips: 10.200.0.2/32
      latest handshake: 3 seconds ago
      transfer: 476 B received, 532 B sent
    ```

핸드셰이크가 오가는 순간을 언더레이에서 잡으면 UDP 51820으로 두 패킷만 오간다. 이미 터널이 올라온 상태라 인터페이스를 한 번 내렸다 올려 핸드셰이크를 다시 유발한 뒤 캡처한다. WireGuard의 핸드셰이크 개시 메시지는 148바이트, 응답 메시지는 92바이트로 크기가 고정돼 있어 값이 그대로 찍힌다.

```s
docker exec dotoryeee-node2 tcpdump -i eth0 -n udp port 51820 -c 2 &   # 캡처를 백그라운드로 대기
docker exec dotoryeee-node1 sh -c 'ip link set wg0 down; ip link set wg0 up'   # 인터페이스 재기동으로 핸드셰이크 재유발
docker exec dotoryeee-node1 ping -c 1 10.200.0.2                       # 첫 패킷으로 핸드셰이크 개시
172.21.0.2.51820 > 172.21.0.3.51820: UDP, length 148   # Handshake Initiation
172.21.0.3.51820 > 172.21.0.2.51820: UDP, length 92    # Handshake Response
172.21.0.2.51820 > 172.21.0.3.51820: UDP, length 148   # Handshake Initiation
172.21.0.3.51820 > 172.21.0.2.51820: UDP, length 92    # Handshake Response
```

## 암호화 대조 실측

---

여기가 이 실습의 핵심이다. 같은 성격의 트래픽을 두 터널에 각각 흘리고 바깥 인터페이스에서 캡처해 페이로드가 보이는지 확인한다. 페이로드가 눈에 띄게 하려고 ping에 dotoryeee라는 문자열 패턴을 실어 보낸다. ping의 -p 옵션은 ICMP 페이로드를 지정한 16진 패턴으로 채운다.

먼저 IPIP다. node2의 eth0에서 IP 프로토콜 4(ipip)만 걸러 캡처하고, node1에서 패턴 ping을 쏜다.

```s
# node2에서 캡처
docker exec dotoryeee-node2 tcpdump -i eth0 -n -X ip proto 4 -c 2
# node1에서 dotoryeee 패턴을 실은 ping
docker exec dotoryeee-node1 ping -c 2 -p 646f746f7279656565 10.100.0.2
```

캡처 결과는 다음과 같다. tcpdump가 헤더 줄에서부터 IP 안에 또 IP가 들었음을 그대로 풀어준다. 바깥은 172.21.0.2에서 172.21.0.3, 안쪽은 10.100.0.1에서 10.100.0.2로 가는 ICMP다. 그리고 hex 덤프 오른쪽 ASCII 열에 dotoryeee가 반복돼 훤히 보인다.

```s
IP 172.21.0.2 > 172.21.0.3: IP 10.100.0.1 > 10.100.0.2: ICMP echo request, id 14, seq 1, length 64
	0x0000:  4500 0068 87e4 4000 4004 5a7e ac15 0002  E..h..@.@.Z~....
	0x0010:  ac15 0003 4500 0054 9c82 4000 4001 895c  ....E..T..@.@..\
	0x0020:  0a64 0001 0a64 0002 0800 976d 000e 0001  .d...d.....m....
	0x0030:  802b 5e6a 0000 0000 0671 0a00 0000 0000  .+^j.....q......
	0x0040:  6565 646f 746f 7279 6565 6564 6f74 6f72  eedotoryeeedotor
	0x0050:  7965 6565 646f 746f 7279 6565 6564 6f74  yeeedotoryeeedot
	0x0060:  6f72 7965 6565 646f                      oryeeedo
```

바깥 헤더 첫 바이트 45는 IPv4이고, 그 뒤 프로토콜 필드가 04다(0x0000 줄 4004에서 뒤쪽 04, IP 헤더의 9번째 바이트). 04는 페이로드가 또 하나의 IP 패킷이라는 표시다. 벗겨낸 안쪽 45로 시작하는 바이트가 원본 ICMP 패킷 그대로다. 신뢰되지 않은 경로였다면 이 페이로드가 통째로 도청된다.

이번엔 WireGuard다. 같은 dotoryeee 패턴 ping을 wg 터널로 쏘고 UDP 51820을 캡처한다.

```s
docker exec dotoryeee-node2 tcpdump -i eth0 -n -X udp port 51820 -c 2
docker exec dotoryeee-node1 ping -c 2 -p 646f746f7279656565 10.200.0.2
```

```s
IP 172.21.0.2.51820 > 172.21.0.3.51820: UDP, length 128
	0x0000:  4500 009c 51ce 0000 4011 d053 ac15 0002  E...Q...@..S....
	0x0010:  ac15 0003 ca6c ca6c 0088 58c9 0400 0000  .....l.l..X.....
	0x0020:  c7e4 a4f1 0200 0000 0000 0000 d47b 81bb  .............{..
	0x0030:  288e 54fc d9c3 5772 04f7 5f0a 409b 7cff  (.T...Wr.._.@.|.
	0x0040:  9c0d 4253 0e46 38ab be6b 6e94 2721 3c2c  ..BS.F8..kn.'!<,
	0x0050:  a9b3 44c1 b385 70c8 f9df 1daa f822 4895  ..D...p......"H.
	0x0060:  f68b 1c42 9543 3aa7 eca6 2a51 785a 5a8f  ...B.C:...*QxZZ.
	0x0070:  d656 97ae c966 8f5c 904a 7a15 fadf ef5c  .V...f.\.Jz....\
	0x0080:  16eb ad3b 82c1 ba9c 93e5 6c60 4744 ef16  ...;......l`GD..
	0x0090:  c977 4044 cd92 88b2 24a4 1b6e            .w@D....$..n
```

바깥은 UDP 51820 한 겹뿐이고, 그 안은 전부 암호문이다. ASCII 열 어디에도 dotoryeee가 없고 안쪽 IP 헤더의 흔적조차 보이지 않는다. 페이로드 앞머리 0400 0000은 WireGuard 데이터 메시지 타입이고, 그 뒤 수신자 인덱스와 카운터를 빼면 나머지는 ChaCha20-Poly1305로 봉인된 바이트다.

두 캡처 파일에서 문자열을 세어 대조하면 차이가 한 줄로 정리된다.

```s
# IPIP 캡처
grep -c dotoryeee ipip_cap.txt
4
# WireGuard 캡처
grep -c dotoryeee wg_cap.txt
0
```

- IPIP: 같은 ping 페이로드가 담긴 줄이 캡처에서 4개 검출(grep -c는 매칭 줄 수) → 경로에서 내용이 그대로 노출
- WireGuard: 같은 페이로드가 0회 검출 → 캡슐 밖에서는 내용을 복원할 수 없음

## 처리량 오버헤드

---

iperf3로 세 경로의 처리량을 잰다. node2에서 서버를 띄우고 node1이 각 대상 IP로 5초씩 접속한다. 대상 IP만 바꾸면 언더레이, IPIP, WireGuard 경로가 갈린다.

```s
docker exec -d dotoryeee-node2 iperf3 -s -D
docker exec dotoryeee-node1 iperf3 -c 172.21.0.3 -t 5 -f m -O 1   # (a) 터널 없음
docker exec dotoryeee-node1 iperf3 -c 10.100.0.2 -t 5 -f m -O 1   # (b) IPIP
docker exec dotoryeee-node1 iperf3 -c 10.200.0.2 -t 5 -f m -O 1   # (c) WireGuard
```

세 번 반복한 receiver 기준 처리량은 다음과 같다.

| 경로 | 1회차 | 2회차 | 3회차 | 대비 |
|---|---|---|---|---|
| (a) 터널 없음 | 98826 Mbps | 97699 Mbps | 98963 Mbps | 기준 |
| (b) IPIP | 75010 Mbps | 73462 Mbps | 73475 Mbps | 약 0.75배 |
| (c) WireGuard | 1416 Mbps | 1426 Mbps | 1423 Mbps | 약 0.014배 |

- IPIP는 캡슐화 처리 비용만큼 떨어지지만 여전히 수십 Gbps대를 유지한다
- WireGuard는 패킷마다 ChaCha20-Poly1305 암호화가 걸려 단일 흐름 처리량이 한 자릿수 Gbps로 급락한다
- 10코어 머신인데도 단일 흐름은 암호화가 코어 하나에 묶여 값이 1.4Gbps대에 고정된다

!!! warning
    💡 같은 호스트 브리지 위 컨테이너 통신이라 데이터 경로가 메모리 복사에 가까워 절대 수치는 실제 NIC 환경보다 크게 부풀려진다. 여기서 의미 있는 건 세 경로의 상대 비교와 경향이지 Gbps 절대값이 아니다

## MTU 실측

---

세 인터페이스의 MTU는 캡슐화 오버헤드만큼 계단식으로 줄어든다.

```s
docker exec dotoryeee-node1 sh -c 'for i in eth0 ipip0 wg0; do
  printf "%-7s mtu %s\n" "$i" "$(cat /sys/class/net/$i/mtu)"; done'
eth0    mtu 1500
ipip0   mtu 1480
wg0     mtu 1420
```

- ipip0 1480: 언더레이 1500에서 바깥 IPv4 헤더 20바이트를 뺀 값
- wg0 1420: WireGuard가 바깥 IPv6 헤더까지 감안해 넉넉히 80바이트를 빼고 잡는 기본값

wg0의 80바이트는 조금 뜯어볼 값이다. IPv4 위 데이터 패킷의 실제 와이어 오버헤드는 바깥 IP 20바이트 + UDP 8바이트 + WireGuard 헤더 16바이트 + Poly1305 인증 태그 16바이트로 약 60바이트다. 그런데 커널은 바깥 헤더가 IPv6(40바이트)일 경우까지 안전하게 잡으려고 인터페이스 MTU를 80바이트 낮춰 둔다. 그래서 IPv4 위에서는 20바이트가 여유로 남는다.

값이 진짜인지 DF 비트를 세운 큰 패킷 ping으로 검증한다. ICMP 데이터에 헤더 28바이트를 더한 크기가 인터페이스 MTU를 넘으면 조각내지 못하고 로컬에서 막힌다.

```s
# IPIP (MTU 1480): 1452바이트는 통과, 1453바이트는 실패
docker exec dotoryeee-node1 ping -c 1 -M do -s 1452 10.100.0.2
1460 bytes from 10.100.0.2: icmp_seq=1 ttl=64 time=0.072 ms
docker exec dotoryeee-node1 ping -c 1 -M do -s 1453 10.100.0.2
ping: local error: message too long, mtu=1480

# WireGuard (MTU 1420): 1392바이트는 통과, 1393바이트는 실패
docker exec dotoryeee-node1 ping -c 1 -M do -s 1392 10.200.0.2
1400 bytes from 10.200.0.2: icmp_seq=1 ttl=64 time=0.607 ms
docker exec dotoryeee-node1 ping -c 1 -M do -s 1393 10.200.0.2
ping: local error: message too long, mtu=1420
```

경계 바이트에서 정확히 갈린다. 1452바이트 페이로드는 28바이트를 더해 딱 1480, 1392바이트는 딱 1420이 돼 통과하고, 각각 1바이트만 커지면 인터페이스 MTU를 넘어 막힌다. 오류 메시지의 mtu 값이 앞서 본 인터페이스 MTU와 일치한다.

## 자원 정리

---

실습이 끝나면 만든 컨테이너와 네트워크만 골라 지운다. 다른 실습 컨테이너를 건드리는 prune은 쓰지 않는다.

```s
docker rm -f dotoryeee-node1 dotoryeee-node2
docker network rm dotoryeee-tunnel-net
```

## 요약

---

캡슐화·암호화 원리와 Noise_IK 핸드셰이크, MTU 계산 같은 배경은 [WireGuard vs IPIP 차이점 정리](wireguard_ipip.md)에서 다뤘다.

- IPIP는 키도 핸드셰이크도 없이 local과 remote만 맞추면 바로 붙고, 바깥 IP 헤더 20바이트만 덧대 MTU가 1480으로만 줄어든다
- WireGuard는 키 쌍을 만들고 피어를 걸면 첫 패킷에 핸드셰이크가 서고, IPv6까지 감안한 기본 MTU 예약으로 MTU가 1420이 된다(IPv4 실제 오버헤드는 60바이트)
- 같은 dotoryeee 페이로드를 언더레이에서 캡처하면 평문이 담긴 줄이 IPIP는 4개, WireGuard는 0개로 갈린다. 캡슐화만 하는 터널과 암호화까지 하는 터널의 차이가 캡처 한 장에 다 드러난다
- 처리량은 IPIP가 기준의 약 0.75배, WireGuard가 약 0.014배로, 암호화 비용이 캡슐화 비용보다 훨씬 크다
- 경로를 신뢰할 수 있으면 IPIP로 가볍게, 도청을 막아야 하면 WireGuard로 무겁더라도 안전하게
