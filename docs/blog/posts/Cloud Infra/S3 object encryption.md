---
draft: false
date: 2021-05-01
authors:
  - dotoryeee
categories:
  - AWS
---
# S3 object encryption

1. 2023년 1월 5일 이후 업로드 되는 모든 오브젝트는 자동으로 암호화된다(SSE-S3) [관련정보](https://aws.amazon.com/ko/about-aws/whats-new/2023/01/amazon-s3-automatically-encrypts-new-objects/)
2. S3 암호화 방식은 총 3가지가 존재한다
    - SSE-S3 (Server-Side Encryption with Amazon S3): AWS에서 키를 관리한다. 암호화 키 소유권은 AWS S3에 있다.
    - SSE-C (Server-Side Encryption with Customer-Provided Keys): 고객이 제공하는 암호화 키를 사용해 데이터를 암호화 한다. 암호화키는 암호화 및 복호와에 모두 사용된다(대칭키)
    - SSE-KMS (Server-Side Encryption with AWS Key Management Service): KMS 마스터키는 AWS KMS 서비스에서 관리된다. 암호화 키의 소유권이 고객에게 있다.
3. 암호화 방식에 따라 오브젝트 업로드 명령 옵션이 상이하다
    - SSE-S3 (default)<br>
    ```bash
    aws s3 cp <object> s3://<bucket>/<key>
    ```
    - SSE-C<br>
    ```bash
    aws s3 cp <object> s3://<bucket>/<key> --sse-c-key <encryption-key>
    ```
    - SSE-KMS<br>
    ```bash
    aws s3 cp <object> s3://<bucket>/<key> --sse aws:kms --sse-kms-key-id
    ```
<!-- more -->
4. SSE-KMS를 이용해 오브젝트 up/download 하는 python code 예시
    - Upload
    ```py title="upload_s3_with_kms.py"
    import boto3

    # KMS KEY ID
    kms_key_id = "kms-key-id"

    # 암호화할 파일의 경로
    file_name = "./file.txt"

    # S3 버킷 정보
    bucket_name = "bucket-name"
    object_key = "file.txt"

    # Boto3 S3 클라이언트 생성
    s3_client = boto3.client('s3')

    # 암호화 헤더 생성
    encryption_header = {
        'ServerSideEncryption': 'aws:kms',
        'SSEKMSKeyId': kms_key_id
    }

    # 파일 업로드
    with open(file_name, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key, ExtraArgs=encryption_header)
    ```
    
    - Download
    ```py title="download_s3_with_kms.py"
    import boto3

    # KMS KEY ID
    kms_key_id = "kms-key-id"

    # 복호화할 S3 객체 정보
    bucket_name = "your-bucket-name"
    object_key = "file.txt"

    # 로컬에 저장할 파일 경로
    output_file_path = "./file.txt"

    # Boto3 S3 클라이언트 생성
    s3_client = boto3.client('s3')

    # 복호화 헤더 생성
    decryption_header = {
        'x-amz-server-side-encryption-customer-algorithm': 'AES256',
        'x-amz-server-side-encryption-customer-key': '',
        'x-amz-server-side-encryption-customer-key-MD5': ''
    }

    # S3 객체 다운로드 및 복호화하여 로컬에 저장
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    encryption_key = response['ServerSideEncryptionCustomerKey']
    encryption_key_md5 = response['ServerSideEncryptionCustomerKeyMD5']

    decryption_header['x-amz-server-side-encryption-customer-key'] = encryption_key
    decryption_header['x-amz-server-side-encryption-customer-key-MD5'] = encryption_key_md5

    with open(output_file_path, 'wb') as file:
        file.write(response['Body'].read())
    ```

