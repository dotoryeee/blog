---
draft: true
date: 2023-10-29
authors:
  - dotoryeee
categories:
  - study
  - Kubernetes
  - Database
  - Cloudnet@
---
# Database on Kubernetes study / Week 2
---
## 목차
1. Kubernetes operator
2. MySQL 8.0과 InnoDB Cluster
3. MySQL Operator for Kubernetes 개념
4. MySQL Operator for Kubernetes 배포
5. 테스트를 위한 Wordpress 배포
6. 장애 테스트
7. Scaling 테스트
8. MySQL 백업 및 복구

<!-- more -->

---
## 실습
1. Kubernetes Operator
    1. Kubernetes(이하 k8s)의 operator는 3가지 요소로 구성되어 있다.
    2. CRD: Custom Resource Definition<br> operator를 사용하기 위해 먼저 k8s API를 확장하여 새로운 리소스 유형을 정의하는 CRD는 YAML형식의 파일로 새로운 Object의 Scheme를 정의한다.
    3. CR: Custom Resource<br> 앞서 정의한 CRD를 기반으로 생성할 수 있는 custom object로, 어플리케이션 상태, 구성, metadata를 저장하는데 사용한다. 당연히 YAML이다.
    4. Operator Controller<br> Operator의 로직을 담고 있는 컴포넌트이고, k8s api server와 직접 통신하여 CR의 상태를 감지하다가 생성, 업데이트, 삭제 등 실제 작업을 수행한다.
2. MySQL 8.0과 InnoDB Cluster
    1. MySQL구성은 Primary-Secondary구조와 Cluster구조를 사용할 수 있다. P-S구조의 경우 읽기에 대한 scale out만 지원하지만, Cluster구조의 경우 읽기와 쓰기 모두 scale out할 수 있다.
    2. MySQL Primary Secondary replication
        1. Primary: 모든 쓰기(INSERT, UPDATE, DELETE) 작업을 처리하고, 데이터 변경이 발생하면 변경사항을 바이너리 로그에 기록한다.
        2. Secondary: Primary 서버에서 발생한 변경사항을 복제하여 동기화하며, 읽기전용 복제본을 제공함으로써 읽기 작업에 대한 부하를 분산시켜준다.
        3. replication: Primary의 바이너리 로그에서 변경사항을 읽고 Secondary 이를 재실행하여 데이터를 동기화한다.
    3. MySQL Cluster(NDB cluster)
        ![NDB-Cluster](./doik2/ndb-cluster.png)<br> 출처: https://dev.mysql.com/doc/refman/8.0/en/mysql-cluster-overview.html
        1. Data Node: 실제 데이터를 저장하며, 여러 대의 Data Node가 분산되어 있어 고가용성과 확장성을 제공합니다.
        2. SQL Node: 클라이언트의 SQL 요청을 처리하며, 데이터를 Data Node에서 읽고 씁니다.
        3. Management Node: 클러스터의 구성과 상태를 관리하며, Data Node와 SQL Node의 연결을 조정합니다.
3. MySQL Operator for Kubernetes 개념
    ![](./doik2/mysql-operator-architecture.jpg)<br>MySQL with k8s operator (cluster)기본 구조 / 출처: [링크](https://ronekins.com/2021/08/31/getting-started-with-the-oracle-mysql-kubernetes-operator-and-portworx/)
    ![](./doik2/mysql-operator-architecture-2.png)<br>MySQL with k8s operator (Primary-Secondary)상세 구조 / 출처: [링크](https://dev.mysql.com/doc/mysql-operator/en/mysql-operator-introduction.html)
    1. 
4. MySQL Operator for Kubernetes 배포
5. 테스트를 위한 Wordpress 배포
6.  장애 테스트
7.  Scaling 테스트
8.  MySQL 백업 및 복구