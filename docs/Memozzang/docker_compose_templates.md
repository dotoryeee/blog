# Docker compose 모음

1. Nextcloud
  
    ```yaml title="docker-compose.yml"
    version: '2'
    volumes:
      nextcloud-app-volume:
      nextcloud-db-volume:
    networks:
      nextcloud-network:
        driver: bridge
    services:
      nextcloud-mariadb:
        image: mariadb
        command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
        restart: always
        ports:
          - 3306:3306
        volumes:
          - nextcloud-db-volume:/var/lib/mysql
        environment:
          - MYSQL_ROOT_PASSWORD=
          - MYSQL_PASSWORD=
          - MYSQL_DATABASE=
          - MYSQL_USER=
        networks:
          - nextcloud-network
      nextcloud-app:
        image: nextcloud
        ports:
          - 8080:80
        links:
          - nextcloud-mariadb
        volumes:
          - nextcloud-app-volume:/var/www/html
        restart: always
        networks:
          - nextcloud-network
    ```

2. Jupyter Lab 3

    ```dockerfile title="Dockerfile"
    FROM jupyter/datascience-notebook:latest
    # Declare root as user
    USER root
    # Update Ubuntu
    RUN sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && sed -i 's/security.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list
    # Install Nanum for Korean Font
    RUN apt-get update && apt-get -y upgrade && apt-get install -y fonts-nanum && fc-cache -fv && rm -fr ~/.cache/matplotlib
    ```

    ```yaml title="docker-compose.yml"
    version: '3'
    services:
        jupyter-notebook:
          build:
            context: .
            dockerfile: ./Dockerfile
          user: root
          environment:
            - GRANT_SUDO=1
            - JUPYTER_ENABLE_LAB=yes
            - JUPYTER_TOKEN=papapassword
          volumes:
            - /home/ubuntu/ds/data:/home/jovyan/data
          ports:
            - "8888:8888"
          container_name: "jupyter-notebook"
          restart: always
    ```
3. Selenium crawler
    ```s
    mkdir ~/app
    cat<<EOF >~/app/requirements.txt
    selenium==4.9.1
    jinja2
    boto3
    webdriver-manager
    EOF
    ```

    ```dockerfile title="Dockerfile"
    FROM python:3.11

    RUN sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
        sed -i 's/security.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
        echo "deb [trusted=yes] http://archive.ubuntu.com/ubuntu bionic main restricted universe multiverse" >> /etc/apt/sources.list && \
        echo "deb [trusted=yes] http://archive.ubuntu.com/ubuntu bionic-security main restricted universe multiverse" >> /etc/apt/sources.list && \
        echo "deb [trusted=yes] http://archive.ubuntu.com/ubuntu bionic-updates main restricted universe multiverse" >> /etc/apt/sources.list

    RUN mkdir -p /app/temp && \
        cd /app && \
        apt-get update --allow-unauthenticated; apt-get install wget language-pack-ko fonts-nanum fonts-nanum-extra -y && \
        locale-gen ko_KR.UTF-8 && \
        fc-cache -fv && \
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O ./temp/google_chrome.deb && \
        apt-get install -f /app/temp/google_chrome.deb -y && \
        apt-get auto-clean; rm -rf /var/lib/apt/lists/* && \
        rm -rf /app/temp && \
        pip install --upgrade pip

    COPY requirements.txt /app

    RUN pip install -r /app/requirements.txt --no-cache-dir

    WORKDIR /app

    ENV DISPLAY=:99

    CMD [ "python", "/app/app.py" ]
    ```

    ```py title="app.py"
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    options = webdriver.ChromeOptions()
    options.add_argument("--display-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"]) #for hide selenium INFO log (eg. DevTools listening ## port)
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("window-size=1200x2100")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)

    ```
 
4. ubuntu기반 oracleDB 21용 sqlplus Dockerfile 생성
    ```dockerfile title="Dockerfile"
    FROM ubuntu:22.04
    RUN apt update; apt install wget alien libaio1 -y
    RUN wget https://download.oracle.com/otn_software/linux/instantclient/219000/oracle-instantclient-basic-21.9.0.0.0-1.el8.x86_64.rpm
    RUN wget https://download.oracle.com/otn_software/linux/instantclient/219000/oracle-instantclient-sqlplus-21.9.0.0.0-1.el8.x86_64.rpm
    RUN wget https://download.oracle.com/otn_software/linux/instantclient/219000/oracle-instantclient-devel-21.9.0.0.0-1.el8.x86_64.rpm
    RUN alien -i oracle-instantclient-basic-21.9.0.0.0-1.el8.x86_64.rpm
    RUN alien -i oracle-instantclient-sqlplus-21.9.0.0.0-1.el8.x86_64.rpm
    RUN alien -i oracle-instantclient-devel-21.9.0.0.0-1.el8.x86_64.rpm
    RUN sh -c "echo /usr/lib/oracle/21/client64/lib > /etc/ld.so.conf.d/oracle.conf"
    RUN ldconfig
    RUN rm -rf *rpm
    CMD ["sqlplus"]

    ```
