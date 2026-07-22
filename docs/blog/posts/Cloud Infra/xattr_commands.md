---
draft: false
date: 2026-07-20
authors:
  - dotoryeee
categories:
  - Linux
tags:
  - xattr
  - ACL
  - Filesystem
description: "macOS xattr와 Linux getfattr·setfacl·setcap·chattr가 다루는 대상과 저장 위치 차이를 실측으로 비교 정리"
---

# xattr 유사 명령어 정리

<!-- more -->

## 확장 속성(xattr)이란

파일 데이터와 inode 기본 메타데이터(권한, 소유자, 타임스탬프) 외에 `이름=값` 쌍을 파일에 덧붙여 저장하는 파일시스템 기능.

- macOS는 단일 xattr 명령으로 전부 다룸
- Linux는 목적별로 명령이 갈라짐. 상당수는 결국 같은 xattr 저장소를 쓰지만 인터페이스가 다름
- chattr/lsattr만 계층이 다름. xattr가 아니라 inode 플래그를 건드림

|명령|플랫폼|다루는 대상|실제 저장 위치|
|---|---|---|---|
|xattr|macOS|임의 이름=값, 쿼런틴|xattr (com.apple.* 등)|
|getfattr/setfattr|Linux|임의 이름=값|xattr (user 네임스페이스)|
|getfacl/setfacl|Linux|POSIX ACL|xattr (system.posix_acl_access)|
|getcap/setcap|Linux|파일 capabilities|xattr (security.capability)|
|chattr/lsattr|Linux|inode 플래그 (+i/+a 등)|xattr 아님 (inode 필드)|

---

## xattr (macOS)

|옵션|설명|
|---|---|
|-l|모든 속성 이름과 값 출력|
|-p 이름|특정 속성 값만 출력|
|-w 이름 값|속성 쓰기|
|-d 이름|특정 속성 삭제|
|-c|모든 속성 제거|
|-r|디렉터리 하위까지 재귀 (-rd 형태로 조합)|

macOS 26.5.2 실측:

```s
$ echo "hello dotoryeee" > dotoryeee.txt
$ xattr -w com.dotoryeee.author "dotoryeee" dotoryeee.txt
$ xattr -l dotoryeee.txt
com.apple.provenance: 
com.dotoryeee.author: dotoryeee
$ xattr -c dotoryeee.txt
$ xattr dotoryeee.txt
com.apple.provenance
```

- xattr -c로 지워도 com.apple.provenance는 커널이 제거 요청을 에러 없이 무시해 그대로 남음 → 사용자 속성만 정리됨
- 인터넷에서 받은 파일에는 com.apple.quarantine가 붙어 Gatekeeper 실행 경고의 근거가 됨

```s
$ xattr -p com.apple.quarantine dotoryeee-dl.txt
0083;6a5e100a;dotoryeee-app;21366EB2-48E8-47A6-9E33-B1D3B3D98202
$ xattr -d com.apple.quarantine dotoryeee-dl.txt   #쿼런틴 해제
```

- 값은 `플래그;시각(hex);다운로드주체;UUID` 4필드. 실제 다운로드 파일에서도 같은 구조 확인. 디렉터리 전체는 xattr -dr로 해제

---

## getfattr / setfattr (Linux)

user 네임스페이스에 임의 메타데이터를 붙이는 명령. attr 패키지에 포함.

Ubuntu 24.04 (attr 2.5.2) 실측:

```s
# setfattr -n user.author -v "dotoryeee" dotoryeee.txt
# setfattr -n user.comment -v "custom metadata" dotoryeee.txt
# getfattr -d dotoryeee.txt
# file: dotoryeee.txt
user.author="dotoryeee"
user.comment="custom metadata"
# setfattr -x user.comment dotoryeee.txt   #속성 삭제
```

- getfattr -d는 user 네임스페이스만 덤프. 다른 네임스페이스까지 보려면 -m - 필요. -e hex로 바이너리 값은 16진수 표기

### Linux 네임스페이스

xattr 이름은 `네임스페이스.이름` 규칙. 접두어에 따라 권한과 용도가 갈림.

|네임스페이스|용도|권한|
|---|---|---|
|user|사용자 임의 메타데이터|일반 사용자 (일반 파일)|
|security|SELinux 레이블, capabilities|보안 모듈·root|
|system|POSIX ACL 등 커널 기능|커널 중재|
|trusted|권한 있는 프로세스 전용|CAP_SYS_ADMIN|

- macOS에는 이 네임스페이스 구분이 없음. com.apple.* 같은 역방향 도메인 이름 관례로만 구분
- setfacl·setcap은 결국 system·security 네임스페이스 xattr를 대신 써주는 전용 도구

---

## chattr / lsattr (inode 플래그)

이름이 비슷해 xattr로 오해하기 쉽지만 xattr가 아님. 커널의 inode 플래그를 켜고 끔. ext 계열 전용이 아니라 XFS·Btrfs·F2FS도 +i/+a 같은 주요 플래그를 지원 (지원 범위는 파일시스템별 상이).

|플래그|의미|
|---|---|
|+i (immutable)|수정·삭제·이름변경·링크 전부 차단|
|+a (append-only)|덧붙이기만 허용, 덮어쓰기·삭제 차단|

Ubuntu 24.04 (--cap-add LINUX_IMMUTABLE) 실측:

```s
# chattr +i dotoryeee-i.txt
# lsattr dotoryeee-i.txt
----i---------e------- dotoryeee-i.txt
# echo v2 > dotoryeee-i.txt
bash: dotoryeee-i.txt: Operation not permitted   #root도 차단됨
# chattr -i dotoryeee-i.txt                       #해제해야 다시 쓰기 가능
# chattr +a dotoryeee-a.txt
# echo line2 >> dotoryeee-a.txt     #append는 통과
# echo x > dotoryeee-a.txt          #truncate는 차단
bash: dotoryeee-a.txt: Operation not permitted
```

- +i는 root 권한으로도 못 지움 → 설정 파일 변조·삭제 방어에 사용
- +a는 로그 파일에 적합. 덧붙이기만 되고 과거 기록 위변조 불가
- 플래그 조작 자체가 CAP_LINUX_IMMUTABLE 필요. 컨테이너 기본 권한으로는 chattr +i가 막힘

---

## getfacl / setfacl · getcap / setcap

둘 다 전용 명령이지만 값은 xattr에 저장됨.

POSIX ACL 실측 (setfacl → system.posix_acl_access):

```s
# setfacl -m u:dotoryeee:rw dotoryeee-acl.txt
# getfacl dotoryeee-acl.txt
user::rw-
user:dotoryeee:rw-
mask::rw-
other::r--
# ls -l dotoryeee-acl.txt
-rw-rw-r--+ 1 root root 3 ... dotoryeee-acl.txt   #끝의 +가 ACL 존재 표시
```

capabilities 실측 (setcap → security.capability):

```s
# setcap cap_net_raw+ep dotoryeee-ping
# getcap dotoryeee-ping
dotoryeee-ping cap_net_raw=ep
# getfattr -m - -d -e hex dotoryeee-ping
security.capability=0x0100000200200000000000000000000000000000
```

- setuid 바이너리는 root 권한을 통째로 얹지만, capability는 필요한 하나만 부여 → 권한 최소화
- SELinux 레이블도 security.selinux xattr에 저장됨 (예시: ls -Z로 확인. 위 컨테이너는 SELinux 미적용이라 미실측)

---

## 크기 제한과 파일시스템 의존성

- VFS 상한: 이름 255바이트, 값 64KB, 이름 목록 64KB (man 7 xattr)
- 개별 파일시스템이 더 빡빡한 실제 한도를 강제

Ubuntu 24.04 overlay(ext4 계열) 실측:

```s
# setfattr -n user.big -v <65537바이트> f.txt
setfattr: f.txt: Argument list too long     #VFS 64KB 초과 → E2BIG
# setfattr -n user.big -v <4096바이트> f.txt
setfattr: f.txt: No space left on device    #ext4 xattr 블록(~4KB) 초과 → ENOSPC
# setfattr -n user.<256자 이름> ...
setfattr: f.txt: Numerical result out of range   #이름 255 초과 → ERANGE
```

- ext4는 inode 여유 공간과 xattr 블록 1개(보통 4KB)에 저장 → 파일당 xattr 총량이 4KB 안팎에서 막힘
- 값 64KB는 VFS가 허용해도 파일시스템이 먼저 ENOSPC로 거절. 실제 한도는 파일시스템에 종속

---

## 복사·백업 시 xattr 보존

xattr는 파일 데이터가 아니라 별도 메타데이터라 복사·업로드 과정에서 유실되기 쉬움.

Ubuntu 24.04 실측 (user.author 속성을 붙인 뒤 각 방식으로 복사):

|방식|xattr 보존|
|---|---|
|cp -p|❌|
|cp --preserve=all|✅|
|rsync -aX|✅|
|tar --xattrs|✅|

- cp -p는 권한·소유자·시각만 보존. xattr는 --preserve=all(또는 -a)가 있어야 따라옴
- macOS cp는 기본으로 xattr를 보존 (플랫폼 차이). 실측에서 복사본의 xattr -l 값이 그대로 유지됨
- S3·FTP처럼 데이터 스트림만 전송하는 경로는 xattr가 넘어가지 않음 → 쿼런틴·ACL·capability가 목적지에서 사라짐

---

## 사용 사례

|상황|명령|
|---|---|
|다운로드 파일 Gatekeeper 경고 해제 (macOS)|xattr -d com.apple.quarantine <file>|
|파일에 커스텀 메타데이터 부착 (Linux)|setfattr -n user.<키> -v <값> <file>|
|설정 파일 변조·삭제 방지|chattr +i <file>|
|로그 위변조 방지 (덧붙이기만 허용)|chattr +a <file>|
|특정 사용자에게만 추가 권한 부여|setfacl -m u:<user>:rw <file>|
|setuid 없이 특정 권한만 부여|setcap cap_net_raw+ep <binary>|
|xattr까지 보존하는 백업|rsync -aX 또는 tar --xattrs|

## 결론

- xattr는 "파일에 이름표를 붙이는 창구", chattr는 "파일 자체를 잠그는 자물쇠"
- setfacl·setcap·쿼런틴은 이름표가 붙는 네임스페이스만 다를 뿐 결국 같은 xattr 저장소를 공유
- 복사·업로드 한 번에 사라질 수 있는 메타데이터라 백업은 -X, --xattrs로 명시해 챙길 것
