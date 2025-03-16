---
draft: false
date: 2025-03-16
authors:
  - dotoryeee
categories:
  - Server
---
# 현대 리눅스 시스템 부팅 순서(메모)

<!-- more -->

최신 시스템(MBR x / initrd x / init x / GRUB 1 x) 전제

power on -> uefi 시작 > gpt의 esp에서 GRUB 2 로드> grub.cfg읽기  > vmlinuz 커널 이미지 로드 > initramfs 로드 > 커널 시작(dmesg로 확인할 수 있는 커널 로그 생성 시작) > swapper(pid 0) 시작 > 커널 링 영역 생성 > 시스템 로드를 위한 램디스크 생성 > initramfs내 init 스크립트 시작 > 루트 파일시스템 마운트(/etc/fstab을 읽지 않고 직접 UUID 읽고 R/O로 마운트) > switch_root로 루트 전환 > systemd(pid 1) 시작 > /etc/fstab읽고 파일시스템을 R/W로 재마운트 > target에 의한 서비스 데몬을 의존성에 따라 병렬 시작
