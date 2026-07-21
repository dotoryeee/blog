---
draft: false
date: 2026-07-21
authors:
  - dotoryeee
categories:
  - Security
tags:
  - Vault
  - PostgreSQL
  - Dynamic Secrets
description: "Vault와 PostgreSQL을 docker compose로 세워 database 엔진으로 TTL 2분짜리 동적 DB 계정을 발급하고 만료와 lease revoke로 자동 회수되는지 psql로 실측한 기록"
hide:
  - toc
---

# Vault 동적 시크릿 실습

<!-- more -->

## 목표

---

- Vault의 database secrets engine으로 DB 계정이 요청 시점에 발급되고 TTL이 지나면 자동으로 사라지는 과정을 로컬에서 실측한다
- docker compose로 Vault(dev 모드)와 PostgreSQL을 띄우고, dotoryeee-app role에서 TTL 2분짜리 계정을 발급받아 그 계정으로 실제 psql 접속까지 확인한다
- TTL 만료와 lease revoke 두 경로로 계정이 회수되는지 postgres 쪽 role 목록으로 교차 검증한다

동적 시크릿의 개념과 Vault 구성요소(secret engine, auth method, policy, lease), 쿠버네티스 연동 방식은 [시크릿 관리 정리](secret_management.md)에서 다뤘다. 이 글은 그 위에서 database 엔진을 실제로 붙이고, 요청 한 번에 계정이 생겼다가 시간이 지나면 저절로 없어지는 것을 눈으로 확인하는 데 집중한다.

## 실습 구성

---

컨테이너 두 개를 한 compose 네트워크에 올린다. Vault는 database 엔진으로 postgres에 관리자 자격으로 붙어 있다가, 클라이언트가 자격증명을 요청하면 그 순간 임시 role을 만들어 돌려준다. 흐름은 다음과 같다.

```mermaid
graph LR
    App["psql 클라이언트<br>(발급받은 임시 계정)"] -->|"1. creds 요청"| Vault["dotoryeee-vault<br>(database engine)"]
    Vault -->|"2. CREATE ROLE (TTL 2분)"| PG["dotoryeee-postgres<br>(dotoryeee_shop)"]
    Vault -->|"3. 임시 계정+암호 반환"| App
    App -->|"4. TTL 동안 접속·조회"| PG
    Vault -.->|"5. TTL 만료시 DROP ROLE"| PG
```

- dotoryeee-vault: dev 모드로 뜨는 Vault 서버. 8200에서 API와 UI를 연다
- dotoryeee-postgres: 동적 계정을 발급받을 대상 DB. dotoryeee_shop 데이터베이스와 관리자 계정 dotoryeee를 갖는다

이미지는 hashicorp/vault:1.18, postgres:16으로 고정한다. Vault는 dev 모드라 기동과 동시에 자동으로 unseal되고 루트 토큰이 발급되지만, 데이터는 메모리에만 남는다.

!!! warning
    💡 dev 모드 종료 시 엔진 설정과 시크릿이 모두 사라지므로 실습·데모용으로만 쓴다

먼저 compose 파일을 작성한다. 컨테이너 이름과 데모 크리덴셜에 dotoryeee를 넣어 UI와 발급 계정에서 자주 노출되게 한다.

```s
vi docker-compose.yml
```

```yaml title="docker-compose.yml"
services:
  dotoryeee-vault:                       #Vault 서버 (dev 모드, 데이터는 메모리에만)
    image: hashicorp/vault:1.18
    container_name: dotoryeee-vault
    cap_add:
      - IPC_LOCK                          #메모리 잠금(mlock) 권한. dev는 필수 아니지만 운영 구성과 맞춰 둠
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: dotoryeee-root      #dev 모드 루트 토큰을 고정값으로 지정
      VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200       #컨테이너 밖에서도 접근 가능하게 바인딩
      VAULT_ADDR: http://127.0.0.1:8200            #컨테이너 안 CLI가 바라볼 주소
    command: server -dev                  #dev 모드로 기동 (자동 unseal, 루트 토큰 발급)
    ports:
      - "8200:8200"                       #UI와 API를 호스트 8200으로 노출

  dotoryeee-postgres:                     #동적 계정을 발급받을 대상 DB
    image: postgres:16
    container_name: dotoryeee-postgres
    environment:
      POSTGRES_DB: dotoryeee_shop         #실습용 데이터베이스명
      POSTGRES_USER: dotoryeee            #Vault가 관리자로 붙을 계정 (superuser)
      POSTGRES_PASSWORD: dotoryeee-pass   #관리자 계정 비밀번호 (데모 값)
    ports:
      - "15432:5432"                      #호스트 15432 -> 컨테이너 5432 (기본 포트 충돌 회피)

networks:
  default:
    name: dotoryeee-net                   #두 컨테이너를 한 네트워크에 묶어 이름으로 통신
```

이제 스택을 올리고 두 컨테이너가 모두 Up인지 확인한다.

```s
docker compose up -d
docker compose ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}'
NAME                 STATUS         PORTS
dotoryeee-postgres   Up 8 seconds   0.0.0.0:15432->5432/tcp, [::]:15432->5432/tcp
dotoryeee-vault      Up 8 seconds   0.0.0.0:8200->8200/tcp, [::]:8200->8200/tcp
```

Vault가 dev 모드로 열려 봉인이 풀린 상태인지 본다. Sealed가 false, Storage Type이 inmem이면 실습을 진행할 수 있다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault status
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.18.5
Storage Type    inmem
HA Enabled      false
```

이후 vault 명령은 컨테이너 안에서 실행하고, 루트 토큰은 VAULT_TOKEN 환경변수로 넘긴다.

## database secrets engine 설정

---

database 엔진을 활성화한다. 활성화하면 database/ 경로가 생기고, secrets list에서 확인할 수 있다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault secrets enable database
Success! Enabled the database secrets engine at: database/
```

이어서 Vault가 postgres에 붙을 연결을 설정한다. connection_url의 username, password 자리는 이중 중괄호 템플릿으로 두고, 실제 관리자 계정과 암호는 뒤에 따로 넘긴다. allowed_roles로 이 연결을 쓸 수 있는 role을 dotoryeee-app 하나로 제한한다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault write database/config/dotoryeee-postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="dotoryeee-app" \
  connection_url="postgresql://{{username}}:{{password}}@dotoryeee-postgres:5432/dotoryeee_shop?sslmode=disable" \
  username="dotoryeee" \
  password="dotoryeee-pass"
Success! Data written to: database/config/dotoryeee-postgres
```

connection_url의 host를 dotoryeee-postgres로 적으면 compose 네트워크가 컨테이너 이름을 DNS로 풀어준다. Vault는 컨테이너 안에서 5432로 붙으므로 호스트 매핑 포트 15432가 아니라 내부 포트 5432를 쓴다.

동적 계정이 읽을 데모 테이블을 관리자 계정으로 하나 만든다. 이 테이블이 있어야 뒤에서 발급 계정에 준 SELECT 권한이 확인할 대상이 생긴다.

```s
docker exec -e PGPASSWORD=dotoryeee-pass dotoryeee-postgres \
  psql -U dotoryeee -d dotoryeee_shop -c \
  "CREATE TABLE products (id serial PRIMARY KEY, name text, price int);
   INSERT INTO products (name, price) VALUES ('dotoryeee-mug', 12000), ('dotoryeee-tshirt', 24000);"
CREATE TABLE
INSERT 0 2
```

## role 만들기

---

role은 "자격증명을 요청받으면 postgres에서 무슨 SQL을 실행할지"를 정의한다. creation_statements에 계정 생성과 권한 부여를, revocation_statements에 회수 SQL을 적는다. default_ttl을 2분으로 짧게 줘서 만료를 금방 확인할 수 있게 하고, max_ttl은 10분으로 둔다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault write database/roles/dotoryeee-app \
  db_name=dotoryeee-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  revocation_statements="REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM \"{{name}}\"; DROP ROLE IF EXISTS \"{{name}}\";" \
  default_ttl="2m" \
  max_ttl="10m"
Success! Data written to: database/roles/dotoryeee-app
```

회수문에 REVOKE를 먼저 넣은 데는 이유가 있다. 생성문에서 계정에 SELECT를 부여했기 때문에, 권한을 그대로 둔 채 DROP ROLE만 하면 postgres가 "dependent 객체가 있다"며 삭제를 거부한다. 그래서 권한을 먼저 회수하고 role을 지운다.

!!! warning
    💡 권한을 부여한 role은 DROP ROLE만으로 삭제되지 않으므로 권한 회수를 앞에 둔다

role 설정이 들어간 것을 read로 확인한다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault read database/roles/dotoryeee-app
Key                      Value
---                      -----
creation_statements      [CREATE ROLE "{{name}}" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{{name}}";]
credential_type          password
db_name                  dotoryeee-postgres
default_ttl              2m
max_ttl                  10m
revocation_statements    [REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM "{{name}}"; DROP ROLE IF EXISTS "{{name}}";]
```

여기까지의 설정은 Vault UI에서도 그대로 보인다. 8200에 루트 토큰으로 로그인한다. Method는 Token, Token 칸에 dotoryeee-root를 넣는다.

![Vault UI 로그인 화면](vault_lab/1.PNG)

로그인하면 방금 활성화한 database 엔진과, 뒤에서 쓸 dotoryeee-kv 엔진이 목록에 보인다.

![Secrets Engines 목록](vault_lab/2.PNG)

database 엔진의 dotoryeee-app role 상세에는 TTL과 최대 TTL, 그리고 생성문·회수문이 그대로 노출된다.

![dotoryeee-app role 상세](vault_lab/3.PNG)

## 동적 계정 발급과 접속

---

이제 자격증명을 요청한다. database/creds/dotoryeee-app 경로를 읽는 순간 Vault가 postgres에 CREATE ROLE을 실행하고, 방금 만든 계정과 암호를 lease와 함께 돌려준다. username은 v-token-으로 시작하고, lease_duration이 2분이다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault read database/creds/dotoryeee-app
Key                Value
---                -----
lease_id           database/creds/dotoryeee-app/JeCKhSTOoj7seFbnrMKQbOZo
lease_duration     2m
lease_renewable    true
password           NVP4LMGsS2paQIDQ-GZd
username           v-token-dotoryee-Ffw1g2fR1w4DCGkiw7u3-1784643060
```

발급받은 계정으로 곧바로 접속해 본다. current_user가 발급받은 v-token 계정이고, 데모 테이블도 읽힌다. 접속과 SELECT가 모두 되는 것을 확인할 수 있다.

```s
docker exec -e PGPASSWORD='NVP4LMGsS2paQIDQ-GZd' dotoryeee-postgres \
  psql -h 127.0.0.1 -U 'v-token-dotoryee-Ffw1g2fR1w4DCGkiw7u3-1784643060' -d dotoryeee_shop \
  -c 'SELECT current_user;' -c 'SELECT * FROM products;'
                   current_user
--------------------------------------------------
 v-token-dotoryee-Ffw1g2fR1w4DCGkiw7u3-1784643060
(1 row)

 id |       name       | price
----+------------------+-------
  1 | dotoryeee-mug    | 12000
  2 | dotoryeee-tshirt | 24000
(2 rows)
```

이 계정이 Vault의 상상 속에만 있는 게 아니라 postgres에 실제로 만들어졌는지 관리자 계정으로 role 목록을 본다. v-token으로 시작하는 role이 하나 잡히고, 생성문의 VALID UNTIL 때문에 만료 시각까지 붙어 있다.

```s
docker exec -e PGPASSWORD=dotoryeee-pass dotoryeee-postgres psql -U dotoryeee -d dotoryeee_shop -c "\du v-token*"
                                         List of roles
                    Role name                     |                 Attributes
--------------------------------------------------+---------------------------------------------
 v-token-dotoryee-Ffw1g2fR1w4DCGkiw7u3-1784643060 | Password valid until 2026-07-21 14:13:05+00
```

UI의 Generate credentials로도 같은 발급이 된다. 발급 결과 화면에는 username, password와 함께 lease ID, lease 지속시간(초)이 표시된다.

![Generate credentials 결과 화면](vault_lab/4.PNG)

## TTL 만료 검증

---

default_ttl이 2분이므로, 발급 뒤 그대로 두면 Vault의 lease 만료가 회수문을 실행해 계정을 지운다. 2분 남짓 기다린 뒤 다시 role 목록을 본다. 방금 있던 v-token 계정이 사라졌다.

```s
docker exec -e PGPASSWORD=dotoryeee-pass dotoryeee-postgres psql -U dotoryeee -d dotoryeee_shop -c "\du v-token*"
     List of roles
 Role name | Attributes
-----------+------------

docker exec -e PGPASSWORD=dotoryeee-pass dotoryeee-postgres psql -U dotoryeee -d dotoryeee_shop \
  -tc "SELECT count(*) FROM pg_roles WHERE rolname LIKE 'v-token%';"
     0
```

한 발 더 나아가, 만료된 계정으로 다시 접속을 시도하면 그 role 자체가 없다는 에러가 난다. 계정이 정말로 삭제됐다는 확증이다.

```s
docker exec -e PGPASSWORD='NVP4LMGsS2paQIDQ-GZd' dotoryeee-postgres \
  psql -h 127.0.0.1 -U 'v-token-dotoryee-Ffw1g2fR1w4DCGkiw7u3-1784643060' -d dotoryeee_shop -c 'SELECT 1;'
psql: error: connection to server at "127.0.0.1", port 5432 failed: FATAL:  role "v-token-dotoryee-Ffw1g2fR1w4DCGkiw7u3-1784643060" does not exist
```

고정 비밀번호를 쓰는 계정이라면 유출된 값이 계속 유효하지만, 동적 계정은 TTL이 지나면 자격증명뿐 아니라 계정 자체가 없어진다. 회전을 사람이 챙길 필요가 사라진다.

## 즉시 회수 (lease revoke)

---

TTL을 기다리지 않고 곧바로 회수해야 할 때도 있다. 유출이 의심되면 해당 lease만 revoke한다. 새 계정을 하나 발급받아 lease ID를 확인한다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault read database/creds/dotoryeee-app
Key                Value
---                -----
lease_id           database/creds/dotoryeee-app/dheb0stEDEZ3Ox5flxDb6sKp
lease_duration     2m
lease_renewable    true
password           z2jc3fSfnEezGFh9-sC7
username           v-token-dotoryee-X7WDrQdWa4WYXjD9Ao4r-1784643242
```

이 lease를 revoke하면 Vault가 즉시 회수문을 큐에 넣어 실행한다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault lease revoke database/creds/dotoryeee-app/dheb0stEDEZ3Ox5flxDb6sKp
All revocation operations queued successfully!
```

TTL이 한참 남았는데도 role 목록은 이미 비어 있다. 만료를 기다리지 않고 계정이 바로 사라졌다.

```s
docker exec -e PGPASSWORD=dotoryeee-pass dotoryeee-postgres psql -U dotoryeee -d dotoryeee_shop \
  -tc "SELECT count(*) FROM pg_roles WHERE rolname LIKE 'v-token%';"
     0
```

유출 사고가 났을 때 전체 비밀번호를 바꾸는 대신, 문제가 된 lease 하나만 revoke하면 그 계정만 무효가 된다. 감사 로그에 누가 언제 무슨 계정을 받아 갔는지가 남으므로 추적 범위도 계정 단위로 좁혀진다.

## 정적 시크릿과의 대비 (KV v2)

---

동적 시크릿과 비교되는 쪽이 정적 시크릿이다. KV v2 엔진은 넣어 둔 값을 그대로 저장했다가 요청하면 돌려준다. 발급도 회전도 만료도 없다. dotoryeee-kv 경로에 엔진을 하나 열고 데모 API 키를 넣는다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault secrets enable -path=dotoryeee-kv kv-v2
Success! Enabled the kv-v2 secrets engine at: dotoryeee-kv/

docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault kv put dotoryeee-kv/api-keys \
  openai_key=sk-dotoryeee-1234 \
  db_password=dotoryeee-static-pw
======= Secret Path =======
dotoryeee-kv/data/api-keys

======= Metadata =======
Key                Value
---                -----
created_time       2026-07-21T14:11:13.072403882Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1
```

넣은 값은 언제 읽어도 똑같이 나온다. 특정 필드만 뽑을 수도 있다.

```s
docker exec -e VAULT_TOKEN=dotoryeee-root dotoryeee-vault vault kv get -field=openai_key dotoryeee-kv/api-keys
sk-dotoryeee-1234
```

UI의 Secret 탭에서도 같은 값이 그대로 보인다.

![KV v2 정적 시크릿](vault_lab/5.PNG)

정적 시크릿은 값을 보관하는 창고에 가깝다. 회전과 폐기를 사람이 챙겨야 한다. 반대로 동적 시크릿은 쓸 때마다 새 계정을 찍어 내고 만료되면 회수한다. 같은 Vault 안에서 두 방식이 서로 다른 자리를 맡는다.

## 정리

---

실습이 끝나면 컨테이너와 네트워크, 볼륨을 함께 내린다. dev 모드라 여기 넣은 엔진 설정과 시크릿은 모두 이 시점에 사라진다.

```s
docker compose down -v
```

- 동적 시크릿의 실체는 요청 시 CREATE ROLE에 TTL을 걸고, 만료 시 REVOKE 후 DROP ROLE을 실행하는 SQL 두 줄이었다
- TTL을 2분으로 두고 기다렸더니 postgres의 v-token 계정이 저절로 사라졌고, 그 계정으로는 더 이상 접속되지 않았다
- 급할 땐 lease revoke로 만료를 기다리지 않고 계정 하나만 즉시 회수했다. 정적 KV 값이 그대로 남아 있는 것과 대비된다
