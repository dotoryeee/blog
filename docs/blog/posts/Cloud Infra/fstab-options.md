---
draft: false
date: 2025-03-11
authors:
  - dotoryeee
categories:
  - Cloud
  - Server
---
# Linux Storage 마운트 옵션

<!-- more -->

# `/etc/fstab`에서 EBS, EFS, Swap 마운트 옵션

###  EBS 마운트 예시 (`/etc/fstab`)
```fstab
/dev/xvdf /mnt/data ext4 defaults,noatime,nodiratime 0 2
```

###  EBS 마운트 옵션 설명
| 옵션 | 설명 |
|------|------|
| `defaults` | 기본 마운트 옵션 (`rw, suid, dev, exec, auto, nouser, async`) 포함 |
| `noatime` | 파일의 접근 시간(`atime`)을 기록하지 않아 성능 향상 |
| `nodiratime` | 디렉터리의 접근 시간(`diratime`)을 기록하지 않음 |
| `nofail` | 부팅 시 마운트 오류가 발생해도 시스템이 부팅됨 |
| `x-systemd.device-timeout=0` | 부팅 시 EBS 볼륨이 연결될 때까지 기다리지 않도록 설정 |
| `discard` | SSD의 TRIM 기능을 활성화하여 성능 최적화 |

---

## EFS 마운트 (`/etc/fstab` 설정 및 옵션)
EFS(Amazon Elastic File System)는 네트워크 파일 스토리지(NFS 기반) 로, 다중 EC2 인스턴스에서 동시에 접근할 수 있습니다.

### EFS 마운트 예시 (`/etc/fstab`)
```fstab
fs-12345678.efs.us-east-1.amazonaws.com:/ /mnt/efs nfs4 defaults,_netdev,noresvport 0 0
```

### EFS 마운트 옵션 설명
| 옵션 | 설명 |
|------|------|
| `defaults` | 기본 마운트 옵션 적용 |
| `_netdev` | 네트워크 장치를 필요로 하는 파일 시스템으로 설정 (부팅 시 네트워크 활성화 후 마운트) |
| `noresvport` | EFS 마운트 시 임시 포트를 사용하여 다중 연결 문제 방지 |
| `vers=4.1` | NFS 버전 4.1을 사용하여 성능 최적화 (기본값은 4.1이므로 생략 가능) |
| `rsize=1048576,wsize=1048576` | 읽기/쓰기 크기를 1MB로 조정하여 성능 최적화 |
| `hard` | 클라이언트가 응답을 받을 때까지 지속적으로 재시도 |
| `timeo=600` | NFS 서버 응답 대기 시간을 60초로 설정 |
| `retrans=2` | 요청 실패 시 최대 2번 재시도 |

---

## Swap 마운트 (`/etc/fstab` 설정 및 옵션)
Swap 공간은 메모리 부족 시 디스크를 가상 메모리로 활용하기 위한 공간입니다.

### Swap 마운트 예시 (`/etc/fstab`)
```fstab
/dev/xvds swap swap defaults 0 0
```

### Swap 마운트 옵션 설명
| 옵션 | 설명 |
|------|------|
| `defaults` | 기본 마운트 옵션 적용 (보통 Swap에는 특별한 옵션이 필요하지 않음) |
| `nofail` | 부팅 시 Swap 파티션이 없더라도 시스템이 정상 부팅됨 |
| `pri=100` | Swap 우선순위를 설정 (값이 높을수록 우선 사용) |

---

## EBS, EFS, Swap 옵션 비교

| 옵션 | EBS (ext4, xfs) | EFS (NFS) | Swap |
|------|----------------|-----------|------|
| `defaults` |  사용 |  사용 |  사용 |
| `noatime` |  사용 (성능 최적화) |  사용 안 함 |  사용 안 함 |
| `nodiratime` |  사용 (디렉터리 성능 최적화) |  사용 안 함 |  사용 안 함 |
| `nofail` |  사용 가능 |  사용 가능 |  사용 가능 |
| `_netdev` |  불필요 |  네트워크 스토리지에 필요 |  불필요 |
| `noresvport` |  불필요 |  사용 권장 |  불필요 |
| `discard` |  SSD 최적화 (TRIM 지원) |  사용 안 함 |  사용 안 함 |
| `rsize,wsize` |  불필요 |  읽기/쓰기 성능 최적화 |  불필요 |
| `hard` |  불필요 |  NFS 연결 보장 |  불필요 |
| `pri` |  불필요 |  불필요 |  Swap 우선순위 설정 |

---

## 요약
- EBS: 블록 스토리지이므로 `noatime`, `nodiratime`, `discard` 옵션을 활용하여 성능 최적화 가능.
- EFS: 네트워크 파일 시스템이므로 `_netdev`, `noresvport` 같은 네트워크 관련 옵션이 필요.
- Swap: 특수한 마운트 옵션이 필요하지 않지만, `nofail` 및 `pri` 옵션을 조정 가능.

