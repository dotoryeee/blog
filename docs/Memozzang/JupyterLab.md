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
