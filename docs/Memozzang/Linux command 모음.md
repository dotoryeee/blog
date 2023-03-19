## tar

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
4. 