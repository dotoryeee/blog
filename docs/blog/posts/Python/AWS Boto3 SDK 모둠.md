---
draft: false
date: 1993-09-17
authors:
  - dotoryeee
categories:
  - Python
---
# Boto3 사용 예시
1. 인스턴스 타입 변경
    ```python title="change_instance_type.py" linenums="1"
    ##############################################
    TARGET_INSTANCE_IDs = ["i-0351fd54bd47a17db"]
    TARGET_INSTANCE_TYPE = "t2.nano"
    ##############################################

    import boto3

    ec2 = boto3.client("ec2")

    def stop_instance(instance_id):
        try:
            ec2.stop_instances(InstanceIds=[instance_id])
            print(f"trying to STOP INSTANCE {instance_id}...", end="")
            waiter = ec2.get_waiter("instance_stopped")
            waiter.wait(InstanceIds=[instance_id])
            print(f"SUCCESS")
            return True  # 인스턴스 정지 성공
        except:
            print(f"FAILED : STOP INSTANCE {instance_id}")
            return False


    def modify_instance_type(instance_id):
        try:
            ec2.modify_instance_attribute(
                InstanceId=instance_id, Attribute="instanceType", Value=TARGET_INSTANCE_TYPE
            )
            print(f"SUCCESS : {instance_id} INSTANCE CHANGED TO {TARGET_INSTANCE_TYPE}")
        except:
            print(f"FAILED : CHANGE {instance_id} INSTANCE TYPE")


    def start_instance(instance_id):
        try:
            ec2.start_instances(InstanceIds=[instance_id])
            print(f"SUCCESS : RESTART {instance_id}")
        except:
            print(f"FAILED : START INSTANCE {instance_id}")


    def main():
        for instance_id in TARGET_INSTANCE_IDs:
            is_stopped = stop_instance(instance_id)  # is_stopped는 인스턴스 정지 성공 유무 표시용
            if is_stopped:
                modify_instance_type(instance_id)
                start_instance(instance_id)


    main()
    ```
2. Target group deregister후 instance stop하기
    ```py
    import boto3
    from botocore.exceptions import ClientError

    TARGET_INSTANCE_IDs = ["i-0f8e23d613b7d62f0"]
    TARGET_GROUP_ARN = "arn:aws:elasticloadbalancing:ap-northeast-2:737382971423:targetgroup/testTG/36174c22e12f595e"

    elb = boto3.client("elbv2")
    ec2 = boto3.client("ec2")


    def detach_instance(TGarn, instance_id):
        try:
            response = elb.deregister_targets(
                TargetGroupArn=TGarn, 
                Targets=[{"Id": instance_id}], 
            )
            print(response)
            return response
        except:
            raise Exception("ERROR : FAIL TO DETACH INSTANCE FORM TARGET GROUP")


    def stop_instance(instance_id):
        try:
            response = ec2.stop_instances(InstanceIds=instance_id, DryRun=False)
            print(f"STOP SUCCESS : {response}")
        except ClientError as e:
            print(f"ERROR : {e}")


    def main():
        for instance in TARGET_INSTANCE_IDs:
            detach_instance(TARGET_GROUP_ARN, instance)
        stop_instance(TARGET_INSTANCE_IDs)
    ```
3. AMI해제 후 연관 snapshot 삭제
    ```py title="remove_ami_and_snapshots.py" linenums="1"
    import boto3

    DRYRUN = False
    target_region = 'ap-southeast-1'
    target_ami_ids = [
                #AMI IDs
            ]

    ec2 = boto3.client('ec2', region_name=target_region)
    images = ec2.describe_images(ImageIds=target_ami_ids)

    def remove_snapshots(snapshot_ids):
        for snapshot_id in snapshot_ids:
            try:
                print('|remove', snapshot_id, end=':')
                ec2.delete_snapshot(SnapshotId=snapshot_id, DryRun=DRYRUN)
                print('success', end='')
            except:
                print('fail')
        print()

    for target_image in images['Images']:
        print('remove ',target_image['ImageId'], end=':')
        try:
            ec2.deregister_image(ImageId=target_image['ImageId'], DryRun=DRYRUN)
            print('success', end='')
            snapshot_ids=[]
            for block_devices in target_image['BlockDeviceMappings']:
                try: #AMI 삭제 성공 시 Snapshot 제거 대상 리스트에 append
                    snapshot_ids.append(block_devices['Ebs']['SnapshotId'])
                except:
                    pass
            remove_snapshots(snapshot_ids)
        except:
            print('fail')
    ```
4. 

