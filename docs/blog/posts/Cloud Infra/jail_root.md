---
draft: false
date: 2025-03-16
authors:
  - dotoryeee
categories:
  - Server
---
# chroot, pivot_root, switch_root 비교

<!-- more -->

# 비교표
|특성|chroot|pivot_root|switch_root|
|----|-----|----------|------------|
|정의|프로세스의 루트 디렉토리를 변경하는 시스템 콜|마운트 네임스페이스의 루트 마운트 포인트를 변경하는 시스템 콜|초기 부팅 환경에서 실제 루트 파일시스템으로 전환하는 유틸리티|
|주요 목적|파일 시스템 접근 제한|컨테이너 격리 및 보안|초기 부팅 환경에서 실제 루트 파일시스템으로 전환|
|보안 수준|낮음 (탈옥 가능)|높음 (탈옥 어려움)|중간 (부팅 과정에 초점)|
|구현 복잡성|단순함|복잡함|중간|
|이전 루트 처리|이전 루트 접근 가능|이전 루트를 새 위치에 마운트 가능|이전 루트 삭제|
|컨테이너 기술|초기 컨테이너 기술, 간단한 샌드박스|Docker, Podman, containerd, CRI-O 등 현대 컨테이너 런타임|사용하지 않음|
|초기 램디스크|사용하지 않음|initrd (Initial RAM Disk)|initramfs (Initial RAM Filesystem)|
|작동 방식|프로세스의 루트 디렉토리 경로만 변경|마운트 네임스페이스의 루트 마운트 포인트 자체를 변경|chroot 실행 후 이전 루트 삭제 및 마운트 포인트 이동|
|시스템 콜|chroot()|pivot_root()|여러 시스템 콜 조합 (chroot, umount, mount 등)|
|마운트 포인트 처리|기존 마운트 포인트 유지|기존 마운트 포인트 재배치 가능|중요 마운트 포인트(/proc, /sys 등)를 새 루트로 이동|
|필요 권한|루트 권한 필요|루트 권한 및 CAP_SYS_ADMIN 권한 필요|루트 권한 필요|
|네임스페이스 통합|네임스페이스와 통합되지 않음|마운트 네임스페이스와 완전히 통합|네임스페이스와 직접적 통합 없음|
|파일시스템 요구사항|특별한 요구사항 없음|새 루트는 마운트 포인트여야 함|새 루트는 마운트 포인트여야 함|
|메모리 사용|변경 없음|변경 없음|이전 루트 메모리 해제|
|사용 예시|chroot /new-root|pivot_root /new-root /new-root/old-root|switch_root /new-root /sbin/init|


# 기술별 매커니즘

|기술/시스템|사용하는 메커니즘|비고|
|--------|-------------|---|
|Docker|pivot_root|초기에는 chroot 사용, 보안 강화를 위해 pivot_root로 전환|
|Podman|pivot_root|--no-pivot 옵션으로 chroot 사용 가능|
|LXC/LXD|pivot_root|컨테이너 격리를 위해 사용|
|containerd/runc|pivot_root|OCI 표준 컨테이너 런타임|
|initrd|pivot_root|실제 파일 시스템으로 로드되어 pivot_root 사용 가능|
|initramfs|switch_root|tmpfs 위에 압축 해제되어 pivot_root 사용 불가|
|dracut|switch_root|현대 리눅스 배포판의 initramfs 생성 도구|
|systemd-boot|switch_root|systemd 기반 초기 부팅 환경|