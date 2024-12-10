1. 23-01-01 ~ 23-01-13 사이에 생성된 *.log 파일 tar 압축하기
    ```s
    sudo find ./ -name "*.log" -type f \
    -newerat 2023-01-01 ! -newerat 2023-02-01 \
    -exec tar rf 202301.tar {} \;```
    ```
2. systemd에 등록된 consul 데몬 로그 확인
    ```s
    sudo journalctl -u consul.service -r
    ```
3. install AWS CodeDeploy agent<br>
   CodeDeploy endpoint 사용 시 enable_auth_policy설정이 필요하므로 Codedeploy agent 설치 후 config 수정 -> agent restart가 필요합니다
    ```s
    sudo apt update && sudo apt install -y ruby-full wget

    cd ~/work
    wget https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install
    chmod +x ./install 
    sudo ./install auto

    rm -rf ~/work/install
    sudo systemctl stop codedeploy-agent

    sudo sh -c "cat<<EOF > /etc/codedeploy-agent/conf/codedeployagent.yml
    ---
    :log_aws_wire: false
    :log_dir: '/var/log/aws/codedeploy-agent/'
    :pid_dir: '/opt/codedeploy-agent/state/.pid/'
    :program_name: codedeploy-agent
    :root_dir: '/opt/codedeploy-agent/deployment-root'
    :verbose: false
    :wait_between_runs: 1
    :proxy_uri:
    :max_revisions: 2
    :enable_auth_policy: true
    EOF"

    sudo systemctl restart codedeploy-agent.service
    ```
4. git branch 분기 확인
    ```s
    git log --all --decorate --oneline --graph
    ```

5. Logstash 처리량 확인
    ```s
    curl localhost:9600/_node/stats/pipelines | jq '.pipelines[].events'
    ```

6. 한글 Windows에서 압축한 파일 Mac OS에서 압축풀기(Illegal byte sequence 에러 발생 시)
    ```s
    mkdir ./unzip_files
    for f in *.zip; do ditto -Vxk --sequesterRsrc --rsrc $f ./unzip_files; done
    ```

7. 모든 Python library upgrade 하기
    ```s
    pip list --outdated | awk '{ print $1 }' | xarge -I{} pip3 install --upgrade {}
    ```
8. exit 0으로 종료될 때 까지 max_attempts만큼 command 실행하기
    ```bash
    #!/bin/bash

    # maximum number of attempts
    max_attempts=5

    # counter for the attempts
    count=0

    while [ $count -le $max_attempts ]
    do
    
    <command here>
    
    # Check if command was successful (exit status 0)
    if [ $? -eq 0 ]
    then
        echo "Command executed successfully"
        exit 0
    else
        echo "Attempt $count Failed. Trying again in 5 seconds..."
        count=$((count+1))
        sleep 5
    fi
    done

    echo "Command failed after $max_attempts attempts."
    exit 1
    ```
9. EFS연결을 위한 NFS utils 패키지 빌드 및 오프라인 설치
    ```bash title="@Bastion"
    sudo yum -y install git make rpm-build
    mkdir ~/efs-utils-pkg; cd ~/efs-utils-pkg
    sudo dnf download --resolve nfs-utils
    git clone https://github.com/aws/efs-utils; cd efs-utils
    sudo make rpm
    sudo cp -av /home/ec2-user/efs-utils-pkg/efs-utils/build/amazon-efs-utils-*.rpm ~/efs-utils-pkg; cd ~/efs-utils-pkg
    tar -cvf ~/efs-utils-pkg.tar *.rpm
    scp -i ~/test.pem ~/efs-utils-pkg.tar ec2-user@10.0.1.97:/home/ec2-user/
    ```

    ```bash title="@Install Target Server(No Internet Server)"
    tar -xvf efs-utils-pkg.tar
    sudo rpm -ivh --nodeps ./*rpm
    sudo mkdir /efs
    sudo mount -t nfs -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport 	172.31.13.181:/ /efs
    ```
10. 모든 명령 실행 결과 마지막에 개행 추가하기
    ```bash
    export PS1="\n[\u@\h \W] $ "
    ```