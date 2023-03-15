## EC2

### Instances
1. `Running` 상태인 인스턴스들의 인스턴스 ID만 찾기
    ```s
    aws ec2 describe-instances \
    --filters Name=instance-state-name,Values=running \
    --query "Reservations[*].Instances[*].InstanceId" --output text
    ```
 2. 인스턴스 Name에 'db'가 들어가는 인스턴스의 Volume Size 찾기
    ```s
    aws ec2 describe-instances \
    --filters Name=tag:Name,Values="*db*" \
    --query "Reservations[*].Instances[*].BlockDeviceMappings[*].Ebs.VolumeId" --output json \
    | jq '.[][][]' \
    | xargs -I{} aws ec2 --region ap-southeast-1 describe-volumes --filters Name=volume-id,Values={} --query "Volumes[*].Size" \
    | jq '.[]'
    ```
3. EC2 Name tag에 db가 포함되는 인스턴스 ID 가져오기
    ```s
    aws ec2 describe-instances \
    --filters Name=tag:Name,Values="*db*" \
    --query "Reservations[*].Instances[*].InstanceId"
    ```

### Image and snapshots
1. 2022-01-01 ~ 2022-12-31 기간에 생성된 EBS Volume snapshot 찾기
    ```s
    aws ec2 describe-snapshots \
    --filters Name=owner-id,Values=123456789012 \
    --query "Snapshots[?(StartTime>='2022-01-01') && (StartTime<='2022-12-31')].[SnapshotId]" --output text
    ```
 2. 타 계정에 공유된 EBS Snapshot중 볼륨 생성 권한도 공유된 Snapshot 찾기
    ```s
    aws ec2 describe-snapshots --owner-ids 12345678 --region ap-northeast-2 \
    | awk -F '"' '/SnapshotId/ {print $4}' \
    | xargs -I{} aws ec2 describe-snapshot-attribute --attribute createVolumePermission --snapshot-id {} --region ap-northeast-2 \
    | grep -vF '"CreateVolumePermissions": []'
    ```
 3. 타 계정에 공유된 AMI Image중 타 계정에서 인스턴스 실행 권한을 가지고 있는 Image만 찾기
    ```s
    aws ec2 describe-images --owners 12345678 --region ap-southeast-1 \
    | awk -F '"'  '/ImageId/ {print $4}' \
    | xargs -I{} aws ec2 describe-image-attribute --attribute launchPermission --image-id {} --region ap-southeast-1 \
    | grep -vF '"LaunchPermissions": []'
    ```
 4. 현재 attached된(in-use상태인) EBS Volume들의 Size 보기
    ```s
    aws ec2 --region ap-southeast-1 describe-volumes \
    --filters Name=attachment.status,Values=attached \
    --query "Volumes[*].Size" \
    | grep -E "[0-9]" |  sed -e 's/^[ \t]*//'
    ```
 5. AMI Image이름 중 'DLM'이 존재하는 Image ID와 SnapshotID 찾기
    ```s
    aws ec2 describe-images --region ap-northeast-2 --owners 12345678 \
    --query "Images[?contains(Name, 'DLM')].{Id:ImageId,EBS:BlockDeviceMappings}" \
    | grep -E 'Id|SnapshotId'
    ```
 6. . EC2 Name tag에 db가 포함되는 모든 인스턴스의 AMI 생성하기
    ```s
    aws ec2 describe-instances --filters Name=tag:Name,Values="*db*" --query "Reservations[*].Instances[*].InstanceId" \
    | jq ".[][]" \
    | xargs -I{} aws ec2 create-image --instance-id {} --no-reboot --name {}
    ```

## S3
1. `~/test/` 디렉터리의 txt파일만 전부 s3://my-bucket/test/ 에 업로드 하기
    ```s
    aws s3 cp ~/test/ s3://my-bucket/test/ \
    --recursive --exclude "*" --include "*.txt"
    ```
