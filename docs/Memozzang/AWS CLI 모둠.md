1. 
    ```s
    aws ec2 describe-snapshots --filters Name=owner-id,Values=123456789012 --query "Snapshots[?(StartTime>='2019-01-01') && (StartTime<='2019-12-31')].[SnapshotId]" --output text
    ```
2. 
    ```s
    aws ec2 describe-instances --filters Name=instance-state-name,Values=running --query "Reservations[*].Instances[*].InstanceId" --output text
    ```
3. 
    ```s
    aws ec2 describe-snapshots --owner-ids self --region ap-northeast-2 | awk -F '"' '/SnapshotId/ {print $4}' | xargs -I{} aws ec2 describe-snapshot-attribute --attribute createVolumePermission --snapshot-id {} --region ap-northeast-2 | grep -vF '"CreateVolumePermissions": []'
    ```
3. 
    ```s
    aws ec2 describe-images --owners self --region ap-southeast-1 | awk -F '"'  '/ImageId/ {print $4}' | xargs -I{} aws ec2 describe-image-attribute --attribute launchPermission --image-id {} --region ap-southeast-1 | grep -vF '"LaunchPermissions": []'
    ```
4. 
    ```s
    aws ec2 describe-instances --filters Name=tag:Name,Values="*db*" --query "Reservations[*].Instances[*].BlockDeviceMappings[*].Ebs.VolumeId" --output json | jq '.[][][]' | xargs -I{} aws ec2 --region ap-southeast-1 describe-volumes --filters Name=volume-id,Values={} --query "Volumes[*].Size" | jq '.[]'
    ```
5. 
    ```s
    aws ec2 --region ap-southeast-1 describe-volumes --filters Name=attachment.status,Values=attached --query "Volumes[*].Size" | grep -E "[0-9]" |  sed -e 's/^[ \t]*//'
    ```
6. 
    ```s
    aws ec2 describe-images --region ap-northeast-2 --owners self --query "Images[?contains(Name, 'DLM')].{Id:ImageId,EBS:BlockDeviceMappings}" | grep -E 'Id|SnapshotId'
    ```