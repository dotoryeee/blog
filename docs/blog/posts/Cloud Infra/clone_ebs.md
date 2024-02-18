---
draft: false
date: 2024-02-18
authors:
  - dotoryeee
categories:
  - AWS
---
# rsync로 EBS 복제하는 방법

rsync로 EBS -> EBS 복제할 일이 생겨서 절차를 중요한 절차만 요약하였습니다.<br>
볼륨 용량 줄이기, File System변경 등에 사용할 수 있습니다.

<!-- more -->

1. AWS에서 EC2생성 시 동시에 여러개의 EBS를 부착할 수 있는데, 이때 생성과 동시에 Tag를 붙일 수 없기 때문에 별도 작업이나 기록을 해놓지 않으면 추후 어떤 EBS ID가 어떤 볼륨으로 사용했던 것인지 알기 쉽지 않다.
![create ebs when start ec2](./clone_ebs/Screenshot%202024-02-18%20at%2010.37.07.png)
2. 따라서 EC2 접속 후 아래 명령어를 사용해 현재 부착된 볼륨의 AWS EBS Volume ID를 조회한다.
```bash
lsblk -o +SERIAL
```
![](./clone_ebs/Screenshot%202024-02-18%20at%2015.55.12.png)
3. 볼륨 복제를 관장할 신규 인스턴스 생성 후 기존 볼륨을 ~/old에, 신규 볼륨을 ~/new에 마운트 한다.
4. rsync명령어를 사용해 ~/old내용을 ~/new로 전부 복사한다. 이때 axcHAWS, numeric-ids옵션을 반드시 넣어줘야 사용자와 권한등 정보를 수정하지 않고 정확하게 복사한다. 또한 rsync 명령 시 ~/old뒤에 /를 넣어줘야 ~/new/old/ 로 복사되는 일을 방지할 수 있다.
```bash
rsync -axcHAWS --numeric-ids --info=progress2 ~/old/ ~/new
```
   