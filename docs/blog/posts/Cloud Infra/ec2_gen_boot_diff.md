---
draft: false
date: 2025-03-10
authors:
  - dotoryeee
categories:
  - Cloud
  - Server
---
# 서버 부팅 방식 정리

<!-- more -->



## 각 용어의 개념

### MBR (Master Boot Record)
- 역할: 디스크의 첫 번째 512바이트에 위치하는 데이터 구조로, 부트 로더 및 파티션 정보를 저장함.
- 왜 사용하는가?
  - 오래된 BIOS 기반 시스템에서 부팅을 지원하기 위해 사용됨.
  - 부트 로더(예: GRUB)의 첫 번째 스테이지(Stage 1)를 저장하여 운영체제 로딩을 시작할 수 있도록 함.
  - 단순한 구조이지만, 최대 2TiB 크기까지만 지원하고, 최대 4개의 기본(primary) 파티션만 가질 수 있음.

---

### GPT (GUID Partition Table)
- 역할: 최신 디스크 파티션 테이블 형식으로, MBR보다 많은 파티션과 더 큰 디스크 크기를 지원함.
- 왜 사용하는가?
  - MBR의 2TiB 한계를 해결하여 대형 디스크(2TiB 이상)를 지원함.
  - 최대 128개의 파티션을 만들 수 있음.
  - 디스크 무결성을 위해 CRC32 체크섬을 사용하며, 복구 기능을 제공함.
  - UEFI 부팅을 지원하는 최신 시스템에서 필수적으로 사용됨.

---

### UEFI (Unified Extensible Firmware Interface)
- 역할: BIOS를 대체하는 최신 펌웨어 인터페이스로, 운영체제와 하드웨어 간의 연결을 제공함.
- 왜 사용하는가?
  - 기존 BIOS보다 빠르고 더 많은 기능을 지원하며, 보안 기능(예: Secure Boot)을 포함함.
  - GPT와 함께 사용하여, MBR의 2TiB 제한을 극복하고 더 많은 파티션을 지원함.
  - 네트워크 부팅, 고해상도 GUI 인터페이스 제공 등 추가적인 기능을 제공함.

---

### GRUB (GRand Unified Bootloader)
- 역할: 운영체제를 로드하는 부트 로더.
- 왜 사용하는가?
  - 여러 운영체제를 지원하는 멀티 부트 기능 제공.
  - MBR 또는 GPT에서 커널을 로드할 수 있도록 설계됨.
  - BIOS 기반 부팅에서는 MBR의 Stage 1에 설치됨.
  - UEFI 기반 부팅에서는 ESP 파티션(`/boot/efi`)에 `grubx64.efi` 형식으로 설치됨.

---

### ESP (EFI System Partition)
- 역할: UEFI 기반 시스템에서 부트 로더 및 부팅 관련 데이터를 저장하는 FAT32 파티션.
- 왜 사용하는가?
  - UEFI 부팅을 위해 필수적인 공간으로, 여기서 GRUB 또는 다른 EFI 부트 로더가 실행됨.
  - 일반적으로 `/boot/efi`에 마운트됨.
  - `EFI/BOOT/BOOTX64.EFI`와 같은 실행 가능한 EFI 파일이 포함됨.

---

## /boot 및 /boot/efi 필요성
| 부트 방식 | `/boot` 필요 여부 | `/boot/efi` 필요 여부 | 설명 |
|----------|-----------------|------------------|------------------|
| BIOS + MBR | ✅ 필요 | ❌ 필요 없음 | GRUB이 MBR에 설치되고, `/boot`에서 커널을 로드 |
| UEFI + GPT | ✅ 필요 | ✅ 필요 | GRUB이 `/boot/efi`의 ESP에서 실행되고, 커널을 `/boot`에서 로드 |
| AWS Nitro 기반 (x86) | ✅ 필요 | ❌ 필요 없음 | AWS 가상화 환경에서는 `/boot/efi` 없이도 부팅 가능 |
| AWS Xen 기반 (t2 등 구형) | ✅ 필요 | ❌ 필요 없음 | MBR 기반 BIOS 부팅 사용 |

---

## 3. AWS EC2 인스턴스에서 /boot/efi가 필요 없는 이유
### AWS Xen 기반 (예: t2, m4)
- Xen 하이퍼바이저는 기본적으로 BIOS 부팅 방식을 사용하며, `/boot/efi`가 필요 없음.
- AWS에서 제공하는 기본 AMI(Amazon Machine Image)는 MBR 기반이 많음.
- GRUB이 MBR에 설치되며, `/boot`에서 커널을 로드하여 부팅.

### AWS Nitro 기반 (예: m5, m6i, m7i, t4g, a1)
- Nitro 기반 인스턴스는 UEFI 부팅을 지원하지만, AWS AMI 기본 설정은 BIOS + MBR 부팅을 사용.
- `/boot/efi` 없이도 부팅 가능하도록 구성됨.
- Amazon Linux 2, Ubuntu 20.04, RHEL 8 등의 AMI는 기본적으로 MBR 부팅을 유지.

### AWS Nitro 기반에서 UEFI 부팅이 필요한 경우
- 일부 최신 OS(Amazon Linux 2023 등)는 UEFI-preferred 설정이 되어 있으며, ESP(`/boot/efi`)를 사용.
- Nitro 기반 인스턴스에서 UEFI 모드를 활성화하면 GPT 및 `/boot/efi`를 사용하여 부팅 가능.
- 그러나 대부분의 리눅스 AMI는 여전히 MBR 기반 BIOS 부팅을 기본값으로 사용.

## AWS EC2 인스턴스 세대 및 OS별 부팅 방식
| 인스턴스 유형 및 OS             | ESP 사용 | 파티션 타입 | 부팅 방식       | 비고                          |
|--------------------------------|---------|-------------|-----------------|-------------------------------|
| t2, m4 (Xen기반) - Ubuntu, AL2, RHEL8/9 | ❌       | MBR         | BIOS            | GRUB(MBR)로 부팅              |
| m5, m6i, m7i (Nitro 기반, x86) - Ubuntu, AL2, RHEL8/9 | ❌       | MBR         | BIOS(기본값)    | UEFI 지원하지만 기본 MBR/BIOS |
| m5, m6i, m7i - Amazon Linux 2023 | ✅       | GPT         | UEFI            | UEFI-preferred, ESP 존재      |
| a1, t4g, m6g (Nitro, ARM Graviton) | ✅       | GPT         | UEFI            | ARM 환경은 UEFI만 지원        |


---

## 결론
- MBR은 BIOS 부팅에서 사용되며, 2TiB 이하의 디스크에서 유효함.
- GPT는 UEFI 부팅에 필수적이며, 대형 디스크 및 보안 기능을 지원함.
- GRUB은 MBR 또는 UEFI 환경에서 동작할 수 있음.
- ESP(`/boot/efi`)는 UEFI 부팅에서 필수이며, AWS Nitro 기반에서는 일반적으로 사용되지 않음.
- AWS EC2 인스턴스에서는 대부분 MBR 기반 부팅을 사용하여 `/boot/efi` 없이도 정상 작동함.



---
