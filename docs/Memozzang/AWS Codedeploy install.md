```s
sudo apt update && sudo apt install -y ruby-full wget

cd ~/work
wget https://aws-codedeploy-cn-north-1.s3.cn-north-1.amazonaws.com.cn/latest/install
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



wget https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install
```