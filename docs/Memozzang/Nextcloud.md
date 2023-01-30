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
      - MYSQL_ROOT_PASSWORD=rororoot
      - MYSQL_PASSWORD=dbpassword1234
      - MYSQL_DATABASE=dbdbdb
      - MYSQL_USER=usususer
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