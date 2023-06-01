#!/bin/bash
# install nginx
sudo apt update && sudo apt install nginx -y
sudo wget https://kr2-api-object-storage.nhncloudservice.com/v1/AUTH_cca4d757fedb477a91cc757b336ce430/garden_public/nginx.conf -O /etc/nginx/nginx.conf
sudo nginx -s reload
echo '<h1>This page created for Log & Crash service test</h1>' | sudo tee /var/www/html/index.html
# install logstash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
sudo apt-get update && sudo apt-get install logstash
sudo usermod -aG adm logstash
sudo wget https://kr2-api-object-storage.nhncloudservice.com/v1/AUTH_cca4d757fedb477a91cc757b336ce430/garden_public/nhn-log-crash.conf -O /etc/logstash/conf.d/nhn-log-crash.conf
sudo systemctl enable logstash; sudo systemctl restart logstash

