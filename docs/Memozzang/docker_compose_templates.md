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
    RUN apt-get update && apt-get -y upgrade && apt-get install -y fonts-nanum* && fc-cache -fv && rm -fr ~/.cache/matplotlib
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
            - GRANT_SUDO=yes
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
    requests
    selenium
    EOF
    ```

    ```dockerfile title="Dockerfile"
    FROM python:latest
    RUN mkdir -p app/temp
    WORKDIR app
    RUN apt update -y; apt install wget unzip -y
    RUN wget http://dl.google.com/linux/deb/pool/main/g/google-chrome-unstable/google-chrome-unstable_112.0.5615.20-1_amd64.deb -O ./temp/google_chrome.deb
    RUN apt install -f ./temp/google_chrome.deb -y
    RUN wget https://chromedriver.storage.googleapis.com/112.0.5615.28/chromedriver_linux64.zip -P ./temp
    RUN unzip ./temp/chromedriver_linux64.zip -d ./
    RUN rm -rf ./temp
    RUN pip install --upgrade pip
    COPY app/requirements.txt ./
    RUN pip install -r requirements.txt --no-cache-dir
    CMD [ "python", "/app/app.py" ]
    ```
4. 