# Project - 1

!!! tip
    ๐ก ์ ํ : ๊ฐ์ธ ํ ์ด ํ๋ก์ ํธ

## ๋ชฉํ

---

- ์ฌํ ํ์ตํด์๋ ๊ฐ์ข ๊ธฐ์ ๋ค์ ์ค์ ๋ก ํ์ฉํด๋ณธ ๊ฒฝํ์ ๊ฐ์ ธ๋ณด๊ณ  ๋ฌธ์ ํด๊ฒฐ ๋ฅ๋ ฅ์ ํค์ฐ๊ธฐ ์ํด ์ค์  ์ด์์ด ๊ฐ๋ฅํ ์ธํ๋ผ๋ฅผ ๊ตฌ์ถํด๋ณด๊ณ  ์ถ์์ต๋๋ค

## ์๋น์ค ์์ฝ

---

- ์ธ๋ ฅํ์ ์ง์์๋ฅผ ๋ฑ๋กํ  ์ ์๋ ๊ฐ๋จํ ์๋น์ค๋ฅผ ๋์ปค๋ฅผ ํ์ฉํ ๋ฉํฐ์ปจํ์ด๋ ์ธํ๋ผ๋ฅผ ์ ์ฉํ์ฌ ๊ตฌ์ฑํ์์ต๋๋ค

## ๊ตฌ์ฑ๋

---

- Service Flow
    
    ![Project-1/Untitled.png](Project-1/Untitled.png)
    
- DEV Flow
    
    ![Project-1/Untitled%201.png](Project-1/Untitled%201.png)
    
- AWS ์ธํ๋ผ ๊ตฌ์ฑ๋
    
    ![Project-1/Untitled%202.png](Project-1/Untitled%202.png)
    

## ๊ฐ ๊ธฐ์ ๋ค์ ์ ํ ์ด์ 

---

- ๋ณธ ํ๋ก์ ํธ๋ ์๋น์ค๊ฐ ์ํํ๊ฒ ๋์ํ  ์ ์๋ ์ธํ๋ผ๋ฅผ ๊ตฌ์ฑํ๋๋ฐ ์ค์ ์ ๋๊ณ ์์ต๋๋ค. ํ๋ก๊ทธ๋๋ฐ์ ์ต์ํ ํ๊ธฐ ์ํด ์ ๋ค๋ฃฐ ์ ์๋ ์ธ์ด์ธ Python์ ์ฌ์ฉํ๊ณ ,  ๋น ๋ฅด๊ฒ ์น ์๋น์ค๋ฅผ ๊ตฌ๋ํ  ์ ์๋ Flask ํ๋ ์์ํฌ๋ฅผ ์ด์ฉํ์ต๋๋ค.
- CICD ์๋ฃจ์์ผ๋ก Cloudbase + public repository ๋ฌด๋ฃ + multi container ์ฌ์ฉ๊ฐ๋ฅ ์กฐ๊ฑด์ ๋ง์ถฐ์ค ์ ์๋ Travis CI๋ฅผ ์ฑํํ์์ต๋๋ค
[https://djangostars.com/blog/continuous-integration-circleci-vs-travisci-vs-jenkins/](https://djangostars.com/blog/continuous-integration-circleci-vs-travisci-vs-jenkins/)
- Apache์ Nginx์ค ๋น๋๊ธฐ๋ฅผ ์ด์ฉํด ๋ง์ ๋์์ ์ ํธ๋ํฝ์ด ์์ฉ๊ฐ๋ฅํ Nginx๋ฅผ ์ ํํ์์ต๋๋ค [https://kinsta.com/blog/nginx-vs-apache/](https://kinsta.com/blog/nginx-vs-apache/)
- Flask์ ๊ธฐ๋ณธ ๋ด์ฅ์๋ฒ๋ ๋์ฉ๋์ฒ๋ฆฌ์ ๋ถ์ ํฉํ๊ธฐ ๋๋ฌธ์ WSGI๋ฅผ ์ ์ฉํ์ต๋๋ค
    
    ![Project-1/Untitled%203.png](Project-1/Untitled%203.png)
    
- WSGI๊ตฌํ์ gunicorn์ ์ฌ์ฉํ์์ต๋๋ค
- DB์์ฑ ํ ์คํค๋ง๋ฅผ ๋ณ๊ฒฝํ  ์ผ์ด ์๊ธฐ ๋๋ฌธ์ SQL์ ์ฌ์ฉํ๋๋ฐ, ์ถํ RDS๋ก ๋ง์ด๊ทธ๋ ์ด์๋ ๊ฐ๋ฅํ MySQL์ ์ฌ์ฉํ์์ต๋๋ค
- ๋ฉํฐ์ปจํ์ด๋์ฉ Beanstalk๋ณด๋จ ์ถํ ์ปค์คํ์ด ์์ ๋ก์ด EC2 ์๋น์ค๋ฅผ ์ ํํ์์ต๋๋ค
- fault tolerance์๊ณ ๋ฆฌ์ฆ์ ์ํด EC2 ์ธ์คํด์ค ์๋ ํ์๋ก ๊ตฌ์ฑํ์์ต๋๋ค
[https://docs.docker.com/engine/swarm/admin_guide/](https://docs.docker.com/engine/swarm/admin_guide/)

## ์๋ฌ ์์  ๊ธฐ๋ก

---

- Docker์์ Flask ์๋ฒ๋ฅผ ๋์ธ ๋ Host์ฃผ์๋ 0.0.0.0
- wsgi์ฉ ํ์ด์ฌ ํ์ผ์ ๋ณ๋๋ก ๋ถ๋ฆฌํ๊ณ  ํฌํธ ํ ๋นํ๊ธฐ
- ์ต์  uWSGI๋ [musl](https://en.wikipedia.org/wiki/Musl)์ ์ฌ์ฉํ๊ธฐ ๋๋ฌธ์ [https://stackoverflow.com/questions/36217250/cannot-install-uwsgi-on-alpine](https://stackoverflow.com/questions/36217250/cannot-install-uwsgi-on-alpine)
[https://github.com/gliderlabs/docker-alpine/issues/158](https://github.com/gliderlabs/docker-alpine/issues/158)
RUN apk add python3-dev build-base linux-headers pcre-dev ๋ช๋ น์ ์ถ๊ฐํฉ๋๋ค
- ์ด์ ์์ด ๋ญ๊ฐ ์ ์๋๋ฉด ์ผ๋จ YAML ๋์ด์ฐ๊ธฐ๋ถํฐ ํ์ธ
- Nginx ๋ผ์ฐํ ์ค์ ์ URI ๋ง์ง๋ง์ / ์ถ๊ฐ
[https://askubuntu.com/questions/1173951/all-routes-except-return-404-from-nginx-running-flask-wsgi](https://askubuntu.com/questions/1173951/all-routes-except-return-404-from-nginx-running-flask-wsgi)
- EC2 ์ธ์คํด์ค์ ๊น๋จน์ง ๋ง๊ณ  ์ฌ์ฉ์ ๋ฐ์ดํฐ ๋ช์ํ  ๊ฒ
user_data ์ฌ์ฉ์ terraform init ๋ค์ ํด์ผ ํจ
- EC2 ์ธ์คํด์ค์ ์๋์ผ๋ก CodeDeploy Agent ์ค์นํ๋ ค๋ฉด CodeDeploy ์ ๊ทผ๊ฐ๋ฅ ์ญํ ์ ๋จผ์  ๋ถ์ฌํ  ๊ฒ
- ์ค๋ฅ ํด๊ฒฐ์ ์ํด ์ด๊ฒ ์ ๊ฒ ํด๋ณด๋๋ผ ๋ช ์๊ฐ ๊น์ง ๊ฑธ๋ฆฌ๋ ๊ฒ์ ๋น์ฐํ ๊ฒ..
    
    ![Project-1/Untitled%204.png](Project-1/Untitled%204.png)
    
- ์ ์ ๋ฐ์ดํฐ์ ํ๋ก๊ทธ๋จ ์ค์น ๋ช๋ น์ ๋ฃ์ผ๋ฉด ๋น์ฐํ ์ค์น ๋  ๋ ๊น์ง ๊ธฐ๋ค๋ ค์ผ ํฉ๋๋ค
    
    ![Project-1/Untitled%205.png](Project-1/Untitled%205.png)
    
- HTTP๋ HTTPS๋ ํท๊ฐ๋ฆฌ์ง ๋ง๊ฒใใใใ(์ ์ผ ์ด์ด ์๋ ๋ถ๋ถ)
- HTML์ ์ ๋์ค์ง๋ง CSS, JS ๋ก๋๊ฐ ์๋๋ฉด Nginx ์ค์  ๋ฌธ์ 
- ์ ์ ์ปจํ์ธ  s3 ํธ์คํ์ ์ํ ์ด๋์ผ๋ก cp */*/*.css */*/*.js ./deploy ์ด๋ฐ๊ฒ๋ ๊ฐ๋ฅ
- S3์ static resource ๋ถ๋ฆฌํ  ๋ public access ๊ถํ ์ ๊ฒํ๊ธฐ
- S3 ๋ฒํท์ ์ฑ ๋ง๋ค ๋ ๋ฆฌ์์ค์ /* ๋ถ์ด๊ธฐ[https://stackoverflow.com/questions/44228422/s3-bucket-action-doesnt-apply-to-any-resources](https://stackoverflow.com/questions/44228422/s3-bucket-action-doesnt-apply-to-any-resources)
- ํ๋ผํผ์์ ๋ณด์๊ทธ๋ฃน ์ค์ค๋ก๋ฅผ ์์ค๋ก ์ฌ์ฉํ๋ ค๋ฉด ID๋ฅผ ๋ฃ์ง ๋ง๊ณ  self = true ์ด์ฉํ๊ธฐ
[https://stackoverflow.com/questions/49995417/self-reference-not-allowed-in-security-group-definition](https://stackoverflow.com/questions/49995417/self-reference-not-allowed-in-security-group-definition)
- ์ค์ผ์คํธ๋ ์ด์ ๊ตฌ์ถํ  ๋ ํผ๋ธ๋ฆญ IP ๋ง๊ณ  ํ๋ผ์ด๋น IP๋ก ๊ตฌ์ถ
- EC2 ํ๋ผ์ด๋น IP ๊ฐ์ ธ์ค๊ธฐโญ
    - /sbin/ifconfig eth0 | grep 'inet' | cut -d: -f2 | awk '{print $2}'
    - hostname -i
- ์ง์ํํ๋ฆฟ ์ฌ์ฉ์ ๋์๋ฌธ์ ๊ตฌ๋ถ ํ์(ํนํ ๋ฉ์๋ ๋ถ๋ถ)
- Nginx์์ ๋ฐ๋ก POST ๋ฉ์๋๋ฅผ ์ฌ์ฉํ ๊ฒฝ์ฐ ๋ฆฌ๋ค์ด๋ ์ ๋ฐ์
    
    โ [https://stackoverflow.com/questions/27795068/nginx-rewrite-post-data](https://stackoverflow.com/questions/27795068/nginx-rewrite-post-data)
    
- Apply์๋ฒ์ POST, Result์๋ฒ์ GET ๋ฐฉ์์ ์ ์ฉํ์ต๋๋ค
- ๊น ๋ธ๋์น๋ก ๊ด๋ฆฌํ  ๋ ํ๋ผํผ ์๋ง์ด ๋์ง ์๋๋ก ์ฃผ์ํ๊ธฐ
- ๋์ปค์ค์์ ๋์ปค์ปดํฌ์ฆํ์ผ์ ์คํ์ผ๋ก ์ด์ฉํด ๊ตฌ๋ ๊ฐ๋ฅ[https://docs.docker.com/engine/swarm/stack-deploy/](https://docs.docker.com/engine/swarm/stack-deploy/)
- ๋์ปค์คํ ๊ตฌ๋์ ์ปจํ์ด๋ ์คํ์์ฒด๊ฐ ๋ฌธ์ ์ผ ๊ฒฝ์ฐ ์ปดํฌ์ฆ๋ฅผ ํ ๋ฒ ๋๋ ค๋ณด๋ฉด ์ค๋ง๋ฆฌ๋ฅผ ์ฐพ์ ์ ์์ต๋๋ค
    
    ![Project-1/Untitled%206.png](Project-1/Untitled%206.png)
    
- RDS๊ฐ ํ๋ผ์ด๋น ์๋ธ๋ท์ ์กด์ฌํ๋ฉด Travis์์ ์ฝ๋ํ์คํธ๋ฅผ ์งํํ  ๋ RDS์ ์ ์์คํจํ์ฌ ํ์คํธ ์คํจ๋ก ์ด์ด์ง๋ ๊ฒ์ ์ฃผ์
- MySQL ์ ์ ์ปค๋งจ๋
    
    ```s
    mysql -h myapp.cnr20hoyd3cu.ap-northeast-2.rds.amazonaws.com -P 3306 -u root -p
    ```
    
- ๋์ปค ์ค์๋ชจ๋ ์๋ฌ ํ์ธ
    
    โ  docker service logs {SERVICE} ๋ช๋ น์ผ๋ก ๋ก๊ทธ ํ์ธ ๊ฐ๋ฅ
    
    ![Project-1/Untitled%207.png](Project-1/Untitled%207.png)
    

## TODO

---

- IaC
    - [x]  Terraform
    - [ ]  Terraform ๊ณ ๋ํ
- CICD
    - [x]  Container(Dockerfile)
        - [x]  Flask + gunicorn
        - [x]  MySQL
        - [x]  Nginx
    - [x]  Docker Compose
    - [x]  Travis CI
    - [x]  CodeDeploy
    - [x]  ๋ฐฐํฌ ์๋ฃ ํ ๊ตฌ๋ ์ธํ
    - [x]  EC2
    - [ ]  CI๋ฅผ ์ํ ํ์คํธ์ฝ๋ ์์ฑ
- Server
    - [x]  HTML CSS ํ ๋ง๋ค๊ธฐ
    - [x]  RDS, MySQL ์ฐ๊ฒฐ
    - [x]  ๊ธฐ๋ฅ ์ ์
- Orchestration
    - [x]  Swarm Mode

# Part 1 - CICD

## CodeDeploy(์ฝ์)

1. ์๋ก์ด CodeDeploy ์์ ์์ฑ
    
    ![Project-1/Untitled%208.png](Project-1/Untitled%208.png)
    
2. ๋ฐฐํฌ๊ทธ๋ฃน ์์ฑ
    
    ![Project-1/Untitled%209.png](Project-1/Untitled%209.png)
    
3. ํ๊ทธ๋ฅผ ์ด์ฉํด EC2๋ฅผ ์ง์ ํ  ์ ์์ต๋๋ค
    
    ![Project-1/Untitled%2010.png](Project-1/Untitled%2010.png)
    
4. AWS SM์ ์ฌ์ฉํ์ง ์๊ณ  ์ง์  CodeDeploy๋ฅผ ์ค์นํ์์ต๋๋ค
    
    ![Project-1/Untitled%2011.png](Project-1/Untitled%2011.png)
    
5. CodeDeploy์ ๋ฐฐํฌ ๊ด๋ จ ์ค์ ์ ์งํํฉ๋๋ค
    
    ![Project-1/Untitled%2012.png](Project-1/Untitled%2012.png)
    

## EC2 ๋ฐฐํฌ ์ค์ 

---

1. CodeDeploy Agent ์ค์น
    
    ```s
    aws s3 cp s3://aws-codedeploy-ap-northeast-2/latest/install . --region ap-northeast-2
    sudo yum install -y ruby wget
    chmod +x ./install
    sudo ./install auto
    sudo service codedeploy-agent start
    sudo service codedeploy-agent status
    ```
    
2. Docker ์ค์น
    
    ```s
    sudo yum -y install docker
    sudo systemctl start docker
    sudo systemctl enable docker 
    sudo usermod -aG docker ec2-user
    ```
    
    ๊ถํ ๋ฌธ์ ๋ก docker ps -a ๋ช๋ น์ด ๋ถ๊ฐ๋ฅ ํ  ๊ฒฝ์ฐ
    
    ```s
    sudo chmod 666 /var/run/docker.sock
    ```

3. ๋ฐ๋ผ์ ํ๋ผํผ์ ์์ฑํ  EC2 ์ธ์คํด์ค์ ์ฌ์ฉ์ ๋ฐ์ดํฐ๋ ๋ค์๊ณผ ๊ฐ์ต๋๋ค
        
    ```s
    <<-EOF
        #!/bin/bash
        aws s3 cp s3://aws-codedeploy-ap-northeast-2/latest/install . --region ap-northeast-2
        sudo yum install -y ruby wget git
        chmod +x ./install
        sudo ./install auto
        sudo service codedeploy-agent start
        sudo yum -y install docker
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker ec2-user
        sudo chmod 666 /var/run/docker.sock
        sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        EOF
    ```
        
4. CICD๋ฅผ ์ํ .travis.yml ์์ฑ

    ```yaml title=".travis.yml"
    language: generic

    services:
        - docker

    before_install:
        - docker build -t dotoryeee/test-submit-server -f ./flask-submit-server/Dockerfile ./flask-submit-server

    script:
        - docker run -e CI=true dotoryeee/test-submit-server python3 test.py

    after_success:
        - docker build -t dotoryeee/flask-submit-server ./flask-submit-server
        - docker build -t dotoryeee/flask-result-server ./flask-result-server
        - docker build -t dotoryeee/nginx ./nginx

        - echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_ID" --password-stdin

        - docker push dotoryeee/flask-submit-server
        - docker push dotoryeee/flask-result-server
        - docker push dotoryeee/nginx

    before_deploy:
        - zip -r myapp.zip ./* #CI ์๋ฃ ํ ๋ชจ๋  ํ์ผ์ myapp.zip๋ก ์์ถ
        - mkdir -p deploy  # deploy ๋๋ ํฐ๋ฆฌ ์์ฑ
        - mv myapp.zip ./deploy #myapp.zip๋ฅผ deploy ๋๋ ํฐ๋ฆฌ๋ก ์ด๋

    deploy:
        - provider: s3
        access_key_id: $AWS_ACCESS_KEY
        secret_access_key: $AWS_SECRET_ACCESS_KEY
        bucket: dotoryeee-s3
        region: ap-northeast-2
        skip_cleanup: true #์์ถํ์ผ ์ญ์  ๋ฐฉ์ง
        local_dir: deploy #deploy ๋๋ ํฐ๋ฆฌ์ ํ์ผ์ S3์ ์ ์ก
        wait-until-deployed: true
        on:
            branch: main
        - provider: codedeploy
        access_key_id: $AWS_ACCESS_KEY
        secret_access_key: $AWS_SECRET_ACCESS_KEY
        bucket: dotoryeee-s3
        key: myapp.zip
        bundle_type: zip
        application: talentpool
        deployment_group: CICD-test
        region: ap-northeast-2
        wait-until-deployed: true #AWS์ ํ์ผ ์ ๋ฌ ์ดํ์๋ ์๋ฌ ํ์ธ ๊ฐ๋ฅ
        on:
            branch: main
    ```

5. CodeDeploy ์ดํ ์์ ๋ช์๋ฅผ ์ํ appspec.yml ์์ฑ
    
    ```yaml title="appspec.yml"
    version: 0.0
    os: linux
    files:
        - source: /
        destination: /home/ec2-user/app
        overwrite: yes
    hooks:
        AfterInstall:
        - location: execute-deploy.sh
            timeout: 300
    ```
    
1. ์๋ฒ์์ ๊ตฌ๋ ์ํ docker-compose-ec2.yml ์์ฑ
    
    ```yaml title="docker-compose-ec2.yml"
    version: "3"
    services:
    flask-submit-server:
        image: dotoryeee/flask-submit-server
        restart: always
        container_name: flask-submit-server
        ports:
        - "8000:8000"
        command: gunicorn -w 1 -b 0.0.0.0:8000 wsgi:server
    
    flask-result-server:
        image: dotoryeee/flask-result-server
        restart: always
        container_name: flask-result-server
        ports:
        - "7000:7000"
        volumes:
        - ./flask-result-server:/usr/src/app
        command: gunicorn -w 1 -b 0.0.0.0:7000 wsgi:server
    
    nginx:
        image: dotoryeee/nginx
        container_name: nginx
        restart: always
        ports:
        - "80:80"
        #flask ์ปจํ์ด๋ ๋ก๋๊ฐ ๋๋๋ฉด Nginx๋ฅผ ์์ํฉ๋๋ค
        depends_on:
        - flask-submit-server
        - flask-result-server
    ```
    
7. ์ฐ๋ํ์ฌ ์๋ฒ ์์ ๋ช๋ น์ด ๋ช์๋ execute-deploy ์คํฌ๋ฆฝํธ ์์ฑ
        
    ```bash title="execute-deploy.sh"
    #!/bin/bash
    sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    docker-compose -f /home/e2-user/app/docker-compose-ec2.yml rm -fs
    docker system prune -a -f
    docker-compose -f /home/e2-user/app/docker-compose-ec2.yml up
    ```
    

## ๋์ ํ์ธ

---

1. Terraform Apply๋ฅผ ์ด์ฉํด ์ธํ๋ผ๋ฅผ ์์ฑํฉ๋๋ค
    - Terraform Apply
        
    ```json
    An execution plan has been generated and is shown below.
    Resource actions are indicated with the following symbols:
        + create

    Terraform will perform the following actions:

        # aws_instance.public_01 will be created
        + resource "aws_instance" "public_01" {
            + ami                          = "ami-006e2f9fa7597680a"
            + arn                          = (known after apply)
            + associate_public_ip_address  = (known after apply)
            + availability_zone            = (known after apply)
            + cpu_core_count               = (known after apply)
            + cpu_threads_per_core         = (known after apply)
            + get_password_data            = false
            + host_id                      = (known after apply)
            + iam_instance_profile         = "EC2_role_for_codedeploy"
            + id                           = (known after apply)
            + instance_state               = (known after apply)
            + instance_type                = "t2.micro"
            + ipv6_address_count           = (known after apply)
            + ipv6_addresses               = (known after apply)
            + key_name                     = "dotoryeee"
            + outpost_arn                  = (known after apply)
            + password_data                = (known after apply)
            + placement_group              = (known after apply)
            + primary_network_interface_id = (known after apply)
            + private_dns                  = (known after apply)
            + private_ip                   = (known after apply)
            + public_dns                   = (known after apply)
            + public_ip                    = (known after apply)
            + secondary_private_ips        = (known after apply)
            + security_groups              = (known after apply)
            + source_dest_check            = true
            + subnet_id                    = (known after apply)
            + tags                         = {
                + "Name" = "talentpool-webserver"
            }
            + tenancy                      = (known after apply)
            + user_data                    = "37dd0b56bc65486734172a29cc30def4180da21a"
            + vpc_security_group_ids       = (known after apply)

            + ebs_block_device {
                + delete_on_termination = (known after apply)
                + device_name           = (known after apply)
                + encrypted             = (known after apply)
                + iops                  = (known after apply)
                + kms_key_id            = (known after apply)
                + snapshot_id           = (known after apply)
                + tags                  = (known after apply)
                + throughput            = (known after apply)
                + volume_id             = (known after apply)
                + volume_size           = (known after apply)
                + volume_type           = (known after apply)
            }

            + enclave_options {
                + enabled = (known after apply)
            }

            + ephemeral_block_device {
                + device_name  = (known after apply)
                + no_device    = (known after apply)
                + virtual_name = (known after apply)
            }

            + metadata_options {
                + http_endpoint               = (known after apply)
                + http_put_response_hop_limit = (known after apply)
                + http_tokens                 = (known after apply)
            }

            + network_interface {
                + delete_on_termination = (known after apply)
                + device_index          = (known after apply)
                + network_interface_id  = (known after apply)
            }

            + root_block_device {
                + delete_on_termination = (known after apply)
                + device_name           = (known after apply)
                + encrypted             = (known after apply)
                + iops                  = (known after apply)
                + kms_key_id            = (known after apply)
                + tags                  = (known after apply)
                + throughput            = (known after apply)
                + volume_id             = (known after apply)
                + volume_size           = (known after apply)
                + volume_type           = (known after apply)
            }
        }

        # aws_instance.public_02 will be created
        + resource "aws_instance" "public_02" {
            + ami                          = "ami-006e2f9fa7597680a"
            + arn                          = (known after apply)
            + associate_public_ip_address  = (known after apply)
            + availability_zone            = (known after apply)
            + cpu_core_count               = (known after apply)
            + cpu_threads_per_core         = (known after apply)
            + get_password_data            = false
            + host_id                      = (known after apply)
            + iam_instance_profile         = "EC2_role_for_codedeploy"
            + id                           = (known after apply)
            + instance_state               = (known after apply)
            + instance_type                = "t2.micro"
            + ipv6_address_count           = (known after apply)
            + ipv6_addresses               = (known after apply)
            + key_name                     = "dotoryeee"
            + outpost_arn                  = (known after apply)
            + password_data                = (known after apply)
            + placement_group              = (known after apply)
            + primary_network_interface_id = (known after apply)
            + private_dns                  = (known after apply)
            + private_ip                   = (known after apply)
            + public_dns                   = (known after apply)
            + public_ip                    = (known after apply)
            + secondary_private_ips        = (known after apply)
            + security_groups              = (known after apply)
            + source_dest_check            = true
            + subnet_id                    = (known after apply)
            + tags                         = {
                + "Name" = "talentpool-webserver"
            }
            + tenancy                      = (known after apply)
            + user_data                    = "37dd0b56bc65486734172a29cc30def4180da21a"
            + vpc_security_group_ids       = (known after apply)

            + ebs_block_device {
                + delete_on_termination = (known after apply)
                + device_name           = (known after apply)
                + encrypted             = (known after apply)
                + iops                  = (known after apply)
                + kms_key_id            = (known after apply)
                + snapshot_id           = (known after apply)
                + tags                  = (known after apply)
                + throughput            = (known after apply)
                + volume_id             = (known after apply)
                + volume_size           = (known after apply)
                + volume_type           = (known after apply)
            }

            + enclave_options {
                + enabled = (known after apply)
            }

            + ephemeral_block_device {
                + device_name  = (known after apply)
                + no_device    = (known after apply)
                + virtual_name = (known after apply)
            }

            + metadata_options {
                + http_endpoint               = (known after apply)
                + http_put_response_hop_limit = (known after apply)
                + http_tokens                 = (known after apply)
            }

            + network_interface {
                + delete_on_termination = (known after apply)
                + device_index          = (known after apply)
                + network_interface_id  = (known after apply)
            }

            + root_block_device {
                + delete_on_termination = (known after apply)
                + device_name           = (known after apply)
                + encrypted             = (known after apply)
                + iops                  = (known after apply)
                + kms_key_id            = (known after apply)
                + tags                  = (known after apply)
                + throughput            = (known after apply)
                + volume_id             = (known after apply)
                + volume_size           = (known after apply)
                + volume_type           = (known after apply)
            }
        }

        # aws_internet_gateway.main will be created
        + resource "aws_internet_gateway" "main" {
            + arn      = (known after apply)
            + id       = (known after apply)
            + owner_id = (known after apply)
            + tags     = {
                + "Name" = "igw-talent-pool"
            }
            + vpc_id   = (known after apply)
        }

        # aws_key_pair.dotoryeee will be created
        + resource "aws_key_pair" "dotoryeee" {
            + arn         = (known after apply)
            + fingerprint = (known after apply)
            + id          = (known after apply)
            + key_name    = "dotoryeee"
            + key_pair_id = (known after apply)
            + public_key  = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDD5D5mHSD/vdgcGmh6Kd57DqLxebcvbrUsHj8DYDW0+9MSvvK874Bm4hpqHliYze/ht7VnzL5+A5qZkCevKGBDeJNmR/QDHccCsCfRuyEmzMlvj3SxzYSH2N4lBG6eZZbQ+0yRl7ny3aeyol5boDkztLZ/PZwVR5IH6BgsNiGClSDtuf2CYoKN7hQufjeuCDcLlQa+ItFa4abMe/mWtMeEh7+ZpC+0KAFFvqY80OCtuUdqq7tcP8uHzQy9mPKvKBieJYitUoStjFEMAro1v34u6193Qgk6DAhyMom4GmLc2+tTyKMsvBlRKUOb87F+2zsATX3Ahz9cMpEkfPTkY15V dotoryeee@i5-6500"
        }

        # aws_route.default will be created
        + resource "aws_route" "default" {
            + destination_cidr_block     = "0.0.0.0/0"
            + destination_prefix_list_id = (known after apply)
            + egress_only_gateway_id     = (known after apply)
            + gateway_id                 = (known after apply)
            + id                         = (known after apply)
            + instance_id                = (known after apply)
            + instance_owner_id          = (known after apply)
            + local_gateway_id           = (known after apply)
            + nat_gateway_id             = (known after apply)
            + network_interface_id       = (known after apply)
            + origin                     = (known after apply)
            + route_table_id             = (known after apply)
            + state                      = (known after apply)
        }

        # aws_route_table.private will be created
        + resource "aws_route_table" "private" {
            + id               = (known after apply)
            + owner_id         = (known after apply)
            + propagating_vgws = (known after apply)
            + route            = (known after apply)
            + tags             = {
                + "Name" = "RT-private-talent-pool"
            }
            + vpc_id           = (known after apply)
        }

        # aws_route_table.public will be created
        + resource "aws_route_table" "public" {
            + id               = (known after apply)
            + owner_id         = (known after apply)
            + propagating_vgws = (known after apply)
            + route            = (known after apply)
            + tags             = {
                + "Name" = "RT-public-talent-pool"
            }
            + vpc_id           = (known after apply)
        }

        # aws_route_table_association.private-asso-2a will be created
        + resource "aws_route_table_association" "private-asso-2a" {
            + id             = (known after apply)
            + route_table_id = (known after apply)
            + subnet_id      = (known after apply)
        }

        # aws_route_table_association.private-asso-2c will be created
        + resource "aws_route_table_association" "private-asso-2c" {
            + id             = (known after apply)
            + route_table_id = (known after apply)
            + subnet_id      = (known after apply)
        }

        # aws_route_table_association.public-asso-2a will be created
        + resource "aws_route_table_association" "public-asso-2a" {
            + id             = (known after apply)
            + route_table_id = (known after apply)
            + subnet_id      = (known after apply)
        }

        # aws_route_table_association.public-asso-2c will be created
        + resource "aws_route_table_association" "public-asso-2c" {
            + id             = (known after apply)
            + route_table_id = (known after apply)
            + subnet_id      = (known after apply)
        }

        # aws_security_group.public_ec2 will be created
        + resource "aws_security_group" "public_ec2" {
            + arn                    = (known after apply)
            + description            = "allow SSH from anywhere"
            + egress                 = [
                + {
                    + cidr_blocks      = [
                        + "0.0.0.0/0",
                    ]
                    + description      = ""
                    + from_port        = 0
                    + ipv6_cidr_blocks = []
                    + prefix_list_ids  = []
                    + protocol         = "-1"
                    + security_groups  = []
                    + self             = false
                    + to_port          = 0
                },
            ]
            + id                     = (known after apply)
            + ingress                = [
                + {
                    + cidr_blocks      = [
                        + "0.0.0.0/0",
                    ]
                    + description      = ""
                    + from_port        = 22
                    + ipv6_cidr_blocks = []
                    + prefix_list_ids  = []
                    + protocol         = "tcp"
                    + security_groups  = []
                    + self             = false
                    + to_port          = 22
                },
                + {
                    + cidr_blocks      = [
                        + "0.0.0.0/0",
                    ]
                    + description      = ""
                    + from_port        = 80
                    + ipv6_cidr_blocks = []
                    + prefix_list_ids  = []
                    + protocol         = "tcp"
                    + security_groups  = []
                    + self             = false
                    + to_port          = 80
                },
            ]
            + name                   = "allow SSH and HTTP"
            + name_prefix            = (known after apply)
            + owner_id               = (known after apply)
            + revoke_rules_on_delete = false
            + tags                   = {
                + "Name" = "SG-EC2-webserver"
            }
            + vpc_id                 = (known after apply)
        }

        # aws_subnet.private-2a will be created
        + resource "aws_subnet" "private-2a" {
            + arn                             = (known after apply)
            + assign_ipv6_address_on_creation = false
            + availability_zone               = "ap-northeast-2a"
            + availability_zone_id            = (known after apply)
            + cidr_block                      = "10.0.2.0/24"
            + id                              = (known after apply)
            + ipv6_cidr_block_association_id  = (known after apply)
            + map_public_ip_on_launch         = false
            + owner_id                        = (known after apply)
            + tags                            = {
                + "Name" = "private-2a"
            }
            + vpc_id                          = (known after apply)
        }

        # aws_subnet.private-2c will be created
        + resource "aws_subnet" "private-2c" {
            + arn                             = (known after apply)
            + assign_ipv6_address_on_creation = false
            + availability_zone               = "ap-northeast-2c"
            + availability_zone_id            = (known after apply)
            + cidr_block                      = "10.0.3.0/24"
            + id                              = (known after apply)
            + ipv6_cidr_block_association_id  = (known after apply)
            + map_public_ip_on_launch         = false
            + owner_id                        = (known after apply)
            + tags                            = {
                + "Name" = "private-2c"
            }
            + vpc_id                          = (known after apply)
        }

        # aws_subnet.public-2a will be created
        + resource "aws_subnet" "public-2a" {
            + arn                             = (known after apply)
            + assign_ipv6_address_on_creation = false
            + availability_zone               = "ap-northeast-2a"
            + availability_zone_id            = (known after apply)
            + cidr_block                      = "10.0.0.0/24"
            + id                              = (known after apply)
            + ipv6_cidr_block_association_id  = (known after apply)
            + map_public_ip_on_launch         = true
            + owner_id                        = (known after apply)
            + tags                            = {
                + "Name" = "public-2a-talent-pool"
            }
            + vpc_id                          = (known after apply)
        }

        # aws_subnet.public-2c will be created
        + resource "aws_subnet" "public-2c" {
            + arn                             = (known after apply)
            + assign_ipv6_address_on_creation = false
            + availability_zone               = "ap-northeast-2c"
            + availability_zone_id            = (known after apply)
            + cidr_block                      = "10.0.1.0/24"
            + id                              = (known after apply)
            + ipv6_cidr_block_association_id  = (known after apply)
            + map_public_ip_on_launch         = true
            + owner_id                        = (known after apply)
            + tags                            = {
                + "Name" = "public-2c-talent-pool"
            }
            + vpc_id                          = (known after apply)
        }

        # aws_vpc.main will be created
        + resource "aws_vpc" "main" {
            + arn                              = (known after apply)
            + assign_generated_ipv6_cidr_block = false
            + cidr_block                       = "10.0.0.0/16"
            + default_network_acl_id           = (known after apply)
            + default_route_table_id           = (known after apply)
            + default_security_group_id        = (known after apply)
            + dhcp_options_id                  = (known after apply)
            + enable_classiclink               = (known after apply)
            + enable_classiclink_dns_support   = (known after apply)
            + enable_dns_hostnames             = true
            + enable_dns_support               = true
            + id                               = (known after apply)
            + instance_tenancy                 = "default"
            + ipv6_association_id              = (known after apply)
            + ipv6_cidr_block                  = (known after apply)
            + main_route_table_id              = (known after apply)
            + owner_id                         = (known after apply)
            + tags                             = {
                + "Name" = "vpc-talent-pool"
            }
        }

    Plan: 17 to add, 0 to change, 0 to destroy.

    Do you want to perform these actions?
        Terraform will perform the actions described above.
        Only 'yes' will be accepted to approve.

        Enter a value: yes

    aws_key_pair.dotoryeee: Creating...
    aws_vpc.main: Creating...
    aws_key_pair.dotoryeee: Creation complete after 1s [id=dotoryeee]
    aws_vpc.main: Still creating... [10s elapsed]
    aws_vpc.main: Creation complete after 11s [id=vpc-0c885c480266a1609]
    aws_route_table.public: Creating...
    aws_subnet.private-2c: Creating...
    aws_subnet.public-2a: Creating...
    aws_route_table.private: Creating...
    aws_internet_gateway.main: Creating...
    aws_subnet.public-2c: Creating...
    aws_subnet.private-2a: Creating...
    aws_security_group.public_ec2: Creating...
    aws_route_table.private: Creation complete after 0s [id=rtb-007ecd93701976184]
    aws_route_table.public: Creation complete after 0s [id=rtb-07a3c28f427d9d9b0]
    aws_internet_gateway.main: Creation complete after 1s [id=igw-08b4682de4ec8f301]
    aws_subnet.private-2c: Creation complete after 1s [id=subnet-0f054920c100a9591]
    aws_subnet.private-2a: Creation complete after 1s [id=subnet-05bfc7af15120b423]
    aws_route_table_association.private-asso-2c: Creating...
    aws_route.default: Creating...
    aws_route_table_association.private-asso-2a: Creating...
    aws_route_table_association.private-asso-2c: Creation complete after 0s [id=rtbassoc-0dbe25bb20f9f3fbf]
    aws_route_table_association.private-asso-2a: Creation complete after 0s [id=rtbassoc-099fe2753e2de8eeb]
    aws_route.default: Creation complete after 0s [id=r-rtb-07a3c28f427d9d9b01080289494]
    aws_security_group.public_ec2: Creation complete after 2s [id=sg-0a3b2cfbd654e0211]
    aws_subnet.public-2a: Still creating... [10s elapsed]
    aws_subnet.public-2c: Still creating... [10s elapsed]
    aws_subnet.public-2c: Creation complete after 11s [id=subnet-08dd1b40e3066df36]
    aws_subnet.public-2a: Creation complete after 11s [id=subnet-03874ee39103bba68]
    aws_route_table_association.public-asso-2c: Creating...
    aws_route_table_association.public-asso-2a: Creating...
    aws_instance.public_01: Creating...
    aws_instance.public_02: Creating...
    aws_route_table_association.public-asso-2a: Creation complete after 0s [id=rtbassoc-0b6bc559f38878ca0]
    aws_route_table_association.public-asso-2c: Creation complete after 0s [id=rtbassoc-0eaa97ebcf00bcfd6]
    aws_instance.public_01: Still creating... [10s elapsed]
    aws_instance.public_02: Still creating... [10s elapsed]
    aws_instance.public_01: Still creating... [20s elapsed]
    aws_instance.public_02: Still creating... [20s elapsed]
    aws_instance.public_01: Creation complete after 21s [id=i-00cb9f1261ba14494]
    aws_instance.public_02: Creation complete after 21s [id=i-0a84d66623f8c2a83]

    Apply complete! Resources: 17 added, 0 changed, 0 destroyed.
    ```
        
    
    ![Project-1/Untitled%2013.png](Project-1/Untitled%2013.png)
    
2. EC2๊ฐ ์ ์์ฑ๋์์ต๋๋ค
    
    ![Project-1/Untitled%2014.png](Project-1/Untitled%2014.png)
    
3. ๋ณด์๊ทธ๋ฃน๊ณผ ์ญํ ์ด ์ ๋ถ์ฌ๋์์ต๋๋ค
    
    ![Project-1/Untitled%2015.png](Project-1/Untitled%2015.png)
    
4. SSH๋ก ์ธ์คํด์ค์ ์ ์ํด Docker๊ฐ ์ค์น๋ ๊ฒ์ ํ์ธํฉ๋๋ค
์ต์ด ์ ์์์๋ ๋ถ๊ตฌํ๊ณ  ๋์ปค๊ฐ ์ค์น๋ ๊ฒ์ ํ์ธํ  ์ ์์ต๋๋ค
    
    ![Project-1/Untitled%2016.png](Project-1/Untitled%2016.png)
    
5. ๊นํ์ Push ํ์ฌ CICD ํ์ดํ๋ผ์ธ์ ์๋์ ๊ฑธ์ด๋ด๋๋ค
    
    ![Project-1/Untitled%2017.png](Project-1/Untitled%2017.png)
    
6. ๊นํ์ Push ํ๋ฉด Travis CI๊ฐ ์๋์ผ๋ก ํตํฉ ํ์คํธ๋ฅผ ์ํํฉ๋๋ค
    
    ![Project-1/Untitled%2018.png](Project-1/Untitled%2018.png)
    
7. CI๊ฐ ์ฑ๊ณตํ๋ฉด
    
    ![Project-1/Untitled%2019.png](Project-1/Untitled%2019.png)
    
8. AWS S3์ ์ฝ๋๋ฅผ ์๋ก๋ ํ๊ณ  CodeDeploy์ ๋ฐฐํฌ ํธ๋ฆฌ๊ฑฐ๋ฅผ ์์ํฉ๋๋ค
    
    ![Project-1/Untitled%2020.png](Project-1/Untitled%2020.png)
    
9. S3์ ์์ค์ฝ๋๊ฐ ์๋ก๋ ๋์์ต๋๋ค
    
    ![Project-1/Untitled%2021.png](Project-1/Untitled%2021.png)
    
10. CodeDeploy๊ฐ ์ค์ ์ ๋งค์นญ๋๋ EC2๋ฅผ ์ฐพ์ต๋๋ค
    
    ![Project-1/Untitled%2022.png](Project-1/Untitled%2022.png)
    
11. CodeDeploy์ ์๋ก์ด ์ผ๊ฑฐ๋ฆฌ๊ฐ ๋ก๋๋์์ต๋๋ค
    
    ![Project-1/Untitled%2023.png](Project-1/Untitled%2023.png)
    
12. CodeDeploy๊ฐ S3 โ EC2๋ก ์์ค์ฝ๋๋ฅผ ์ง์ด๋ฃ๊ณ  ์์ถ์ ํ์ด์ค๋๋ค
    
    ![Project-1/Untitled%2024.png](Project-1/Untitled%2024.png)
    
13. ์คํจํ๋ฉด ์๋ฌ๊ฐ ๋งค์ฐ ์ ๋์ต๋๋ค. CodeDeploy๊ฐ ์ด ๋ถ๋ถ์ด ๋๋ฌด ์ ๋์ด์์ด์ ๋น์คํก์ ๋ชป ์ฐ๊ฒ ์ต๋๋ค
    
    ![Project-1/Untitled%2025.png](Project-1/Untitled%2025.png)
    
    ![Project-1/Untitled%2026.png](Project-1/Untitled%2026.png)
    
14. Travis CI์์ wait-until-deployed์ต์์ ์ฌ์ฉํ๊ธฐ ๋๋ฌธ์ ๋ฐฐํฌ๊ฐ ์ต์ข ์๋ฃ๋  ๋ ๊น์ง ์ง์ผ๋ณด๊ณ  ์์ต๋๋ค. ๋์ปค ์ปดํฌ์ฆ ๋๋๋ ๊ฒ ๊น์ง ํฌํจํด์ ๋ฐฐํฌ ์ด ๊ณผ์ ์ด ์ผ๋ง๋ ๊ฑธ๋ฆฌ๋์ง ์ ์ ์์ต๋๋ค.
    
    ![Project-1/Untitled%2027.png](Project-1/Untitled%2027.png)
    
15. ๋ ์ธ์คํด์ค ๋ชจ๋ ๋ฐฐํฌ๊ฐ ์ฑ๊ณตํ๊ฒ ๋๋ฉด
    
    ![Project-1/Untitled%2028.png](Project-1/Untitled%2028.png)
    
16. EC2์ ํ์ผ์ด ์ ์์ฑ๋์ด์์ต๋๋ค
    
    ![Project-1/Untitled%2029.png](Project-1/Untitled%2029.png)
    
17. ๋ชจ๋  ๋ฐฐํฌ๊ณผ์ ์ ๋ง์น๋ฉด EC2์์ ์๋์ผ๋ก ์ปดํฌ์ฆ๋ฅผ ์ด์ฉํด Hub์ ์๋ก๋๋ ์ด๋ฏธ์ง๋ฅผ ๊ฐ์ ธ์ ์คํํฉ๋๋ค.
18. ์๋ฒ๊ฐ ์ ์คํ๋ฉ๋๋ค
    
    ![Project-1/Untitled%2030.png](Project-1/Untitled%2030.png)
    
19. EC2์ ํผ๋ธ๋ฆญ DNS๋ก ์ ์ํ๋ฉด ํ์ธํ  ์ ์์ต๋๋ค
    
    ![Project-1/Untitled%2031.png](Project-1/Untitled%2031.png)
    

# Part 2 - Service

---

## ๋ธ๋์น

1. ๋ธ๋์น๋ฅผ ํ๋ ๋ง๋ค์ด์ ์์์ ์์ํฉ๋๋ค
    
    ![Project-1/Untitled%2032.png](Project-1/Untitled%2032.png)
    
2. ๋ธ๋์น๋ฅผ ์์ฑํด์ ์์ํ๊ณ  Pull Request๋ก ๋จธ์ง๋ฅผ ์์ฒญ โ ๋จธ์ง ํ ํธ๋ ๋น์ค๊ฐ ํ์คํธ๋ฅผ ํฉ๋๋ค. ๊นํ ํ์ด์ง์์ ํ์ธํ  ์ ์์ต๋๋ค
    
    ![Project-1/Untitled%2033.png](Project-1/Untitled%2033.png)
    
3. ์๋ฒ๊ฐ ์์ฑ๋๋ฉด pull request๋ฅผ ์์ฒญํฉ๋๋ค
    
    ![Project-1/Untitled%2034.png](Project-1/Untitled%2034.png)
    
4. ๊นํ์์ ์ฝ๋ ๊ฒ์ฌ ํ ํฉ๋ณ ๊ฐ๋ฅํ๋ฉด Merge๋ฅผ ์งํํฉ๋๋ค
    
    ![Project-1/Untitled%2035.png](Project-1/Untitled%2035.png)
    
5. PR์ ์์ฒญ๋๋ฉด ์๋์ผ๋ก ํธ๋ ๋น์ค์์ ๊ฒ์ฌ๋ฅผ ์์ํฉ๋๋ค
    
    ![Project-1/Untitled%2036.png](Project-1/Untitled%2036.png)
    
6. ๊ฒ์ฌ ์์
    
    ![Project-1/Untitled%2037.png](Project-1/Untitled%2037.png)
    
7. ๊ฒ์ฌ๊ฐ ์๋ฃ๋์์ต๋๋ค. ํ์ง๋ง PR์์ฒญ์ ๋ฐ๋ฅธ ๊ฒ์ฌ์ด๊ธฐ ๋๋ฌธ์ ๋ฐฐํฌ๋ ์งํํ์ง ์์ต๋๋ค
    
    ![Project-1/Untitled%2038.png](Project-1/Untitled%2038.png)
    
8. github์ ํ์คํธ ์ฑ๊ณต ๊ฒฐ๊ณผ๊ฐ ์ ์์ ์ผ๋ก ๋ฆฌํด๋์์ต๋๋ค
    
    ![Project-1/Untitled%2039.png](Project-1/Untitled%2039.png)
    
9. ๊ทธ๋์ ์๋ฒ ์ ์ ๋ธ๋์น๋ฅผ ์ด์ฉํด์ฃผ์์ ๊ฐ์ฌํฉ๋๋ค
    
    ![Project-1/Untitled%2040.png](Project-1/Untitled%2040.png)
    
10. PR๋ด์ญ์ ๋ชจ๋ ๊นํ์ ๊ธฐ๋ก๋ฉ๋๋ค
    
    ![Project-1/Untitled%2041.png](Project-1/Untitled%2041.png)
    
11. Main Branch์ Merge ๋์๊ธฐ ๋๋ฌธ์ ๋ค์ ํธ๋ ๋น์ค๊ฐ ๋ฐ์ํฉ๋๋ค
    
    ![Project-1/Untitled%2042.png](Project-1/Untitled%2042.png)
    
12. Deploy๊ฐ ์์๋ฉ๋๋ค
    
    ![Project-1/Untitled%2043.png](Project-1/Untitled%2043.png)
    
13. AWS CodeDeploy ๋ฐฐํฌ ์ฑ๊ณต
    
    ![Project-1/Untitled%2044.png](Project-1/Untitled%2044.png)
    
14. ์น์๋ฒ๊ฐ RDS์ ์ฐ๊ฒฐํ์ฌ ์ ๋์ํฉ๋๋ค
    
    ![Project-1/Untitled%2045.png](Project-1/Untitled%2045.png)
    

## ์ ์ ์ปจํ์ธ  S3์ ๋ถ๋ฆฌํ๊ธฐ

1. ์ ์ ์ปจํ์ธ ๋ฅผ S3๋ก ๋ถ๋ฆฌํฉ๋๋ค
    
    ![Project-1/Untitled%2046.png](Project-1/Untitled%2046.png)
    
    ![Project-1/Untitled%2047.png](Project-1/Untitled%2047.png)
    
2. ๋น์ฐํ ๊ถํ์ ์ด์ด์ค์ผ ํฉ๋๋ค
    
    ![Project-1/Untitled%2048.png](Project-1/Untitled%2048.png)
    
3. ๋ฌธ์ ๋ CICD์ ์ํด ๋ค์ S3์ ์๋ก๋ํ๋ฉด ๊ถํ์ด ์ฌ๋ผ์ง๋๋ค
    
    ![Project-1/Untitled%2049.png](Project-1/Untitled%2049.png)
    
4. ๋ฐ๋ผ์ ์ ์ฑ์์ฑ๊ธฐ๋ก ์ด๋ ํ
    
    [AWS Policy Generator](http://awspolicygen.s3.amazonaws.com/policygen.html)
    
5. ๋ค์๊ณผ ๊ฐ์ด ์ ์ฑ์ ์์ฑํ๊ณ  ๋ณต์ฌํฉ๋๋ค
    
    ![Project-1/Untitled%2050.png](Project-1/Untitled%2050.png)
    
6. S3 ๋ฒํท์ ์ฑ์ ์์ ํฉ๋๋ค
    
    ![Project-1/Untitled%2051.png](Project-1/Untitled%2051.png)
    
7. ์๋ฌ๋ฅผ ์ ๋๊ฒ ๋ฟ์ด๋ด๋๋ฐ ๋ฒํท์ ์ฑ์์ resouce ๋ง์ง๋ง์ /*์ ๋ถ์ฌ์ค์ผ ํฉ๋๋ค
    
    ![Project-1/Untitled%2052.png](Project-1/Untitled%2052.png)
    
8. ์ด์  ์ธ๋ถ์์ ์ ๊ทผ์ด ์ ๋ฉ๋๋ค
    
    ![Project-1/Untitled%2053.png](Project-1/Untitled%2053.png)
    

## RDS ์ฐ๊ฒฐํ๊ธฐ

1. ํ๊ฒฝ๋ณ์๋ฅผ ์ด์ฉํด ํ๊ทธ๊ฐ์ ๊ฐ์ ธ์ค๊ธฐ ์ํด ๊ธฐ์กด EC2 ์ญํ ์ ๊ถํ์ ์ถ๊ฐํฉ๋๋ค
    
    ![Project-1/Untitled%2054.png](Project-1/Untitled%2054.png)
    
2. ๋ค์๊ณผ ๊ฐ์ด EC2 ์์ RDS์ ์ฐ๊ฒฐํ  ์ ์๋๋ก ์ค์ ์ ํด๋ก๋๋ค
        
    ```s
    mysql -u root -p --host myapp.cnr20hoyd3cu.ap-northeast-2.rds.amazonaws.com
    ```
    
    ![Project-1/Untitled%2055.png](Project-1/Untitled%2055.png)
    
3. ๋ค์๊ณผ ๊ฐ์ด ํ์ด๋ธ์ ๋ง๋ค์ด์ค๋๋ค
    
    ํฉ๊ฒฉ ๊ฒฐ๊ณผ๋ฅผ ๋์ด์ค result๋ ๊ธฐ๋ณธ ๊ฐ์ 0์ ๋ถ์ฌํฉ๋๋ค
    
    ```sql
    create table {RDS_TABLE} (number int auto_increment primary key, name char(10) not null ,contact text not null ,resume text, blog text, result BOOLEAN default 0)
    ```
    
4. ๋ค์๊ณผ ๊ฐ์ด ํ์คํธ ํด๋ด๋๋ค. ์ ์ฐ๊ฒฐ๋์์ต๋๋ค.
    
    ![Project-1/Untitled%2056.png](Project-1/Untitled%2056.png)
    
5. ๋ฑ๋ก์๋ฒ ์์ฑ
    
    ![Project-1/Untitled%2057.png](Project-1/Untitled%2057.png)
    
6. ๊ฒฐ๊ณผ์๋ฒ ์์ฑ
    
    ![Project-1/Untitled%2058.png](Project-1/Untitled%2058.png)
    

# Part 3 - Orchestration

---

## Swarm mode

1. ์ค์์ ์ํ ํฌํธ๋ฅผ ๊ฐ๋ฐฉํฉ๋๋ค
    - tcp 2377 - ํด๋ฌ์คํฐ ๋งค๋์ง๋จผํธ
    - tcp udp 7946 - ๋ธ๋๊ฐ ํต์ 
    - udp 4789 - ์ค๋ฒ๋ ์ด ๋คํธ์ํฌ
2. ๋ ์ค์ ๋ง์์ ๋๋๊ฑธ๋ก ์ฌ์ฉํ๋ฉด ๋ฉ๋๋ค
    
    ![Project-1/Untitled%2059.png](Project-1/Untitled%2059.png)
    
    ![Project-1/Untitled%2060.png](Project-1/Untitled%2060.png)
    
    ![Project-1/Untitled%2061.png](Project-1/Untitled%2061.png)
    
3. ๋งค๋์  ๋ธ๋๋ฅผ ์์ํฉ๋๋ค

    ```s
    docker swarm init --advertise-addr {ADDR}
    ```
        
    ![Project-1/Untitled%2062.png](Project-1/Untitled%2062.png)
    
4. ์์ปค ๋ธ๋๋ฅผ ์ถ๊ฐํฉ๋๋ค
    
    ![Project-1/Untitled%2063.png](Project-1/Untitled%2063.png)
    
    ![Project-1/Untitled%2064.png](Project-1/Untitled%2064.png)
    
    ![Project-1/Untitled%2065.png](Project-1/Untitled%2065.png)
    
5. ๋ค์๊ณผ ๊ฐ์ ๋ฐฉ์์ผ๋ก Nginx ์ปจํ์ด๋๋ฅผ ๋ก๋ํ๊ณ  ์ ๋ณด๋ฅผ ํ์ธํ  ์ ์์ต๋๋ค
    
    ```s
    docker service create --name nginx -p 80:80 nginx
    docker service ls
    docker service ps nginx
    ```
    
    ![Project-1/Untitled%2066.png](Project-1/Untitled%2066.png)
    
6. ์ด๋ค ์ธ์คํด์ค๋ก ์ ์ํ๋ ์๊ด์์ด Nginx ์ปจํ์ด๋์ ์ฐ๊ฒฐ๋ฉ๋๋ค
    
    ![Project-1/Untitled%2067.png](Project-1/Untitled%2067.png)
    
7. ๋์ปค ์ค์์ detached๋ฅผ ๊ธฐ๋ณธ ์ ์ ๋ก ๊น๊ณ  ๊ฐ๊ธฐ ๋๋ฌธ์ ๋ค์๊ณผ ๊ฐ์ด process๊ฐ ์ข๋ฃ๋๋ ์ปจํ์ด๋๋ฅผ ์คํํ๋ฉด ํด๋น ์ปจํ์ด๋๊ฐ ์๋ฌ๊ฐ ๋ฐ์ํ ๊ฒ์ผ๋ก ํ๋จํ์ฌ ๋ฌดํ ์ฌ์คํ ๋ฉ๋๋ค
    
    ![Project-1/Untitled%2068.png](Project-1/Untitled%2068.png)
    
8. 
9. ์ปจํ์ด๋ ํ๋์ฉ ๋ก๋ํ  ์ ์๋ ๊ฒฝ์ฐ ์คํ์ ์ด์ฉํฉ๋๋ค
    
    ![Project-1/Untitled%2069.png](Project-1/Untitled%2069.png)

    ```s
    docker stack deploy --compose-file docker-compose-swarm.yml test
    ```

10. ์๋น์ค๊ฐ ์ ์คํ๋๋ฉด RDS์ 2๊ฐ์ ์ฐ๊ฒฐ์ด ์์ฑ๋ ๊ฒ์ ํ์ธํ  ์ ์์ต๋๋ค
    
    ![Project-1/Untitled%2070.png](Project-1/Untitled%2070.png)
    
11. ์๋น์ค๊ฐ ์ ๋ก๋๋์์ต๋๋ค
    
    ![Project-1/Untitled%2071.png](Project-1/Untitled%2071.png)
    

## Links

---

- Docker Best Practices
    
    [Docker Security Best Practices from the Dockerfile](https://cloudberry.engineering/article/dockerfile-security-best-practices/)
    
- AWS ECS@beanstalk ๋ฉํฐ์ปจํ์ด๋ DOCS
    
    [๋ฉํฐ์ปจํ์ด๋ Docker ํ๋ซํผ(Amazon Linux AMI)](https://docs.aws.amazon.com/ko_kr/elasticbeanstalk/latest/dg/create_deploy_docker_ecs.html)
    
- EC2
    - User_data ****ํ๋์ฝ๋ฉ
        
        [Terraform by examples. Part 1](https://medium.com/@dhelios/terraform-by-examples-part-1-ef3e3be7b88b)
        
    - EC2 User_data YAML ์์ฑ๋ฒ
        
        [Cloud config examples - cloud-init 21.1 documentation](https://cloudinit.readthedocs.io/en/latest/topics/examples.html)
        
    - EC2์์ ํ๊ฒฝ๋ณ์๋ก ํ๊ทธ ๊ฐ์ ธ์ค๋ ๋ฐฉ๋ฒ
        
        [AWS EC2 Tags๋ฅผ ENV๋ก ์ฌ์ฉํ๊ธฐ](https://say8425.github.io/ec2-tags-env/)
        
- Nginx ์ค์ 
    - ๊ธฐ๋ณธ
        
        [NGINX ํ๊ฒฝ์ค์  - NGINX](https://opentutorials.org/module/384/4526)
        
    - Nginx ๋ก๊ทธ
        
        [](https://ktdsoss.tistory.com/410)
        
- Nginx์ ์ญํ 
    
    
    [Nginx ์ดํดํ๊ธฐ ๋ฐ ๊ธฐ๋ณธ ํ๊ฒฝ์ค์  ์ธํํ๊ธฐ](https://whatisthenext.tistory.com/123?category=779890)
    
    [NGINX ์๊ฐ - NGINX](https://opentutorials.org/module/384/3462)
    
- WSGI๋
    
    [WSGI์ ๋ํ ์ค๋ช, WSGI๋ ๋ฌด์์ธ๊ฐ?](https://paphopu.tistory.com/entry/WSGI%EC%97%90-%EB%8C%80%ED%95%9C-%EC%84%A4%EB%AA%85-WSGI%EB%9E%80-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80)
    
    [wsgi๋ฅผ ์ ์ฐ๋์](https://uiandwe.tistory.com/1268)
    
- Flask + uWSGI + Nginx
    - ์ฌ๋ก
        
        [[Python] Flask + uWSGI + Nginx๋ฅผ ์ฐ๊ฒฐ ๋ฐ ๋ฐฐํฌ](https://soyoung-new-challenge.tistory.com/118)
        
        [ํํ ํธํธ ์ฆ๊ธฐ๋ ๊ฐ๋ฐใ๋ณด์ ๋ธ๋ก๊ทธ ๊๊(แตแแต*) : ๋ค์ด๋ฒ ๋ธ๋ก๊ทธ](https://blog.naver.com/dsz08082/222255617542)
        
    - Docs
        
        [Nginx support - uWSGI 2.0 documentation](https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html)
        
    - uWSGI.ini ์ค๋ช
        
        [[uWSGI] iniํ์ผ์ ํตํด uWSGI ์คํํ๊ธฐ](https://twpower.github.io/43-run-uwsgi-by-using-ini-file)
        
- Flask + gunicorn + Nginx
    - uWSGI โ gunicorn์ผ๋ก ๋ณ๊ฒฝํ ์ฌ๋ก
        
        [python๊ฐ๋ฐ์ uwsgi๋ฅผ ๋ฒ๋ฆฌ๊ณ  gunicorn์ผ๋ก ๊ฐ์ํ๋ค.](https://elastic7327.medium.com/python%EA%B0%9C%EB%B0%9C%EC%9E%90-uwsgi%EB%A5%BC-%EB%B2%84%EB%A6%AC%EA%B3%A0-gunicorn%EC%9C%BC%EB%A1%9C-%EA%B0%88%EC%95%84%ED%83%80%EB%8B%A4-df1c95f220c5)
        
    - Docs
        
        [Full Example Configuration](https://www.nginx.com/resources/wiki/start/topics/examples/full/)
        
    - ์ฌ๋ก
        
        [Flask + Gunicorn + Nginx + Docker๋ฅผ ์ฌ์ฉํ์ฌ ML ๋ชจ๋ธ์ ๋ฐฐํฌํ๋ ๋ฐฉ๋ฒ](https://ichi.pro/ko/flask-gunicorn-nginx-dockerleul-sayonghayeo-ml-model-eul-baepohaneun-bangbeob-10664946283472)
        
- Python โ RDS
    
    [[AWS] RDS์ ์ฐ๊ฒฐ๋ MySQL ๊ณผ Python ์ฐ๋ํ๊ธฐ, MySQL ์์ ์ ์ฅํ๊ธฐ](https://0-sunny.tistory.com/45)
    
    [[AWS/RDS]RDS์ Python ์ฐ๊ฒฐํ๊ธฐ(4) - pymysql์ ์ฌ์ฉํด python์ผ๋ก DB ์ด์ํ๊ธฐ](https://leo-bb.tistory.com/26)
    
- Flask โ RDS
    - ์ฐ๊ฒฐ
        
        [AWS EC2์์ RDS ์ฐ๋ํ Flask ์ ์ฉ](https://seyeon-hello.tistory.com/4)
        
    - ๋ฐ์ดํฐ ์ ์ด
        
        [AWS RDS with MySQL using Flask](https://medium.com/aws-pocket/aws-rds-with-mysql-using-flask-f1c6d8cc7eff)
        
- ํ์ด์ฌ ํ์คํธ์ฝ๋ ๊ธฐ๋ณธ ์์
    
    [Travis-ci๋ฅผ ์ด์ฉํ์ฌ python 'Hello world' ์์ฑํ๊ธฐ](https://cjh5414.github.io/travis-ci/)
    
- MySQL my.cnf ์์ฑ๋ฒ
    
    [make my.cnf](https://good-dba.gitbooks.io/mariadb-installation/content/make_mycnf.html)
    
    [MySQL ์ค์ ํ์ผ my.cnf](https://zetawiki.com/wiki/MySQL_%EC%84%A4%EC%A0%95%ED%8C%8C%EC%9D%BC_my.cnf)
    
- AWS Elastic Beanstalk
    - Beanstalkํ๊ฒฝ์์ Docker ์ปจํ์ด๋ ์ ์ ๋ฐฉ๋ฒ
        
        [Docker ๊ตฌ์ฑ](https://docs.aws.amazon.com/ko_kr/elasticbeanstalk/latest/dg/single-container-docker-configuration.html#docker-configuration.no-compose)
        
    - Beanstalk ์์์ ์ ๊ณต์ ์์ฑ ๊ฐ์ด๋
        
        [๋ฉํฐ์ปจํ์ด๋ Docker ๊ตฌ์ฑ](https://docs.aws.amazon.com/ko_kr/elasticbeanstalk/latest/dg/create_deploy_docker_v2config.html)
        
- Terraform
    - Beanstalk Docs
        
        [](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/elastic_beanstalk_application)
        
    - EC2์ ํ๊ฒฝ๋ณ์ ๋ฃ๋ ๋ฒ
        
        [Set environment variables in an AWS instance](https://stackoverflow.com/questions/50668315/set-environment-variables-in-an-aws-instance)
        
    - VPC Docs
        
        [](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc)
        
- Travis CI
    - CodeDeploy Docs
        
        [Travis CI Documentation](https://docs.travis-ci.com/user/deployment/codedeploy/)
        
- Docker Swarm Docs
    - Docker official
        
        [Getting started with swarm mode](https://docs.docker.com/engine/swarm/swarm-tutorial/#open-protocols-and-ports-between-the-hosts)
        
    - Stack ์ฌ์ฉ๋ฒ
        
        [Deploy a stack to a swarm](https://docs.docker.com/engine/swarm/stack-deploy/)
        
    - Terraform Module
        
        [](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/2.3.0/submodules/docker-swarm)
        
    - ์ค๋ฒ๋ ์ด ๋คํธ์ํฌ์์ ์ปจํ์ด๋ ์ฐพ๊ธฐ
        
        [How to use Docker swarm DNS/Service names in Nginx upstream](https://stackoverflow.com/questions/43896846/how-to-use-docker-swarm-dns-service-names-in-nginx-upstream)
        
    - ์ค์๋ชจ๋๋ฅผ ์ํ ์คํ ์์ฑ
        
        [๋์ปค ์์ํ๊ธฐ 11 : ๋์ปค ์ค์ - ๋คํธ์ํฌ](https://javacan.tistory.com/entry/docker-start-11-swarm-network)
        
    - ์๋น์ค ์์ ์๋ฌ
        
        [Troubleshooting swarm service create](https://forums.docker.com/t/troubleshooting-swarm-service-create/55161)
        
    - ๋ฐํ์ฉ ppt
        
        [๊ฐ์ธํ์ .pptx](Project-1.pptx)
        
